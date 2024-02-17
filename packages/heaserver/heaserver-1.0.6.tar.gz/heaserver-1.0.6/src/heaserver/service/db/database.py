import abc
import configparser
import asyncio
from abc import ABC, abstractmethod
from contextlib import AbstractAsyncContextManager, ExitStack, contextmanager, AbstractContextManager
from types import TracebackType

from aiohttp import web
from typing import Any, Optional, TypeVar, Union
from collections.abc import Mapping, Generator, AsyncGenerator
from aiohttp.web import Request

from aiohttp.web_request import Request
from aiohttp.web_response import Response
from heaobject.keychain import Credentials, CredentialTypeVar
from heaobject.volume import FileSystemTypeVar, FileSystem, Volume
from heaobject.root import DesktopObjectDict, DesktopObject
from yarl import URL
from multidict import istr, CIMultiDict, CIMultiDictProxy

from heaobject.user import NONE_USER

from heaserver.service import client, response
from heaserver.service.heaobjectsupport import type_to_resource_url, desktop_object_type_or_type_name_to_type
from heaserver.service.oidcclaimhdrs import SUB
from heaserver.service.util import modified_environ

from copy import copy, deepcopy
import logging


class NotStartedError(ValueError):

    def __init__(self, *args: object) -> None:
        super().__init__('The database is not running. Call start_database() first.', *args)

class Database(abc.ABC):
    """
    Connectivity to databases and other data storage systems for HEA microservices. The database object may be
    optionally configured by providing a ConfigParser object to the constructor. The ConfigParser class provides a
    similar structure to what is found in Windows INI files, including the use of section headers. Section headers
    should be prefixed by the Database subclass' full class name as produced by str(cls) to avoid name clashes.
    Properties in the ConfigParser object should be named using CamelCase. This class is not designed for multiple
    inheritance.
    """

    def __init__(self, config: Optional[configparser.ConfigParser], **kwargs) -> None:
        """
        Initializes the database object. Subclasses must call this constructor.

        :param config: Optional HEA configuration.
        """
        super().__init__(**kwargs)
        logger = logging.getLogger(__name__)
        if logger.getEffectiveLevel() == logging.DEBUG:
            logger.debug('Initialized %s database object', type(self))

    @property
    @abstractmethod
    def file_system_type(self) -> type[FileSystem]:
        """The type of file system accessed by this database."""
        pass

    @classmethod
    def get_config_section(cls) -> str:
        """
        Gets this database type's section in the HEA configuration. By default, the section name is that produced by
        str(cls) in order to avoid name clashes. When overriding this method, take care not to construct a name that
        might clash with the current or future section header of another Database class.
        """
        return str(cls)

    async def get_file_system_and_credentials_from_volume(self, request: web.Request, volume_id: str) -> tuple[FileSystem, Credentials | None]:
        """
        Gets the file system and credentials for the given volume. It uses the registry microservice to access the
        file system and credentials microservices. Override this method to mock getting a file system and credentials.

        :param request: the aiohttp request (required).
        :param volume_id: a volume id string (required).
        :return: a tuple containing a FileSystem object and, if one exists, a Credentials object (or None if one does
        not).
        :raises ValueError: if no volume with that id exists, or no file system exists for the given volume.
        """
        return await get_file_system_and_credentials_from_volume(request, volume_id, self.file_system_type)

    async def get_credentials_from_volume(self, request: web.Request, volume_id: str) -> Credentials | None:
        """
        Gets the volume's credentials.

        :param request: the HTTP request (required).
        :param volume_id: the volume id (required).
        :return a Credentials object, or None if no credentials were found.
        :raises ValueError: if no volume with that id exists.
        """
        return await get_credentials_from_volume(request, volume_id)

    async def get_volumes(self, request: Request, file_system_type_or_type_name: str | type[FileSystem]) -> AsyncGenerator[Volume, None]:
        """
        An async generator of volumes of a given file system type. This implementation is identical to the module-level
        get_volumes() function.

        :param request: the HTTP request (required).
        :param file_system_type_or_type_name: the file system type or type name string (required).
        :raises ValueError: if no volume microservice is registered.
        :raises TypeError: if file_system_type_or_type_name is a type but not a FileSystem.
        """
        async for volume in get_volumes(request, file_system_type_or_type_name):
            yield volume

    async def is_creator(self, request: Request, for_type_or_type_name: str | type[DesktopObject]) -> bool:
        """
        Returns whether the current user may create new desktop objects of the given type. This method consults the
        registry service metadata to determine the user's create permissions.

        :param request: the HTTP request (required).
        :param for_type_or_type_name: the desktop object type or type name.
        :return: True or False.
        :raises ValueError: if an error occurred checking the registry service.
        """
        type_ = for_type_or_type_name.get_type_name() if issubclass(for_type_or_type_name, DesktopObject) else str(for_type_or_type_name)
        component = await client.get_component(request.app, type_)
        if component is None:
            raise ValueError(f'Could not find component for type {type_}')
        resource = component.get_resource(type_.get_type_name())
        if resource is None:
            raise ValueError(f'No resource found for type {type_}')
        return resource.is_creator_user(request.headers.get(SUB, NONE_USER))

    def close(self):
        """
        Closes the database connection. This method may be called multiple times.
        """
        pass


