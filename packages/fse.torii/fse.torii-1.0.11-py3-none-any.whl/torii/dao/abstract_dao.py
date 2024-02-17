from datetime import datetime as dt

from bson import ObjectId
from pymongo import ASCENDING, DESCENDING


class AbstractDao:
    """
    This class offers the base MongoDB data access functionality.

    Any custom query function should use the helper methods to guarantee functionality.
    """

    PROHIBITED_TO_UPDATE = ['_id', 'location', 'creationDate', 'canEdit', 'canRemove']

    def find_one(self, collection, query: dict, include=[]) -> dict:
        """
        Find one document in collection.

        :param collection: Collection context.
        :param query: Query filter.
        :param include: List of keys to project in final result (removes all other keys from result).
        :return: The document if found, otherwise None.
        """
        query = self.prepare_query(query)

        return self.prepare_result(collection.find_one(query, projection=include))

    def find_many(self, collection, query,
                  filters={}, include=None, direction='ASC', sort=None, timeout=300, limit=0, start=0) -> list[dict]:
        """
        Find one or more documents in collection.

        :param collection: Collection context.
        :param query: Query filter.
        :param filters: Optional personalised filters.
        :param include: List of keys to project in final result (removes all other keys from result).
        :param direction: Orders the result as Ascending ('ASC') or Descending (any other value).
            Only applied if 'sort' is not None. Default 'ASC'.
        :param sort: Key to sort the result. Applies 'direction'.
        :param timeout: Time limit (in seconds) for the query operation to return a result.
        :param limit: Limit the number of documents returned by the query.
        :param start: The number of results to skip, therefore starting at a later part of the result.
        :return: List of dictionary documents.
        """
        query = self.prepare_query(query)
        query.update(self.prepare_filter(filters))

        cursor = collection.find(query, projection=include)
        if sort: cursor.sort(sort, ASCENDING if direction == 'ASC' else DESCENDING)
        cursor.skip(start)
        cursor.limit(limit)

        if timeout > 0: cursor.max_time_ms(timeout * 1000)

        return [self.prepare_result(document) for document in cursor]

    def count_documents(self, collection, filters, start=0, limit=0) -> int:
        """
        Count the number of documents returned by query.

        :param collection: Collection context.
        :param filters: Optional personalised filters.
        :param start: The number of results to skip, therefore starting at a later part of the result.
        :param limit: Limit the number of documents returned by the query.
        :return: Total number of documents found by query.
        """
        query = self.prepare_filter(filters)

        kwargs = {'filter': query}
        if start: kwargs['skip'] = start
        if limit: kwargs['limit'] = limit

        return collection.count_documents(**kwargs)

    def insert_one(self, collection, document: dict) -> dict:
        """
        Insert one document into the collection.

        :param collection: Collection context.
        :param document: JSON like document.
        :return: The given document.
        """
        doc = self.prepare_query(document)

        collection.insert_one(doc)

        return document

    def insert_many(self, collection, documents: list[dict]):
        """

        :param collection:
        :param documents:
        :return:
        """
        doc = [self.prepare_query(document) for document in documents]

        collection.insert_many(doc)

    def update_and_retrieve_one(self, collection, query: dict, document: dict, filters={}):
        """
        Update one document in collection.

        :param collection: Collection context.
        :param query: Query filter.
        :param document: JSON like document.
        :param filters: Optional personalised filters.
        :param retrieve: Retrieve updated document.
        :return: The document after the update if found, otherwise None.
        """
        query = self.prepare_query(query)
        query.update(self.prepare_filter(filters))
        document = self.prepare_update(document)

        return self.prepare_result(
                collection.find_one_and_update(filter=query, update={'$set': document}, return_document=True))

    def update_one(self, collection, query: dict, document: dict, filters={}):
        """
        Update one document in collection.

        :param collection: Collection context.
        :param query: Query filter.
        :param document: JSON like document.
        :param filters: Optional personalised filters.
        :param retrieve: Retrieve updated document.
        :return: The document after the update if found, otherwise None.
        """
        query = self.prepare_query(query)
        query.update(self.prepare_filter(filters))
        document = self.prepare_update(document)

        collection.update_one(filter=query, update={'$set': document})

    def delete_one(self, collection, query: dict, filters={}) -> None:
        """
        Delete one document in collection.

        :param collection: Collection context.
        :param query: Query filter.
        :param filters: Optional personalised filters.
        :return: None
        """
        query = self.prepare_query(query)
        query.update(self.prepare_filter(filters))

        collection.delete_one(query)

    def delete_many(self, collection, query: dict, filters={}) -> None:
        """
        Delete one or more documents in collection.

        :param collection: Collection context.
        :param query: Query filter.
        :param filters: Optional personalised filters.
        :return: None
        """
        query = self.prepare_query(query)
        query.update(self.prepare_filter(filters))

        collection.delete_many(query)

    @staticmethod
    def prepare_query(query: dict) -> dict:
        """
        Helper method.

        Guarantees the ID in the query/document is a MongoDB ObjectId.

        :param query: Query filter or JSON like document.
        :return: The modified query/document.
        """
        if '_id' in query and isinstance(query['_id'], str):
            query['_id'] = ObjectId(query['_id'])

        return query

    @staticmethod
    def prepare_filter(filters) -> dict:
        """
        Helper method.

        Turns the optional, personalised filters into a query compatible dictionary.

        :param filters: Optional personalised filters.
        :return: A query compatible dictionary.
        """
        query = {}

        if len(filters) == 1:
            item = filters[0]
            query = {
                item['property']:
                    item['value'] if item['operator'] == 'eq'
                    else {'$regex': item['value']} if item['operator'] == 'like'
                    else {f'${item["operator"]}': item['value']}
            }
        elif len(filters) > 1:
            query = {"$and": [
                {
                    item['property']:
                        item['value'] if item['operator'] == 'eq'
                        else {'$regex': item['value']} if item['operator'] == 'like'
                        else {f'${item["operator"]}': item['value']}
                }
                for item in filters
            ]}

        return query

    def prepare_update(self, document: dict):
        """
        Helper method.

        Removes any key in the given document that is prohibited from being updated by any User.
        Also adds/updates the 'modificationDate' value to reflect the new update.

        :param document: JSON like document.
        :return: The modified document.
        """
        [document.pop(key) for key in self.PROHIBITED_TO_UPDATE if key in document]

        document['modificationDate'] = int(dt.now().timestamp())

        return document

    @staticmethod
    def prepare_result(document):
        """
        Helper method.

        Prepares a MongoDB output result to be JSON compatible.

        :param document: JSON like document.
        :return: The modified document.
        """
        if not document:
            return document
        document['_id'] = str(document['_id'])
        return document

    @staticmethod
    def to_torii_object(document: dict):
        """
        Helper method.

        Prepares a document by converting all keys to String
        and adding all default elements expected from a ToriiObject.

        :param document: JSON like document.
        :return: The modified document with all default elements expected from a ToriiObject.
        """

        def convert_key_to_string(doc: dict):
            return {str(k): convert_key_to_string(i) if isinstance(i, dict) else i for k, i in doc.items()}

        doc = convert_key_to_string(document)

        return {
            'location': doc.pop('location') if 'location' in doc else 'main',
            'name': doc.pop('name') if 'name' in doc else '',
            'creationDate': doc.pop('creationDate') if 'creationDate' in doc else int(dt.now().timestamp()),
            'modificationDate': doc.pop('modificationDate') if 'modificationDate' in doc else int(dt.now().timestamp()),
            'description': doc.pop('description') if 'description' in doc else '',
            'wikiURI': doc.pop('wikiURI') if 'wikiURI' in doc else '',
            'tags': doc.pop('tags') if 'tags' in doc else [],
            'users': doc.pop('users') if 'users' in doc else [],
            'teams': doc.pop('teams') if 'teams' in doc else [],
            'projects': doc.pop('projects') if 'projects' in doc else [],
            'createdBy': doc.pop('createdBy') if 'createdBy' in doc else None,
            'content': doc
        }
