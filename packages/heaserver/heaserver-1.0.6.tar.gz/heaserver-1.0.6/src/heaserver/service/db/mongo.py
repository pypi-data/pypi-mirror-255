"""Connectivity to a MongoDB database for HEA resources.

A MongoDB collection name may only be used by one microservice in a database instance. In addition, for microservices
with content, the collections <collection_name>.files and <collection_name>.chunks will be used for storing the
content. The following collection names are used by existing HEA microservices and are reserved:

folders
folder_items
data_adapters
components
properties
volumes
organizations
"""
from contextlib import contextmanager
from motor import motor_asyncio
from aiohttp import web
from copy import deepcopy

from .mongoexpr import mongo_expr, sub_filter_expr
from ..heaobjectsupport import RESTPermissionGroup, has_permissions
from ..aiohttp import RequestFileLikeWrapper
from .database import get_file_system_and_credentials_from_volume
import bson
import pymongo
from bson.codec_options import CodecOptions
import logging
import configparser
from typing import Literal, Optional, Any, IO
from collections.abc import Collection, AsyncGenerator, Sequence, Mapping
from heaobject import user, root
from heaobject.volume import MongoDBFileSystem
from pymongo.results import UpdateResult, DeleteResult
from .database import Database, DatabaseContextManager, MicroserviceDatabaseManager
from yarl import URL
from motor.motor_asyncio import AsyncIOMotorGridFSBucket
from ..response import SupportsAsyncRead
from gridfs.errors import NoFile
from bson import ObjectId
from heaserver.service.appproperty import HEA_DB
from typing import cast

_codec_options = CodecOptions(tz_aware=True)