class NoDatabase(Database):
    pass


class InMemoryDatabase(Database, abc.ABC):
    """
    In-memory store of desktop objects and content.
    """

    def __init__(self, config: Optional[configparser.ConfigParser] = None,
                 desktop_objects: dict[str, list[DesktopObjectDict]] | None = None,
                 content: dict[str, dict[str, bytes]] | None = None,
                 **kwargs) -> None:
        """
        Initializes the in-memory database.

        :param config: a configparser.ConfigParser object.
        """
        super().__init__(config, **kwargs)
        if desktop_objects:
            self.__desktop_objects = dict(deepcopy(desktop_objects))
        else:
            self.__desktop_objects = {}
        if content:
            self.__content = dict(deepcopy(content))
        else:
            self.__content = {}

    def add_desktop_objects(self, data: Mapping[str, list[DesktopObjectDict]] | None):
        """
        Adds the given desktop objects to the given collection. If the collection does not exist, add that collection
        along with its objects.

        :param data: A dictionary whose keys are collections and whose contents are desktop objects
        """
        for coll, objs in (data or {}).items():
            if coll in self.__desktop_objects:
                self.__desktop_objects[coll].extend(deepcopy(objs))
            else:
                self.__desktop_objects.update({coll: deepcopy(objs)})

    def get_all_desktop_objects(self) -> list[DesktopObjectDict]:
        return deepcopy(self.__desktop_objects)

    def get_desktop_objects_by_collection(self, coll: str) -> list[DesktopObjectDict]:
        return deepcopy(self.__desktop_objects.get(coll, []))

    def get_desktop_object_by_collection_and_id(self, coll: str, id_: Optional[str]) -> Optional[DesktopObjectDict]:
        return deepcopy(next((d for d in self.__desktop_objects.get(coll, []) if d['id'] == id_), None))

    def update_desktop_object_by_collection_and_id(self, coll: str, id_: Optional[str],
                                                   new_value: DesktopObjectDict):
        """
        Updates the desktop object at the given location.

        :param coll: The collection in which the desktop object is located
        :param id_: The ID of the desktop object
        :param new_value: The new value of the desktop object
        """
        index = next((i for i, d in enumerate(self.__desktop_objects.get(coll, [])) if d['id'] == id_), None)
        if index is not None:
            self.__desktop_objects[coll][index] = new_value

    def remove_desktop_object_by_collection_and_id(self, coll: str, id_: Optional[str]):
        """
        Removes the desktop object (and its associated content) at the given location.

        :param coll: The collection in which the desktop object is located
        :param id_: The ID of the desktop object
        """
        index = next((i for i, d in enumerate(self.__desktop_objects.get(coll, [])) if d['id'] == id_), None)
        if index is not None:
            del self.__desktop_objects[coll][index]
            if coll in self.__content and id_ in self.__content[coll]:
                self.__content[coll].pop(id_)

    def add_content(self, content: Mapping[str, Mapping[str, bytes]] | None):
        """
        Adds the given content to the given collection. If there already is content for the object at the ID, replaces
        the content with new content.

        :param content: A dictionary whose keys are collections and whose values are dictionaries whose keys are the IDs
        of their corresponding desktop objects and whose values are the content
        """
        for coll, data in (content or {}).items():
            if coll in self.__content:
                self.__content[coll].update(dict(data))
            else:
                self.__content.update({coll: dict(data)})

    def get_all_content(self) -> dict[str, dict[str, bytes]]:
        return deepcopy(self.__content)

    def get_content_by_collection(self, coll: str) -> Optional[dict[str, bytes]]:
        return copy(self.__content.get(coll, None))

    def get_content_by_collection_and_id(self, coll: str, id_: str) -> Optional[bytes]:
        if (result := self.__content.get(coll, None)) is not None:
            return result.get(id_, None)
        else:
            return None


