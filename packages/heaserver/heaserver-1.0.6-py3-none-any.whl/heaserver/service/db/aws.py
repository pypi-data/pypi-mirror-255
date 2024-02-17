from abc import ABC
from functools import partial
from aiohttp.web import Request
import boto3
from aiohttp import hdrs, web
from botocore.exceptions import ClientError
from mypy_boto3_s3 import S3Client, S3ServiceResource
from mypy_boto3_sts import STSClient
from mypy_boto3_account import AccountClient
from mypy_boto3_organizations import OrganizationsClient

from ..appproperty import HEA_DB
from .database import DatabaseContextManager, Database, MicroserviceDatabaseManager, get_credentials_from_volume
from .mongo import Mongo
from ..oidcclaimhdrs import SUB
from ..sources import AWS as AWS_SOURCE

from heaobject.account import AWSAccount
from heaobject.keychain import AWSCredentials, Credentials
from heaobject.registry import Property
from heaobject.volume import AWSFileSystem
from heaobject.user import NONE_USER
from heaobject.person import Role, encode_role
from ..heaobjectsupport import type_to_resource_url
from .. import client
from yarl import URL
from typing import Optional, Any, TypeVar, cast, overload, Literal
from configparser import ConfigParser
import asyncio
from threading import Lock
from contextlib import closing
from collections.abc import Callable, Sequence, AsyncGenerator
import logging

_boto3_client_lock = Lock()
_boto3_resource_lock = Lock()


class AWS(Database, ABC):
    """
    Connectivity to Amazon Web Services (AWS) for HEA microservices. Subclasses must call this constructor.
    """
    pass


