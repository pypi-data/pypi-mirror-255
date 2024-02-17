import logging

from pymongo import ASCENDING

from torii.dao.abstract_dao import AbstractDao
from torii.decorators.route_registry import RouteRegistry
from torii.exception import ToriiException


class BusinessObjectDao(AbstractDao):

    registry = RouteRegistry()

    def __init__(self, torii):
        self.torii_bo = torii.mongo_database_torii_bo
        self._torii = torii
        self._logger = logging.getLogger('torii')

    def init(self, intent: str, actions: str, *args, **kwargs):
        try:
            return self.registry.call_method(self, intent, actions, *args, **kwargs)
        except Exception as e:
            # raise ToriiException(f"Error in BusinessObjectDao: {e}")
            raise e

    # ===============
    # GET METHODS
    # ===============

    @registry.register('GET', '')
    def get_classes(self, explore=False):
        return self.torii_bo.list_collection_names()

    @registry.register('GET', '{boClass}')
    def get_documents(self, boClass, dir='ASC', sort=None, timeout=300, limit=0,
                      start=0, filter={}, include=[], raw=False):
        collection = self.torii_bo.get_collection(boClass)
        has_permission, reason = self._torii.user_manager.check_user_permission(collection)

        result = self.find_many(collection, filter, include, dir, sort, timeout, limit, start)

        if not has_permission:
            result = self._torii.user_manager.remove_no_access_documents(result)

        return result

    @registry.register('GET', '{boClass}/{id}')
    def get_document(self, boClass, id, include=[]):
        collection = self.torii_bo.get_collection(boClass)
        has_permission, reason = self._torii.user_manager.check_user_permission(collection)

        result = self.find_one(collection, {'_id': id}, include)

        return self._torii.user_manager.check_team_access(result) if not has_permission else result

    @registry.register('GET', '{boClass}/page')
    def get_paged_documents(self, boClass, dir='ASC', sort=None, timeout=300, limit=0,
                            start=0, filter={}, include=[], count=True, raw=False):
        collection = self.torii_bo.get_collection(boClass)
        has_permission, reason = self._torii.user_manager.check_user_permission(collection)

        result = {'result': self.find_many(collection, {}, filter, include, dir, sort, timeout, limit, start)}

        if not has_permission:
            result['result'] = self._torii.user_manager.remove_no_access_documents(result['result'])

        if count:
            result['size'] = len(result['result']) if not has_permission \
                else self.count_documents(collection, filter, start, limit)

        return result

    @registry.register('GET', '{boClass}/count')
    def count(self, boClass, timeout=300, filter={}):
        collection = self.torii_bo.get_collection(boClass)
        has_permission, reason = self._torii.user_manager.check_user_permission(collection)
        if not has_permission: raise ToriiException(reason)

        return self.count_documents(collection, filter)

    @registry.register('GET', '{boClass}/search/{searchedText}')
    def get_searched_objects(self, boClass, searchedText, start=0, limit=5):
        collection = self.torii_bo.get_collection(boClass)
        has_permission, reason = self._torii.user_manager.check_user_permission(collection)

        result = self.find_many(collection, {'$text': {'$search': searchedText}}, start=start, limit=limit)

        if not has_permission:
            result = self._torii.user_manager.remove_no_access_documents(result)

        return result

    @registry.register('GET', '{boClass}/distinct/{property}')
    def distinct(self, boClass, property, limit=100, filter={}, stats=None):
        """ TODO: Needs tests. Unknown if works as intended. """
        collection = self.torii_bo.get_collection(boClass)
        has_permission, reason = self._torii.user_manager.check_user_permission(collection)

        query = self.prepare_filter(filter)

        cursor = collection.find(query)
        cursor.limit(limit)
        cursor.distinct(property)

        if not has_permission:
            return self._torii.user_manager.remove_no_access_documents(list(cursor))

        return list(cursor)

    # ===============
    # POST METHODS
    # ===============

    @registry.register('POST', '{boClass}')
    def create_document(self, boClass, bo=None):
        collection = self.torii_bo.get_collection(boClass)
        has_permission, reason = self._torii.user_manager.check_user_permission(collection, read=False, write=True)
        if not has_permission: raise ToriiException(reason)

        return self.insert_one(collection, self.to_torii_object(bo))

    @registry.register('POST', '{boClass}/{id}')
    def update_document(self, boClass, id, bo=None):
        collection = self.torii_bo.get_collection(boClass)
        has_permission, reason = self._torii.user_manager.check_user_permission(collection, write=True)
        if not has_permission: raise ToriiException(reason)

        return self.update_and_retrieve_one(collection, {'_id': id}, bo)

    @registry.register('POST', '{boClass}/bulk')
    def create_documents(self, boClass, bos=None):
        collection = self.torii_bo.get_collection(boClass)
        has_permission, reason = self._torii.user_manager.check_user_permission(collection, read=False, write=True)
        if not has_permission: raise ToriiException(reason)

        self.insert_many(collection, [self.to_torii_object(bo) for bo in bos])

        return True

    # ===============
    # PUT METHODS
    # ===============

    @registry.register('PUT', '{boClass}/bulk')
    def update_documents(self, boClass, bos=None, retrieve=False):
        collection = self.torii_bo.get_collection(boClass)
        has_permission, reason = self._torii.user_manager.check_user_permission(collection, write=True)
        if not has_permission: raise ToriiException(reason)

        if not bos: return []

        updated_bos = []
        if retrieve:
            for bo in bos:
                updated_bos.append(self.update_and_retrieve_one(collection, {'_id': bo['_id']}, bo))
        else:
            for bo in bos:
                self.update_one(collection, {'_id': bo['_id']}, bo)

        return updated_bos

    @registry.register('PUT', '{boClass}/index')
    def create_index(self, boClass, fields=None, default=False, unique=False):
        """ TODO: Needs tests. Unknown if works as intended. """
        collection = self.torii_bo.get_collection(boClass)
        has_permission, reason = self._torii.user_manager.check_user_permission(collection, write=True)
        if not has_permission: raise ToriiException(reason)

        if default:
            collection.create_index([('_id', ASCENDING), ('location', ASCENDING)], unique=True)

        if fields:
            collection.create_index([(item, ASCENDING) for item in fields], unique=unique)

        return True

    # ===============
    # DELETE METHODS
    # ===============

    @registry.register('DELETE', '{boClass}')
    def delete_conditional(self, boClass, filter={}, force=False):
        collection = self.torii_bo.get_collection(boClass)
        has_permission, reason = self._torii.user_manager.check_user_permission(collection, read=False, write=True)
        if not has_permission: raise ToriiException(reason)

        self.delete_many(collection, {}, filter)

        return True

    @registry.register('DELETE', '{boClass}/{id}')
    def delete_document(self, boClass, id, force=False):
        collection = self.torii_bo.get_collection(boClass)
        has_permission, reason = self._torii.user_manager.check_user_permission(collection, read=False, write=True)
        if not has_permission: raise ToriiException(reason)

        self.delete_one(collection, {'_id': id})

        return True

    @registry.register('DELETE', '{boClass}/clear/{dataset}')
    def delete_dataset(self, boClass, dataset):
        collection = self.torii_bo.get_collection(boClass)
        has_permission, reason = self._torii.user_manager.check_user_permission(collection, read=False, write=True)
        if not has_permission: raise ToriiException(reason)

        self.delete_many(collection, {'content.dataset': dataset})

        return True

    # ===============
    # PATCH METHODS
    # ===============

    @registry.register('PATCH', '{boClass}')
    def patch_documents(self, boClass, patchOperations=None, retrieve=False):
        collection = self.torii_bo.get_collection(boClass)
        has_permission, reason = self._torii.user_manager.check_user_permission(collection, write=True)
        if not has_permission: raise ToriiException(reason)

        updated_bos = []

        for action in patchOperations:
            obj_id = action['id']
            operation = action['op']
            key = action['key']
            value = action['value']

            if operation == 'replace':
                updated_bos.append(self.update_and_retrieve_one(collection, {'_id': obj_id}, {key: value}))
            else:
                raise ToriiException(f"Patch operation not supported: {operation}")

        return updated_bos if retrieve else []

    @registry.register('PATCH', '{boClass}/{id}')
    def patch_document(self, boClass, id, patchOperations=None):
        collection = self.torii_bo.get_collection(boClass)
        has_permission, reason = self._torii.user_manager.check_user_permission(collection, write=True)
        if not has_permission: raise ToriiException(reason)

        for action in patchOperations:
            operation = action['op']
            key = action['key']
            value = action['value']

            if operation == 'replace':
                self.update_one(collection, {'_id': id}, {key: value})
            else:
                raise ToriiException(f"Patch operation not supported: {operation}")

        return True

    @registry.register('PATCH', '{boClass}/bulk')
    def patch_documents_with_filter(self, boClass, patchOperations=None, filter={}):
        collection = self.torii_bo.get_collection(boClass)
        has_permission, reason = self._torii.user_manager.check_user_permission(collection, write=True)
        if not has_permission: raise ToriiException(reason)

        for action in patchOperations:
            obj_id = action['id']
            operation = action['op']
            key = action['key']
            value = action['value']

            if operation == 'replace':
                self.update_one(collection, {'_id': obj_id}, {key: value}, filter)
            else:
                raise ToriiException(f"Patch operation not supported: {operation}")

        return True