async def get_file_system_and_credentials_from_volume(request: Request, volume_id: str,
                                                      file_system_type: type[FileSystemTypeVar],
                                                      credential_type: type[CredentialTypeVar] | None = None) -> tuple[FileSystemTypeVar, CredentialTypeVar | None]:
    """
    Get the file system and credentials for the given volume.

    :param request: the aiohttp request (required).
    :param volume_id: a volume id string (required).
    :param file_system_type: the type of file system (required).
    :param credential_type: the type of credential (optional)
    :return: a tuple containing a FileSystem object and, if one exists, a Credentials object (or None if one does not).
    :raise ValueError: if no volume with that id exists, no file system exists for the given volume, the volume's
    credentials were not found, or there was a problem accessing the registry service.
    """
    headers = {SUB: request.headers[SUB]} if SUB in request.headers else None
    (volume, volume_url), fs_url = await asyncio.gather(_get_volume(request.app, volume_id, headers),
                                                        type_to_resource_url(request, FileSystem))
    if volume is None:
        raise ValueError(f'No volume with id {volume_id}')
    assert fs_url is not None, 'No file system service registered'
    file_system_future = client.get(request.app,
                                   URL(fs_url) / 'bytype' / file_system_type.get_type_name() / 'byname' / volume.file_system_name,
                                   file_system_type,
                                   headers=headers)
    credentials_future = _get_credentials(request.app, volume, credential_type, headers)
    file_system, credentials = await asyncio.gather(file_system_future, credentials_future)
    if file_system is None:
        raise ValueError(f"Volume {volume.id}'s file system {volume.file_system_name} does not exist")
    return file_system, credentials


async def get_credentials_from_volume(request: Request, volume_id: str,
                                      credential_type: type[CredentialTypeVar] | None = None) -> CredentialTypeVar | None:
    """
    Get the file system and credentials for the given volume.

    :param request: the aiohttp request (required).
    :param volume_id: a volume id string (required).
    :param credential_type: the type of credential (optional)
    :return: a tuple containing a FileSystem object and, if one exists, a Credentials object (or None if one does not).
    :raise ValueError: if no volume with that id exists, no file system exists for the given volume, or the volumes's
    credentials were not found.
    """
    headers = {SUB: request.headers[SUB]} if SUB in request.headers else None
    volume, volume_url = await _get_volume(request.app, volume_id, headers)
    if volume is None:
        raise ValueError(f'No volume with id {volume_id}')
    if volume_url is None:
        raise ValueError(f'Volume {volume_id} has no URL')
    return await _get_credentials(request.app, volume, credential_type, headers)


async def has_volume(request: Request, volume_id: Optional[str] = None,
                     headers: Optional[Mapping[str, str]] = None) -> Response:
    if volume_id is None:
        if 'volume_id' in request.match_info:
            volume_id_ = request.match_info['volume_id']
        elif 'id' in request.match_info:
            volume_id_ = request.match_info['id']
        else:
            volume_id_ = None
    else:
        volume_id_ = volume_id
    if volume_id_ is not None:
        volume_url = await type_to_resource_url(request, Volume)
        volume = await client.get(request.app, URL(volume_url) / volume_id_, Volume, headers=headers)
        if volume is None:
            return response.status_not_found()
        return response.status_ok()
    else:
        return response.status_not_found()