class S3(AWS):
    """
    Connectivity to AWS Simple Storage Service (S3) for HEA microservices.
    """
    # this is the buffer we give to refresh credentials in minutes on our end before they expire on aws
    EXPIRATION_LIMIT = 540
    MAX_DURATION_SECONDS = 43200

    _S3Service = TypeVar('_S3Service')

    @property
    def file_system_type(self) -> type[AWSFileSystem]:
        return AWSFileSystem

    async def update_credentials(self, request: Request, credentials: AWSCredentials) -> None:
        """
        This is a wrapper function to be extended by tests
        It obtains credential's url from the registry and that makes PUT

        :param request:
        :param credentials:
        :returns: None if it succeeds otherwise it will raise ValueError or HTTPError
        :raises ValueError: if there was a problem accessing the registry service or the credentials service was not
        found.
        """
        if credentials.id is None:
            raise ValueError(f'credentials must have a non-None id attribute')
        resource_url = await type_to_resource_url(request, Credentials)
        await client.put(app=request.app, url=URL(resource_url) / credentials.id, data=credentials,
                         headers=request.headers)

    async def get_property(self, app: web.Application, name: str) -> Optional[Property]:
        """
        This is a wrapper function to be extended by tests
        Gets the Property with the given name from the HEA registry service.

        :param app: the aiohttp app.
        :param name: the property's name.
        :return: a Property instance or None (if not found).
        """
        return await client.get_property(app=app, name=name)

    @overload
    async def get_client(self, request: Request, service_name: Literal['s3'], volume_id: str) -> S3Client:
        ...

    @overload
    async def get_client(self, request: Request, service_name: Literal['sts'], volume_id: str) -> STSClient:
        ...

    @overload
    async def get_client(self, request: Request, service_name: Literal['account'], volume_id: str) -> AccountClient:
        ...

    @overload
    async def get_client(self, request: Request, service_name: Literal['organizations'],
                         volume_id: str) -> OrganizationsClient:
        ...

    async def get_client(self, request: Request, service_name: str,
                         volume_id: str) -> S3Client | STSClient | AccountClient | OrganizationsClient:
        """
        Gets an AWS service client.  If the volume has no credentials, it uses the boto3 library to try and find them.
        This method is not designed to be overridden.

        :param request: the HTTP request (required).
        :param service_name: AWS service name (required).
        :param volume_id: the id string of a volume (required).
        :return: a Mongo client for the file system specified by the volume's file_system_name attribute. If no volume_id
        was provided, the return value will be the "default" Mongo client for the microservice found in the HEA_DB
        application-level property.
        :raise ValueError: if there is no volume with the provided volume id, the volume's file system does not exist,
        the volume's credentials were not found, or a necessary service is not registered.

        TODO: need a separate exception thrown for when a service is not registered (so that the server can respond with a 500 error).
        TODO: need to lock around client creation because it's not threadsafe, manifested by sporadic KeyError: 'endpoint_resolver'.
        """
        return await self.__get_resource_or_client(request, service_name, volume_id, create_client)

    async def get_resource(self, request: Request, service_name: str, volume_id: str) -> S3ServiceResource:
        """
        Gets an AWS resource. If the volume has no credentials, it uses the boto3 library to try and find them. This
        method is not designed to be overridden.

        :param request: the HTTP request (required).
        :param service_name: AWS service name (required).
        :param volume_id: the id string of a volume (required).
        :return: a Mongo client for the file system specified by the volume's file_system_name attribute. If no volume_id
        was provided, the return value will be the "default" Mongo client for the microservice found in the HEA_DB
        application-level property.
        :raise ValueError: if there is no volume with the provided volume id, the volume's file system does not exist,
        the volume's credentials were not found, or a necessary service is not registered.

        TODO: need to lock around resource creation because it's not threadsafe, manifested by sporadic KeyError: 'endpoint_resolver'.
        """
        return await self.__get_resource_or_client(request, service_name, volume_id, create_resource)

    async def has_account(self, request: Request, volume_id: str) -> bool:
        """
        Return whether the current user can access the AWS accounts associated with the provided volume_id.

        :param request: the HTTP request object (required).
        :param volume_id: the volume id (required).
        :return: True or False.
        """
        return await self.get_account(request, volume_id) is not None

    async def get_account(self, request: Request, volume_id: str) -> AWSAccount | None:
        """
        Gets the current user's AWS account associated with the provided volume_id.

        :param request: the HTTP request object (required).
        :param volume_id: the volume id (required).
        :return: the AWS account, or None if not found.
        """
        async with STSClientContext(request, volume_id) as sts_client:
            return await S3._get_account(sts_client, request.headers.get(SUB, NONE_USER))

    async def get_accounts(self, request: Request, volume_ids: Sequence[str]) -> AsyncGenerator[
        tuple[AWSAccount, str], None]:
        """
        Gets the AWS accounts associated with the provided volume ids.

        :param request: the HTTP request object (required).
        :param volume_ids: the volume ids (required).
        :return: an async generator of tuples containing the AWS accounts and corresponding volume ids.
        """
        logger = logging.getLogger(__name__)

        async def execute(volume_id) -> tuple[AWSAccount, str]:
            async with STSClientContext(request, volume_id) as sts_client:
                return await S3._get_account(sts_client, request.headers.get(SUB, NONE_USER)), volume_id

        for i, account_volume in enumerate(await asyncio.gather(*(execute(volume_id) for volume_id in volume_ids),
                                                                return_exceptions=True)):
            if not isinstance(account_volume, tuple):
                if isinstance(account_volume, ValueError):
                    logger.error('Error getting account for volume %s', volume_ids[i], exc_info=account_volume)
                    continue
                else:
                    raise account_volume
            yield account_volume

    async def generate_cloud_credentials(self, request: Request, arn: str) -> AWSCredentials | None:
        """
        Create temporary credentials and return a newly created AWSCredentials object.

        :param request: the HTTP request (required).
        :param arn: The aws role arn that to be assumed
        :returns the AWSCredentials populated with the resource's content, None if no such resource exists.
        :raises ValueError: if an error occurs generating cloud credentials other than the user lacking permission.
        """
        return await _generate_cloud_credentials(request=request, arn=arn)

    async def get_credentials_from_volume(self, request: web.Request, volume_id: str) -> AWSCredentials | None:
        """
        Gets the volume's credentials.

        :param request: the HTTP request (required).
        :param volume_id: the volume id (required).
        :return a Credentials object, or None if no credentials were found.
        :raises ValueError: if no volume with that id exists
        """
        return await get_credentials_from_volume(request, volume_id, credential_type=AWSCredentials)

    @staticmethod
    async def _get_account(sts_client, owner: str) -> AWSAccount:
        logger = logging.getLogger(__name__)
        # aws_object_dict = {}
        account = AWSAccount()

        loop = asyncio.get_running_loop()
        identity = await loop.run_in_executor(None, sts_client.get_caller_identity)
        logger.debug('Caller identity: %s', identity)
        # user_future = loop.run_in_executor(None, iam_client.get_user)
        # await asyncio.wait([identity_future])  # , user_future])
        aid = identity.get('Account')
        # aws_object_dict['alias'] = next(iam_client.list_account_aliases()['AccountAliases'], None)  # Only exists for IAM accounts.
        # user = user_future.result()['User']
        # aws_object_dict['account_name'] = user.get('UserName')  # Only exists for IAM accounts.
        account.id = aid
        account.name = aid
        account.display_name = aid
        account.owner = owner
        account.source = AWS_SOURCE
        account.source_detail = AWS_SOURCE
        # account.created = user['CreateDate']
        # FIXME this info coming from Alternate Contact(below) gets 'permission denied' with IAMUser even with admin level access
        # not sure if only root account user can access. This is useful info need to investigate different strategy
        # alt_contact_resp = account_client.get_alternate_contact(AccountId=account.id, AlternateContactType='BILLING' )
        # alt_contact =  alt_contact_resp.get("AlternateContact ", None)
        # if alt_contact:
        # account.full_name = alt_contact.get("Name", None)

        return account

    async def __get_resource_or_client(self, request: Request, service_name: str, volume_id: str,
                                       creator: Callable[[str, str | None, str | None, str | None,
                                                          str | None], _S3Service]) -> _S3Service:
        logger = logging.getLogger(__name__)
        if volume_id is not None:
            credentials = await self.get_credentials_from_volume(request, volume_id)
            logger.debug("credentials retrieved from database checking if expired: %r", credentials)
            loop = asyncio.get_running_loop()
            if not credentials:  # delegate to boto3 to find the credentials
                return await loop.run_in_executor(None, creator, service_name)
            elif credentials.temporary:
                return await self.__get_temporary_credentials(request=request,
                                                              credentials=credentials,
                                                              creator=creator,
                                                              service_name=service_name)
            else:  # for permanent credentials
                return await loop.run_in_executor(None, partial(creator, service_name,
                                                                region_name=credentials.where,
                                                                aws_access_key_id=credentials.account,
                                                                aws_secret_access_key=credentials.password))

        else:
            raise ValueError('volume_id is required')

    async def __get_temporary_credentials(self, request: web.Request, credentials: AWSCredentials,
                                          creator: Callable[
                                              [str, str | None, str | None, str | None, str | None], _S3Service],
                                          service_name: str) -> Any:
        """
            Gets temporary credentials and returns the authorized client. In order to do that it
            gets the previous credential's role_arn and then assumes it.

            :param request: the aiohttp request
            :param credentials: the aws credentials last saved
            :param aws_source: must be either boto3.client or boto3.resource.
            :param service_name: The type of client to return
            :return: the boto3 client provided with credentials
            :raise ValueError if no previously saved credentials it raises ValueError
        """
        logger = logging.getLogger(__name__)
        assert credentials.role_arn is not None, 'credentials must have a non-None role_arn attribute'
        loop = asyncio.get_running_loop()

        if credentials.has_expired(S3.EXPIRATION_LIMIT):
            logger.debug("credentials need to be refreshed")
            cloud_creds = await self.generate_cloud_credentials(request, credentials.role_arn)
            if not cloud_creds:
                raise ValueError(f'Could not generate cloud credentials with these params {credentials.role_arn}')
            if logger.getEffectiveLevel() == logging.DEBUG:
                logger.debug("credentials successfully obtained from cloud: %s" % cloud_creds.to_dict())
            credentials.account = cloud_creds.account
            credentials.password = cloud_creds.password
            credentials.session_token = cloud_creds.session_token
            credentials.expiration = cloud_creds.expiration
            await self.update_credentials(request=request, credentials=credentials)
            logger.debug("credentials updated in the database")
        return await loop.run_in_executor(None, partial(creator,
                                                        service_name,
                                                        region_name=credentials.where,
                                                        aws_access_key_id=credentials.account,
                                                        aws_secret_access_key=credentials.password,
                                                        aws_session_token=credentials.session_token))