class Mongo(Database):
    """
    Connectivity to a MongoDB database for HEA resources.
    """

    def __init__(self, config: Optional[configparser.ConfigParser],
                 connection_string: Optional[str] = None,
                 username: Optional[str] = None,
                 password: Optional[str] = None,
                 database_name: Optional[str] = None,
                 **kwargs) -> None:
        """
        Performs initialization.

        :param config: a configparser.ConfigParser object, which should have a MongoDB section with two properties:

                ConnectionString = the MongoDB connection string, default is http://localhost:5432
                Name = the database name, default is heaserver

                If the MongoDB section is missing or config argument is None, the default database name will be heaserver, and
                the default connection string will be http://localhost:27017.
        :param connection_string: an optional MongoDB connection string that will override any database connection
        string in a provided config file.
        :param username: an optional user name that will override any user name in the connection string.
        :param password: an optional password that will override any password in the connection string.
        :param database_name: an optional database name that will override any database name in a provided config file.
        """
        super().__init__(config, **kwargs)
        logger = logging.getLogger(__name__)

        default_connection_string = 'mongodb://heauser:heauser@localhost:27017/hea'

        config_section = Mongo.get_config_section()
        if config and config_section in config:
            logger.debug('Parsing MongoDB section of config file')
            database_section = config[config_section]
            try:
                if connection_string is not None:
                    conn_url = URL(connection_string)
                else:
                    connection_string = database_section.get('ConnectionString', default_connection_string)
                    conn_url = URL(connection_string)
            except ValueError as e:
                # We wrap the original exception so we can see the URL string that caused it.
                raise ValueError(f'Error creating URL {connection_string}') from e
            if username is not None:
                conn_url = conn_url.with_user(username)
            if password is not None:
                conn_url = conn_url.with_password(password)
            logger.debug('\tUsing connection string %s', conn_url.with_password('xxxxxxxx'))
            if database_name is not None:
                name = database_name
            else:
                name = database_section.get('Name')
            client = motor_asyncio.AsyncIOMotorClient(str(conn_url))
            logger.debug('\tUsing database %s', name or 'default from connection string')
            self.__connection_pool = client.get_database(name=name)
        else:

            if connection_string is not None:
                try:
                    conn_url = URL(connection_string)
                except ValueError as e:
                    # We wrap the original exception so we can see the URL string that caused it.
                    raise ValueError(f'Error creating URL {connection_string}') from e
            else:
                conn_url = URL(default_connection_string)
            if username is not None:
                conn_url = conn_url.with_user(username)
            if password is not None:
                conn_url = conn_url.with_password(password)
            logger.debug('\tUsing connection string %s',
                         str(conn_url.with_password('xxxxxxxx')) if conn_url.password is None else str(conn_url))
            client = motor_asyncio.AsyncIOMotorClient(str(conn_url))
            if database_name is not None:
                self.__connection_pool = client.get_database(name=database_name)
            else:
                self.__connection_pool = client.get_database()

    @classmethod
    def get_config_section(cls) -> str:
        return 'MongoDB'

    @property
    def file_system_type(self) -> type[MongoDBFileSystem]:
        return MongoDBFileSystem

    async def get(self, request: web.Request, collection: str, var_parts=None, mongoattributes=None,
                  sub: Optional[str] = None) -> Optional[root.DesktopObjectDict]:
        """
        Gets an object from the database.

        :param request: the aiohttp Request object (required).
        :param collection: the mockmongo collection (required).
        :param var_parts: the names of the dynamic resource's variable parts (required).
        :param mongoattributes: the attribute to query by. The default value is None. If None, the var_parts will be
        used as the attributes to query by.
        :param sub: the user to filter by.
        :return: a HEA name-value pair dict, or None if not found.
        """
        logger = logging.getLogger(__name__)
        coll = self._get_collection(collection)
        try:
            extra_ = sub_filter_expr(sub or user.NONE_USER,
                                     permissions=[perm.name for perm in RESTPermissionGroup.GETTER_PERMS._perms_internal])
            q = Mongo.__replace_object_ids(mongo_expr(request,
                                                      var_parts,
                                                      mongoattributes,
                                                      extra_))
            logger.debug('Query is %s', q)
            result = await coll.find_one(q)
            if result is not None:
                result['id'] = str(result['_id'])
                del result['_id']
            logger.debug('Got from mongo: %s', result)
            return result
        except bson.errors.InvalidId as e:
            logger.debug('Skipped mongo query: %s', e)
            return None

    async def get_content(self, request: web.Request, collection: str, var_parts=None, mongoattributes=None,
                          sub: Optional[str] = None) -> Optional[SupportsAsyncRead]:
        """
        Handles getting a HEA object's associated content.

        :param request: the HTTP request. Required.
        :param collection: the Mongo collection name. Required.
        :param var_parts: See heaserver.service.db.mongoexpr.mongo_expr.
        :param mongoattributes: See heaserver.service.db.mongoexpr.mongo_expr.
        :param sub: the user to filter by. Defaults to None.
        :return: a Response with the requested HEA object or Not Found.
        """
        obj = await self.get(request, collection, var_parts, mongoattributes, sub)
        if obj is None:
            return None
        fs = self.__new_gridfs_bucket(collection)
        try:
            return await fs.open_download_stream(ObjectId(request.match_info['id']))
        except NoFile:
            return None

    async def get_all(self, request: web.Request, collection: str, var_parts=None, mongoattributes=None,
                      sub: Optional[str] = None, sort: dict[str, Literal[-1, 1]] | None = None) -> AsyncGenerator[root.DesktopObjectDict, None]:
        """
        Handle a get request.

        :param request: the HTTP request (required). This function uses the following query parameters, if present:
            begin: the index of the first object of the collection to return, inclusive.
            end: the index of the last object of the collection to return, exclusive.
        :param collection: the MongoDB collection containing the requested object (required).
        :param var_parts: the names of the dynamic resource's variable parts (required).
        :param mongoattributes: the attributes to query by. The default value is None. If None, the var_parts will be
        used as the attributes to query by.
        :param sub: the user to filter by.
        :param sort: optional properties to sort by.
        :return: an async generator of HEA name-value pair dicts with the results of the mockmongo query.
        """
        logger = logging.getLogger(__name__)
        begin = int(request.query.get('begin', 0))
        end = request.query.get('end', None)
        end_ = int(end) if end is not None else None
        coll = self._get_collection(collection)
        if var_parts is not None or mongoattributes is not None:
            q = Mongo.__replace_object_ids(mongo_expr(request,
                                                      var_parts,
                                                      mongoattributes,
                                                      sub_filter_expr(sub or user.NONE_USER,
                                                                      permissions=[perm.name for perm in
                                                                                   RESTPermissionGroup.GETTER_PERMS._perms_internal]))
                                           )
        else:
            q = sub_filter_expr(sub or user.NONE_USER,
                                permissions=[perm.name for perm in RESTPermissionGroup.GETTER_PERMS._perms_internal])
        logger.debug('Query is %s; sort order is %s', q, sort)
        if sort is not None and (begin > 0 or end_ is not None):
            sort_ = sort | {'_id' : 1} if 'id' not in sort else {}
        else:
            sort_ = sort
        mongo_query = coll.find(q) if sort is None else coll.find(q).sort([(k, v) for k, v in sort_.items()])
        if begin > 0:
            mongo_query = mongo_query.skip(begin)
        if end_ is not None:
            mongo_query = mongo_query.limit(end_ - begin)
        async for result in mongo_query:
            result['id'] = str(result['_id'])
            del result['_id']
            logger.debug('Get all from mongo: %s', result)
            yield result

    async def empty(self, request: web.Request, collection: str, var_parts=None, mongoattributes=None,
                    sub: Optional[str] = None) -> bool:
        """
        Returns whether there are no results returned from the query.

        :param request: the HTTP request (required).
        :param collection: the MongoDB collection containing the requested object (required).
        :param var_parts: the names of the dynamic resource's variable parts (required).
        :param mongoattributes: the attributes to query by. The default value is None. If None, the var_parts will be
        used as the attributes to query by.
        :param sub: the user to filter by.
        :return: True or False.
        """
        logger = logging.getLogger(__name__)
        coll = self._get_collection(collection)
        if var_parts is not None or mongoattributes is not None:
            q = Mongo.__replace_object_ids(mongo_expr(request,
                                                      var_parts,
                                                      mongoattributes,
                                                      sub_filter_expr(sub or user.NONE_USER,
                                                                      permissions=[perm.name for perm in
                                                                                   RESTPermissionGroup.GETTER_PERMS._perms_internal]))
                                           )
            logger.debug('Query is %s', q)
            result = await coll.find_one(q) is None
        else:
            q = sub_filter_expr(sub or user.NONE_USER,
                                permissions=[perm.name for perm in RESTPermissionGroup.GETTER_PERMS._perms_internal])
            logger.debug('Query is %s', q)
            result = await coll.find_one(q) is None
        logger.debug('Got from mongo: %s', result)
        return result

    async def post(self, request: web.Request, obj: root.DesktopObject, collection: str,
                   default_content: Optional[IO] = None) -> Optional[str]:
        """
        Handle a post request.

        :param request: the HTTP request (required).
        :param obj: the HEAObject instance to post.
        :param collection: the MongoDB collection containing the requested object (required).
        :param default_content: the content the HEA object will have once the object has been posted. If None, the
        object will not have content.
        :return: the generated id of the created object, or None if the object could not be inserted or was None.
        """
        # Need to check if the user has permission to insert into the requested collection.
        return await self.insert_admin(obj, collection, default_content)

    async def put(self, request: web.Request, obj: root.DesktopObject, collection: str, sub: Optional[str] = None) -> \
        Optional[UpdateResult]:
        """
        Handle a put request.

        :param request: the HTTP request (required).
        :param obj: the desktop object instance to put.
        :param collection: the MongoDB collection containing the requested object (required).
        :param sub: the user to filter by. Defaults to None.
        :return: an instance of pymongo.results.UpdateResult.
        """
        coll = self._get_collection(collection)
        try:
            extra_ = sub_filter_expr(sub or user.NONE_USER,
                                     permissions=[perm.name for perm in RESTPermissionGroup.PUTTER_PERMS._perms_internal])
            mongo_expr_ = Mongo.__replace_object_ids(mongo_expr(request, 'id', extra=extra_))
            return await coll.replace_one(mongo_expr_, replace_id_with_object_id(obj.to_dict()))
        except bson.errors.InvalidId:
            return None

    async def put_content(self, request: web.Request, collection: str, sub: Optional[str] = None) -> bool:
        """
        Handle a put request of an HEA object's content.

        :param request: the HTTP request (required).
        :param collection: the MongoDB collection containing the requested object (required).
        :param sub: the user to filter by. Defaults to None.
        :return: Whether or not it was successful.
        """
        obj = await self.get(request, collection, var_parts=['id'], sub=sub)
        if obj is None:
            return False
        desktop_obj = root.desktop_object_from_dict(obj)
        if not has_permissions(desktop_obj, sub, RESTPermissionGroup.PUTTER_PERMS._perms_internal):
            return False
        try:
            fs = self.__new_gridfs_bucket(collection)
            fileobj = RequestFileLikeWrapper(request)
            fileobj.initialize()
            failed = True
            try:
                await fs.upload_from_stream_with_id(ObjectId(request.match_info['id']), obj['display_name'], fileobj)
                fileobj.close()
                failed = False
            except Exception as e:
                if failed:
                    try:
                        fileobj.close()
                    except:
                        pass
                raise e
            return True
        except NoFile:
            # Delete orphaned chunks from gridfs if an error occurred
            return False

    async def delete(self, request: web.Request, collection: str, var_parts=None, mongoattributes=None,
                     sub: Optional[str] = None) -> Optional[DeleteResult]:
        """
        Handle a delete request.

        :param request: the HTTP request.
        :param collection: the MongoDB collection containing the requested object (required).
        :param var_parts: See heaserver.service.db.mongoexpr.mongo_expr.
        :param mongoattributes: See heaserver.service.db.mongoexpr.mongo_expr.
        :param sub: the user to filter by. Defaults to None.
        :return: an instance of pymongo.results.DeleteResult.
        """
        coll = self._get_collection(collection)
        try:
            mongo_expr_ = self.__mongo_expr(request, var_parts, mongoattributes, sub, RESTPermissionGroup.DELETER_PERMS._perms_internal)
            result = await coll.delete_many(mongo_expr_)
            if result:
                fs = self.__new_gridfs_bucket(collection)
                try:
                    await fs.delete(ObjectId(request.match_info['id']))
                except NoFile:
                    pass
                finally:
                    return result
        except bson.errors.InvalidId:
            pass
        return None

    async def get_admin(self, collection: str, mongoattributes=None) -> root.DesktopObjectDict | None:
        """
        Gets an object from the database with no permissions checking.
        """
        logger = logging.getLogger(__name__)
        coll = self._get_collection(collection)
        try:
            q = Mongo.__replace_object_ids(mongo_expr(None,
                                                      None,
                                                      mongoattributes))
            logger.debug('Query is %s', q)
            result = await coll.find_one(q)
            if result is not None:
                result['id'] = str(result['_id'])
                del result['_id']
            logger.debug('Got from mongo: %s', result)
            return result
        except bson.errors.InvalidId as e:
            logger.debug('Skipped mongo query: %s', e)
            return None

    async def get_all_admin(self, collection: str, mongoattributes=None, sort: dict[str, Literal[-1, 1]] | None = None) -> AsyncGenerator[root.DesktopObjectDict, None]:
        logger = logging.getLogger(__name__)
        coll = self._get_collection(collection)
        q = Mongo.__replace_object_ids(mongo_expr(None, None, mongoattributes))
        logger.debug('Query is %s; sort order is %s', q, sort)
        async for result in (coll.find(q) if sort is None else coll.find(q).sort([(k, v) for k, v in sort.items()])):
            result['id'] = str(result['_id'])
            del result['_id']
            logger.debug('Get all from mongo: %s', result)
            yield result

    async def upsert_admin(self, obj: root.DesktopObject | root.DesktopObjectDict, collection: str, mongoattributes: Mapping[str, Any] | None=None, default_content: Optional[IO] = None) -> Any:
        """
        Updates a desktop object into the database, if an object with the same id or attributes is already present;
        otherwise inserts a new object. The object's content, if any, is also inserted or updated. No permission
        checking is performed.

        :param obj: the HEAObject instance to post.
        :param collection: the MongoDB collection containing the requested object (required).
        :param default_content: the content the HEA object will have once the object has been posted. If None, the
        object will not have content. If trying to post content, obj must have a display_name attribute.
        :return: the generated id of the created object, or None if the object could not be inserted or was None.
        """
        logger = logging.getLogger(__name__)
        if obj is None:
            return None
        if isinstance(obj, root.DesktopObject):
            obj_ = obj.to_dict()
        else:
            obj_ = obj
        coll = self._get_collection(collection)
        try:
            if mongoattributes is None and 'id' not in obj_:
                result = await coll.insert_one(obj_)
            else:
                result = await coll.replace_one({'_id': ObjectId(obj_['id'])} if mongoattributes is None else mongoattributes, obj_, upsert=True)
            if result and default_content is not None:
                fs = self.__new_gridfs_bucket(collection)
                await fs.upload_from_stream_with_id(ObjectId(result.upserted_id), obj_['display_name'], default_content)
            return result.upserted_id
        except NoFile:
            logger.exception('Error inserting %s into collection', obj_, collection);
            return None

    async def insert_admin(self, obj: root.DesktopObject | root.DesktopObjectDict, collection: str, default_content: Optional[IO] = None) -> str | None:
        """
        Insert a desktop object into the database, with its content if provided, and with no permission checking.

        :param obj: the HEAObject instance to post.
        :param collection: the MongoDB collection containing the requested object (required).
        :param default_content: the content the HEA object will have once the object has been posted. If None, the
        object will not have content. If trying to post content, obj must have a display_name attribute.
        :return: the generated id of the created object, or None if the object could not be inserted or was None.
        """
        logger = logging.getLogger(__name__)
        if obj is None:
            return None
        if isinstance(obj, root.DesktopObject):
            obj_ = obj.to_dict()
        else:
            obj_ = obj
        coll = self._get_collection(collection)
        try:
            result = await coll.insert_one(document=obj_)
            if result and default_content is not None:
                fs = self.__new_gridfs_bucket(collection)
                await fs.upload_from_stream_with_id(ObjectId(result.inserted_id), obj_['display_name'], default_content)
            return str(result.inserted_id)
        except (pymongo.errors.DuplicateKeyError, NoFile) as e:
            logger.exception('Error inserting %s into collection', obj_, collection);
            return None

    async def update_admin(self, obj: root.DesktopObject | root.DesktopObjectDict, collection: str, default_content: Optional[IO] = None) -> UpdateResult | None:
        """
        Updates a desktop object in the database, with its content if provided, and with no permission checking.

        :param obj: the HEAObject instance to post.
        :param collection: the MongoDB collection containing the requested object (required).
        :param default_content: the content the HEA object will have once the object has been posted. If None, the
        object will not have content.
        :return: the generated id of the created object, or None if the object could not be inserted or was None.
        """
        logger = logging.getLogger(__name__)
        if obj is None:
            return None
        if isinstance(obj, root.DesktopObject):
            obj_ = obj.to_dict()
        else:
            obj_ = obj
        coll = self._get_collection(collection)
        try:
            result = await coll.replace_one({'_id': ObjectId(obj_['id'])}, obj_)
            if result and default_content is not None:
                fs = self.__new_gridfs_bucket(collection)
                await fs.upload_from_stream_with_id(ObjectId(obj_['id']), obj_['display_name'], default_content)
            return result
        except (pymongo.errors.DuplicateKeyError, NoFile) as e:
            logger.exception('Error updating %s in collection %s', obj_, collection);
            return None

    async def delete_admin(self, collection: str, mongoattributes=None) -> DeleteResult | None:
        logger = logging.getLogger(__name__)
        coll = self._get_collection(collection)
        try:
            q = Mongo.__replace_object_ids(mongo_expr(None,
                                                      None,
                                                      mongoattributes))
            logger.debug('Query is %s', q)
            to_delete = []
            async for result in coll.find(q):
                result['id'] = str(result['_id'])
                del result['_id']
                logger.debug('Get all from mongo: %s', result)
                to_delete.append(result)
            result = await coll.delete_many(q)
            if result:
                fs = self.__new_gridfs_bucket(collection)
                try:
                    for to_delete_ in to_delete:
                        await fs.delete(ObjectId(to_delete_['id']))
                except NoFile:
                    pass
                finally:
                    return result
        except bson.errors.InvalidId as e:
            logger.debug('Skipped mongo query: %s', e)
            return None

    async def aggregate(self, collection: str, pipeline: Sequence[Mapping[str, Any]], *args, **kwargs) -> AsyncGenerator[root.DesktopObjectDict, None]:
        """
        Execute the provided aggregate pipeline on a collection. Aggregate command parameters should be passed as
        keyword arguments to this method.

        :param collection: the name of the collection (required).
        :param pipeline: the pipeline (required).
        :return: the returned documents.
        """
        coll = self._get_collection(collection)
        async for doc in coll.aggregate(pipeline, *args, **kwargs):
            if '_id' in doc:
                doc['id'] = str(doc['_id'])
                del doc['_id']
            yield doc

    async def ping(self):
        """
        Raises an exception if the database does not respond to a ping command.
        """
        await self.__connection_pool.command('ping')

    def _get_collection(self, collection: str) -> motor_asyncio.AsyncIOMotorCollection:
        """
        Get the requested collection object.

        :param collection: the name of the collection to get.
        :return: the collection object.
        """
        return self.__connection_pool.get_collection(collection, codec_options=_codec_options)

    @staticmethod
    def __mongo_expr(request: web.Request,
                     var_parts=None,
                     mongoattributes=None,
                     sub: str | None = None,
                     perms: Collection[root.Permission] = None) -> dict[str, Any]:
        extra_ = sub_filter_expr(sub or user.NONE_USER, permissions=[perm.name for perm in perms])
        return Mongo.__replace_object_ids(mongo_expr(request, var_parts, mongoattributes, extra_))

    @staticmethod
    def __replace_object_ids(filter_criteria: dict[str, Any]) -> dict[str, Any]:
        """
        Replaces all "id" fields with string value with an "_id" field with its bson.objectid.ObjectId value.

        :param filter_criteria: a MongoDB filter
        :return: a deep copy of the same filter, with string id fields replaced with ObjectId _id fields.
        :raises bson.errors.InvalidId: if any id fields are not a 12-byte input or a 24-character hex string.
        """
        logger = logging.getLogger(__name__)
        logger.debug('Input: %s', filter_criteria)

        def do_replace(filter_criteria_: dict[str, Any]):
            result_ = {}
            for nm, val in filter_criteria_.items():
                if nm == 'id':
                    result_['_id'] = bson.objectid.ObjectId(val)
                elif isinstance(val, dict):
                    result_[nm] = do_replace(val)
                else:
                    result_[nm] = deepcopy(val)
            return result_

        result = do_replace(filter_criteria)
        logger.debug('Output: %s', result)
        return result

    def __new_gridfs_bucket(self, bucket: str) -> AsyncIOMotorGridFSBucket:
        return AsyncIOMotorGridFSBucket(self.__connection_pool, bucket)