async def get_volumes(request: Request, file_system_type_or_type_name: Union[str, type[FileSystem]]) -> AsyncGenerator[
    Volume, None]:
    """
    Gets the volumes accessible to the current user that have the provided filesystem type.

    :param request: the aiohttp request (required).
    :param file_system_type_or_type_name: the filesystem type or type name.
    :return: an async generator of Volume objects.
    :raises ValueError: if no volume microservice is registered.
    :raises TypeError: if file_system_type_or_type_name is a type but not a FileSystem.
    """
    headers = {SUB: request.headers[SUB]} if SUB in request.headers else None
    volume_url = await type_to_resource_url(request, Volume)
    file_system_type_ = desktop_object_type_or_type_name_to_type(file_system_type_or_type_name)
    if not issubclass(file_system_type_, FileSystem):
        raise TypeError(f'Provided file_system_type_or_type_name is a {file_system_type_} not a FileSystem')
    get_volumes_url = URL(volume_url) / 'byfilesystemtype' / file_system_type_.get_type_name()

    async for volume in client.get_all(request.app, get_volumes_url, Volume, headers=headers):
        yield volume


async def get_options(request: Request, methods: list[str]):
    """
    Responds to an OPTIONS request. It calls the provided function, checks for the 200 status code, and if 200 is
    returned, returns a response with a 200 status code and an Allow header.

    :param request: the HTTP request (required).
    :param methods: a list of methods to include in the Allow header (required).
    :return: the HTTP response.
    """
    return await response.get_options(request, methods)


async def _get_volume(app: web.Application, volume_id: str, headers: Union[Mapping[Union[str, istr], str], CIMultiDict[str], CIMultiDictProxy[str], None] = None) -> tuple[Volume, str]:
    """
    Gets the volume with the provided id.

    :param app: the aiohttp app (required).
    :param volume_id: the id string of a volume.
    :param headers: any headers.
    :return: a two-tuple with either the Volume and its URL.
    :raise ValueError: if there is no volume with the provided volume id, or there was a problem accessing the registry
    service.
    """
    if volume_id is None:
        raise ValueError('volume_id cannot be None')
    volume_url = await client.get_resource_url(app, Volume)
    if volume_url is None:
        raise ValueError(f'No volume resource in the registry service')
    volume = await client.get(app, URL(volume_url) / volume_id, Volume, headers=headers)
    if volume is None:
        raise ValueError(f'No volume with volume_id={volume_id}')
    return volume, volume_url


async def _get_credentials(app: web.Application, volume: Volume, cred_type: Optional[type[CredentialTypeVar]] = None,
                           headers: Optional[Mapping] = None) -> Optional[CredentialTypeVar]:
    """
    Gets a credential specified in the provided volume, or if there is none, a credential with the where attribute set
    to the volume's URL.

    :param app: the aiohttp app (required).
    :param volume: the Volume (required).
    :param volume_url: the volume's URL (required).
    :param cred_type: The Credential's Type to be instantiated
    :param headers: any headers.
    :return: the Credentials, or None if the volume has no credentials.
    :raise ValueError: if the volume's credentials were not found, there was a problem accessing the registry
    service, or the type of credential associated with the volume does not match cred_type.
    """
    if volume.credential_id is not None:
        cred_url = await client.get_resource_url(app, Credentials)
        credential = await client.get(app, URL(cred_url) / volume.credential_id, type_or_obj=cred_type, headers=headers)
        if credential is not None:
            return credential
        else:
            raise ValueError(f'Credential {volume.credential_id} not found')
    else:
        return None