class S3WithMongo(S3, Mongo):
    def __init__(self, config: Optional[ConfigParser], **kwargs):
        super().__init__(config, **kwargs)


class S3Manager(MicroserviceDatabaseManager):
    """
    Database manager for mock Amazon Web Services S3 buckets. It will not make any calls to actual S3 buckets. This
    class is not designed to be subclassed.
    """

    def get_database(self) -> S3:
        return S3(self.config)

    @classmethod
    def database_types(self) -> list[str]:
        return ['system|awss3']


class S3WithMongoManager(S3Manager):

    def get_database(self) -> S3:
        return S3WithMongo(self.config)


class S3ClientContext(DatabaseContextManager[S3Client]):  # Go into db package?
    """
    Provides an S3 client.
    """

    def __init__(self, request: web.Request, volume_id: str):
        super().__init__(request, volume_id)

    async def connection(self) -> S3Client:
        return await cast(S3, self.request.app[HEA_DB]).get_client(self.request, 's3', self.volume_id)


class STSClientContext(DatabaseContextManager[STSClient]):  # Go into db package?
    """
    Provides an STS client.
    """

    def __init__(self, request: web.Request, volume_id: str):
        super().__init__(request, volume_id)

    async def connection(self) -> STSClient:
        return await cast(S3, self.request.app[HEA_DB]).get_client(self.request, 'sts', self.volume_id)


class AccountClientContext(DatabaseContextManager[AccountClient]):
    """
    Provides an Account client.
    """

    def __init__(self, request: web.Request, volume_id: str):
        super().__init__(request, volume_id)

    async def connection(self) -> AccountClient:
        return await cast(S3, self.request.app[HEA_DB]).get_client(self.request, 'account', self.volume_id)


