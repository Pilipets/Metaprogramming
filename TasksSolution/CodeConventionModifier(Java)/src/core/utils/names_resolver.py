from collections import defaultdict
from .utils import NamesResolverError, setup_logger
import copy, logging, os

logger = setup_logger(__name__, logging.DEBUG)

class LocalResolver(dict):
    def __init__(self, path, tokens, names, p_resolver, r_resolver):
        self._path = path
        self._tokens = tokens
        self._names = names
        self._p_resolver = p_resolver
        self._r_resolver = r_resolver
        self._pending = defaultdict(list)

    def _reset(self):
        self._path = None
        self._tokens = None
        self._names = None
        self._p_resolver = None
        self._r_resolver = None

    def add_pending(self, token):
        self._pending[token.value].append(token)
        self._p_resolver.add_pending(token.value, self)

    def process_pending(self, name, new_name):
        for x in self._pending.get(name, []):
            x.value = new_name
        del self._pending[name]

        if len(self._pending) == 0:
            self.close()

    def is_pending(self):
        return len(self._pending) > 0

    def get_pending_count(self):
        return len(self._pending)

    def get_pending(self):
        return self._pending.keys()

    def get_names(self):
        return self._names

    def close(self):
        """Closes current names resolver:
        1. Creates file with the given self._path;
        2. Produces new file structure from self._tokens and self._names;
        3. Removes current resolver from further consideration."""

        logger.debug('Closing local resolver({})'.format(id(self)))
        logger.debug('{} local names found, {} pending names found'.format(
            super().__len__(), len(self._pending)))

        #output = 
        #os.makedirs(os.path.dirname(self._path), exist_ok=True)
        #with open(filename, "w") as f:
        #    f.write("FOOBAR")

        self._r_resolver._remove_local_resolver(self)
        self._reset()

class GlobalResolver(dict):
    def __init__(self, r_resolver):
        self._pending = defaultdict(list)
        self._r_resolver = r_resolver

    def _reset(self):
        self._pending = defaultdict(list)
        self._r_resolver = None

    def __setitem__(self, name, new_name):
        if name in self._pending:
            for unit in self._pending.get(name, []):
                unit.process_pending(name, new_name)
            del self._pending[name]

        super().__setitem__(name, new_name)

    def add_pending(self, name, unit):
        self._pending[name].append(unit)

    def is_pending(self):
        return len(self._pending) > 0

    def close(self):
        logger.debug('Closing global resolver({})'.format(id(self)))
        logger.debug('{} global names found, {} pending names found'.format(
            super().__len__(), len(self._pending)))

        self._reset()

class NamesResolver:
    def __init__(self):
        self._g_resolver = GlobalResolver(self)
        self._resolvers = {}

    def _reset(self):
        self._g_resolver = None
        self._resolvers = {}

    def new_local_resolver(self, path, tokens, names):
        obj = LocalResolver(path, tokens, names, self._g_resolver, self)

        uuid = id(obj)
        self._resolvers[uuid] = obj
        return uuid

    def get_local_resolver(self, uuid):
        return self._resolvers.get(uuid, None)

    def get_global_resolver(self):
        return self._g_resolver

    def close_all_resolvers(self):
        logger.debug('{} resolvers left, closing all now...'.format(len(self._resolvers)))
        for unit in list(self._resolvers.values()):
            unit.close()

        self._g_resolver.close()
        self._reset()

    def _remove_local_resolver(self, resolver):
        '''Closes the resolver specified by uuid, expects resolver not being pending'''
        del self._resolvers[id(resolver)]