class DatabaseManager(ABC):
    """
    Abstract base class for database managers. These classes start a database, load data into it, return a Database
    object for manipulating the data, and delete the data. All subclasses of DatabaseManager must have a no-arg
    constructor, and they are expected to be immutable.
    """

    def __init__(self, config: configparser.ConfigParser | None = None):
        self.__started = False
        self.config = config
        self.__databases: list[Database] = []

    @property
    def config(self) -> configparser.ConfigParser:
        """
        Database configuration.
        """
        return self.__config

    @config.setter
    def config(self, config: configparser.ConfigParser | None):
        self.__config = config

    def start_database(self, context_manager: ExitStack) -> None:
        """
        Starts the database. The provided context manager will destroy the database automatically. Override this
        method to start a database, such as in a docker container. Place the super() call after the database is
        already started.

        :param context_manager: a context manager for creating and destroying the database (required).
        :raises heaserver.service.error.DatabaseStartException: if the database fails to start.
        """
        self.__started = True

    @property
    def started(self) -> bool:
        return self.__started

    def get_env_vars(self, ) -> dict[str, str]:
        """
        Gets environment variables to connect to this database. This default implementation
        returns an empty dict. This method may only be called after the start_database() method. Override this method
        to return a dictionary of environment variable name-value pairs.

        :return: a str->str dict.
        """
        return {}

    def get_config_file_section(self) -> str:
        """
        Creates a HEA configuration file section for connecting to this database. This default implementation returns
        an empty string. This method may only be called after the start_database() method.

        :return: a string.
        """
        return ''

    @abstractmethod
    def insert_all(self, desktop_objects: Optional[dict[str, list[DesktopObjectDict]]],
                   content: Optional[dict[str, dict[str, bytes]]]):
        """
        Inserts all data and content. Failure may put the object in an inconsistent state where one is properly
        inserted but the other is not. This method is not designed to be overridden.

        :raises KeyError: if an unexpected key was found in the data or the content.
        """
        pass

    @abstractmethod
    def delete_all(self):
        pass

    def close(self):
        """
        Removes all data and content, and cleans up any other resources created
        by other methods of this object. This method is not designed to be
        overridden. This method may be called multiple times.
        """
        if self.started:
            try:
                self.delete_all()
            finally:
                try:
                    exceptions = []
                    while self.__databases:
                        try:
                            self.__databases.pop().close()
                        except Exception as e:
                            exceptions.append(e)
                finally:
                    if exceptions:
                        raise exceptions[0]  # Use exception groups in Python 3.11.

    @classmethod
    def get_environment_to_remove(cls) -> list[str]:
        """
        Gets any environment variables that need to be removed temporarily for the database.

        :return: a list of environment variable names, or the empty list.
        """
        return []

    @classmethod
    def get_environment_updates(cls) -> dict[str, str]:
        """
        Gets a newly created dict with any environment variables that are needed by the database.

        :return: environment variable name -> value dict, or the empty dict if no environment variables are needed.
        """
        return {}

    @classmethod
    @contextmanager
    def environment(cls):
        with modified_environ(*cls.get_environment_to_remove(), **cls.get_environment_updates()):
            yield

    @classmethod
    def get_context(cls) -> list[AbstractContextManager]:
        """
        Gets a newly created list of context managers, or the empty list if there are none. This method is called by
        the context() context manager, which instantiates any context managers in the list.
        """
        return []

    @classmethod
    @contextmanager
    def context(cls):
        with ExitStack() as stack:
            for context_ in cls.get_context():
                stack.enter_context(context_)
            yield

    @classmethod
    @abstractmethod
    def database_types(self) -> list[str]:
        pass

    @abstractmethod
    def get_database(self) -> Database:
        """
        Gets a database object to perform queries. This object's close() method
        must be called when you are done with it. Accessing the object via the
        database() context manager causes it to be closed automatically.
        Concrete subclasses must implement this method.

        :return: the database object.
        """
        pass

    @contextmanager
    def database(self) -> Generator[Database, None, None]:
        """
        Context manager that creates the corresponding Database object.
        Override this method to return a Database instance. The database object
        will be closed automatically.

        :return: the database object.
        """
        db = self.get_database()
        if db is None:
            raise ValueError('The database is not running. Did you call start_database()?')
        try:
            yield db
        finally:
            db.close()