class OrganizationsClientContext(DatabaseContextManager[OrganizationsClient]):
    """
    Provides an Organizations client.
    """

    def __init__(self, request: web.Request, volume_id: str):
        super().__init__(request, volume_id)

    async def connection(self) -> OrganizationsClient:
        return await cast(S3, self.request.app[HEA_DB]).get_client(self.request, 'organizations', self.volume_id)


@overload
def create_client(service_name: Literal['s3'],
                  region_name: str | None = None,
                  aws_access_key_id: str | None = None,
                  aws_secret_access_key: str | None = None,
                  aws_session_token: str | None = None) -> S3Client:
    ...


@overload
def create_client(service_name: Literal['sts'],
                  region_name: str | None = None,
                  aws_access_key_id: str | None = None,
                  aws_secret_access_key: str | None = None,
                  aws_session_token: str | None = None) -> STSClient:
    ...


@overload
def create_client(service_name: Literal['account'],
                  region_name: str | None = None,
                  aws_access_key_id: str | None = None,
                  aws_secret_access_key: str | None = None,
                  aws_session_token: str | None = None) -> AccountClient:
    ...


@overload
def create_client(service_name: Literal['organizations'],
                  region_name: str | None = None,
                  aws_access_key_id: str | None = None,
                  aws_secret_access_key: str | None = None,
                  aws_session_token: str | None = None) -> OrganizationsClient:
    ...


def create_client(service_name: Literal['s3', 'sts', 'account', 'organizations'],
                  region_name: str | None = None,
                  aws_access_key_id: str | None = None,
                  aws_secret_access_key: str | None = None,
                  aws_session_token: str | None = None) -> S3Client | STSClient | AccountClient | OrganizationsClient:
    """
    Thread-safe boto client creation. Once created, clients are generally
    thread-safe.
    """
    with _boto3_client_lock:
        return boto3.client(service_name,
                            region_name=region_name,
                            aws_access_key_id=aws_access_key_id,
                            aws_secret_access_key=aws_secret_access_key,
                            aws_session_token=aws_session_token)


def create_resource(service_name: Literal['s3'],
                    region_name: str | None = None,
                    aws_access_key_id: str | None = None,
                    aws_secret_access_key: str | None = None,
                    aws_session_token: str | None = None) -> S3ServiceResource:
    """
    Thread-safe boto resource creation. Resources are generally NOT
    thread-safe!
    """
    with _boto3_resource_lock:
        return boto3.resource(service_name,
                              region_name=region_name,
                              aws_access_key_id=aws_access_key_id,
                              aws_secret_access_key=aws_secret_access_key,
                              aws_session_token=aws_session_token)


async def _generate_cloud_credentials(request: Request, arn: str) -> AWSCredentials | None:
    """
    Create temporary credentials and return a newly created AWSCredentials object.

    :param request: the HTTP request (required).
    :param arn: The aws role arn that to be assumed
    :returns the AWSCredentials populated with the resource's content, None if no such resource exists.
    :raises ValueError: if an error occurs generating cloud credentials other than the user lacking permission.
    """
    logger = logging.getLogger(__name__)
    sub = request.headers.get(SUB, None)
    if sub is None:
        raise ValueError('OIDC SUB header is required')
    if not arn:
        raise ValueError('Cannot get credentials arn which is required')
    auth = request.headers.get(hdrs.AUTHORIZATION, '')
    auth_token = auth.split(' ')

    if len(auth_token) != 2:
        raise ValueError("Bearer Token is required in header")
    roles_url = await type_to_resource_url(request, Role)
    logger.debug('Checking if user %s has role %s...', sub, arn)
    assumed_role_object = None
    try:
        if await client.has(request.app, URL(roles_url) / 'byname' / encode_role(arn),
                            headers={hdrs.AUTHORIZATION: auth, SUB: sub}):
            logger.debug('User %s has role %s', sub, arn)
            loop = asyncio.get_running_loop()
            with closing(await loop.run_in_executor(None, boto3.client, 'sts')) as sts_client:
                assumed_role_object = await loop.run_in_executor(None, partial(sts_client.assume_role_with_web_identity,
                                                                               WebIdentityToken=auth_token[1],
                                                                               RoleArn=arn,
                                                                               RoleSessionName=sub,
                                                                               DurationSeconds=S3.MAX_DURATION_SECONDS
                                                                               ))
        else:
            logger.error('User %s does not have role %s', sub, arn)
            return None
    except ClientError:
        logger.exception('Permission denied')
        return None
    creds_dict = assumed_role_object.get('Credentials')
    if not creds_dict:
        return None
    creds = AWSCredentials()
    creds.account = creds_dict['AccessKeyId']
    creds.password = creds_dict['SecretAccessKey']
    creds.session_token = creds_dict['SessionToken']
    creds.expiration = assumed_role_object.get('Credentials')['Expiration']

    return creds