def replace_id_with_object_id(obj: dict[str, Any]):
    """
    Returns a shallow copy of the provided dict with any id key replaced by an _id key with an ObjectId value.
    :param obj: a HEA object as a dict.
    :return: a newly created dict.
    """
    if 'id' in obj:
        f_ = dict(obj)
        f_['_id'] = bson.ObjectId(f_.pop('id', None))
        return f_
    else:
        return dict(obj)


class MongoManager(MicroserviceDatabaseManager):
    """
    Database manager for a MongoDB database.
    """

    def __init__(self, config: configparser.ConfigParser | None = None):
        super().__init__(config)

    def get_database(self) -> Mongo:
        return Mongo(config=self.config)

    @classmethod
    def get_environment_updates(cls) -> dict[str, str]:
        """
        Returns any environment variables that need to be given to the mongo docker container.

        :return: a dictionary of environment variable names to values.
        """
        result = super().get_environment_updates()
        result['MONGO_DB'] = 'hea'
        return result

    @classmethod
    def database_types(self) -> list[str]:
        return ['system|mongo']


class MongoContext(DatabaseContextManager[Mongo]): # Go into db package?
    """
    Provides a Mongo object.
    """

    async def connection(self) -> Mongo:
        return cast(Mongo, await _get_mongo(self.request, self.volume_id))


async def _get_mongo(request: web.Request, volume_id: Optional[str]) -> Mongo:
    """
    Gets a mongo client.

    :param request: the HTTP request (required).
    :param volume_id: the id string of a volume.
    :return: a Mongo client for the file system specified by the volume's file_system_name attribute. If no volume_id
    was provided, the return value will be the "default" Mongo client for the microservice found in the HEA_DB
    application-level property.
    :raise ValueError: if there is no volume with the provided volume id, the volume's file system does not exist,
    or a necessary service is not registered.
    """

    if volume_id is not None:
        file_system, credentials = await get_file_system_and_credentials_from_volume(request, volume_id, MongoDBFileSystem)
        if credentials is None:
            return Mongo(None, connection_string=file_system.connection_string)
        else:
            return Mongo(None, connection_string=file_system.connection_string, username=credentials.account, password=credentials.password)
    else:
        return request.app[HEA_DB]