class MicroserviceDatabaseManager(DatabaseManager, ABC):
    """
    Abstract base class for database managers. These classes start a database, load data into it, return a Database
    object for manipulating the data, and delete the data. All subclasses of TestDatabaseManager must have a no-arg
    constructor, and they are expected to be immutable.
    """

    def insert_desktop_objects(self, desktop_objects: Optional[Mapping[str, list[DesktopObjectDict]]]):
        """
        Inserts data into the database. The start_database() method must be called before calling this method. The
        default implementation does nothing and is expected to be overridden with an implementation for a specific
        database technology. Implementations should anticipate multiple inheritance. Call super(), and do not pass
        desktop object collections that are handled by this collection into the superclass' implementation.

        :param desktop_objects: a dict of collection -> list of desktop object dicts. Required.
        :raises KeyError: if an unexpected key was found in the data.
        """
        if not self.started:
            raise NotStartedError

    def insert_content(self, content: Optional[Mapping[str, Mapping[str, bytes]]]):
        """
        Inserts content into the database. The start_database() method must be called before calling this method.
        The default implementation does nothing and is expected to be overridden with an implementation for a specific
        database technology. Implementations should anticipate multiple inheritance. Call super(), and do not pass
        content collections that are handled by this collection into the superclass' implementation.

        :param content: a dict of collection -> dict of desktop object id -> content. Required.
        :raises KeyError: if an unexpected key was found in the content.
        """
        if not self.started:
            raise NotStartedError

    def insert_all(self, desktop_objects: Optional[Mapping[str, list[DesktopObjectDict]]], content: Optional[Mapping[str, Mapping[str, bytes]]]):
        """
        Inserts all data and content. Failure may put the object in an inconsistent state where one is properly
        inserted but the other is not. This method is not designed to be overridden.

        :raises KeyError: if an unexpected key was found in the data or the content.
        """
        self.insert_desktop_objects(desktop_objects)
        self.insert_content(content)

    def delete_desktop_objects(self):
        """
        Deletes data from the database. The start_database() method must be called before calling this method. This
        should support being called multiple times, and after the first time have no effect. Override this method to
        delete the provided desktop objects from the database.

        :raises KeyError: if an unexpected key was found in the data.
        """
        if not self.started:
            raise NotStartedError

    def delete_content(self):
        """
        Deletes content from the database. The start_database() method must be called before calling this method. This
        should support being called multiple times, and after the first time have no effect. Override this method to
        delete the provided content from the database.

        :raises KeyError: if an unexpected key was found in the content.
        """
        if not self.started:
            raise NotStartedError

    def delete_all(self):
        try:
            self.delete_desktop_objects()
        finally:
            self.delete_content()

DatabaseClient = TypeVar('DatabaseClient')

class DatabaseContextManager(AbstractAsyncContextManager[DatabaseClient], ABC):
    def __init__(self, request: Request, volume_id: str | None = None) -> None:
        if request is None:
            raise ValueError('Request cannot be None')
        if not isinstance(request, Request):
            raise ValueError(f'request {request} must be a Request')
        self.__request = request
        self.__volume_id = str(volume_id) if volume_id is not None else None

    async def __aenter__(self) -> DatabaseClient:
        return await self.connection()

    async def __aexit__(self, exc_type: type[BaseException] | None,
                        exc_value: BaseException | None,
                        traceback: TracebackType | None) -> Any:
        (await self.connection()).close()

    @abstractmethod
    async def connection(self) -> DatabaseClient:
        """Returns the database connection."""
        pass

    @property
    def request(self) -> Request:
        return self.__request

    @property
    def volume_id(self) -> str:
        return self.__volume_id


class NoDatabaseManager(MicroserviceDatabaseManager):
    def get_database(self) -> Database:
        return NoDatabase()

    @classmethod
    def database_types(self) -> list[str]:
        return ['system|nodatabase']
