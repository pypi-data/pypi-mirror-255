import logging

from torii.dao.business_object_dao import BusinessObjectDao


class DaoManager:
    """
    The manager for all data access objects (DAOs).

    All DAOs should be mapped to the 'services' dictionary, where the Key is the
    first element in the REST API path and the value the uninitialized DAO class.
    """

    # Due to Azure Functions using Shared State between requests (object caching),
    # and to make use of this Azure optimization,
    # we need to test if cls was already initialized by checking the instance,
    # otherwise it will throw "TypeError: class object is not callable"
    services = {
        'bo': {'cls': BusinessObjectDao, 'type': BusinessObjectDao},
    }

    def __init__(self, torii):
        self._torii = torii
        self._logger = logging.getLogger('torii')

        for key, bo in self.services.items():
            # If class is not instantiated, then initialize it
            if not isinstance(self.services[key]['cls'], self.services[key]['type']):
                self.services[key]['cls'] = self.services[key]['cls'](torii)

    def run_service(self, intent: str, path: str, params=None, json=None, data=None, files=None, timeout=None):
        """
        Runs the intended service corresponding to the given intent and path.
        Passes the defined arguments to the service.

        :param intent: The Http method (GET, POST, PUT, DELETE or PATCH).
        :param path: The REST API path (ex.: bo/{boClass}/page).
        :param params: Optional keyword argument.
        :param json: Optional argument.
        :param data: Optional argument.
        :param files: Optional argument.
        :param timeout: Optional argument.
        :returns: The class method if exists, otherwise None.
        """

        if not self._torii.properties['use_python_dao']:
            return None

        path = path.split('/')
        service = path.pop(0)

        if service not in self.services:
            return None

        args = [intent, '/'.join(path)]
        if json: args.append(json)
        if data: args.append(data)
        if files: args.append(files)
        if timeout: args.append(timeout)
        kwargs = params or {}

        try:
            return self.services[service]['cls'].init(*args, **kwargs)
        except Exception as e:
            self._logger.info('Error in DAO Manager run_service:', e)
            raise e
