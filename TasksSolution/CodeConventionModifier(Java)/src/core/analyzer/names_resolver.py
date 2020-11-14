from collections import defaultdict
from ...core.utils.utils import NamesResolverError, setup_logger, FormatterType
from ...core.convention.convention_naming import get_convention_file_path
from ...core.tokenizer.java_lexer import restore_from_tokens
import copy, logging, os

logger = setup_logger(__name__, logging.DEBUG)
out_logger = setup_logger('renamed', logging.INFO, FormatterType.SHORT)

class LocalResolver(dict):
    def __init__(self, path, tokens, names, produce_file, p_resolver, r_resolver):
        self._path = path
        self._tokens = tokens
        self._renamed_tokens = names
        self._produce_file = produce_file
        self._p_resolver = p_resolver
        self._r_resolver = r_resolver
        self._pending = defaultdict(list)

    def _reset(self):
        self._path = None
        self._tokens = None
        self._renamed_tokens = None
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
        return self._renamed_tokens

    def close(self):
        """Closes current names resolver:
        1. Creates file with the given self._path;
        2. Produces new file structure from self._tokens and self._renamed_tokens;
        3. Removes current resolver from further consideration."""

        logger.debug('Closing local resolver({}) at "{}"'.format(id(self), self._path))
        logger.debug('{} local names found, {} pending names found'.format(
            super().__len__(), len(self._pending)))

        
        file_path = get_convention_file_path(self._path)
        out_logger.info('Renaming for file "{}"'.format(self._path).center(80, '-'))
        if self._path != file_path:
            out_logger.info('Renaming file: {} -> {}'.format(self._path, file_path))

        renamed_mask = [False for _ in range(len(self._renamed_tokens))]
        for cur_idx, (origin_idx, x) in enumerate(self._renamed_tokens):
            new_name, name = x.value, self._tokens[origin_idx].value
            if name != new_name:
                pos = self._tokens[origin_idx].position
                out_logger.info('Renaming at {}: {} -> {}'.format(pos, name, new_name))

        out_logger.info(''.center(80, '-'))

        if not self._produce_file:
            self._r_resolver._remove_local_resolver(self)
            self._reset()
            return

        output_str = restore_from_tokens(self._tokens, self._renamed_tokens)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, "w") as f:
            f.write(output_str)

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

    def new_local_resolver(self, path, tokens, names, produce_file):
        obj = LocalResolver(path, tokens, names, produce_file, self._g_resolver, self)

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

    def _add_renaming(self, type, name, stack):
        f_resolver = self.names_resolver.get_local_resolver(self.uuid)
        g_resolver = self.names_resolver.get_global_resolver()

        if name in g_resolver:
            return

        new_name = get_convention_rename(type, name)
        #if name == new_name:
        #    return

        if stack[-1].value == '' and type == NameType.CLASS:
            # Process globals
            g_resolver[name] = new_name
            print(type, name, new_name)

        elif (len(stack) == 3 and stack[-1].value == '{'
              and stack[-2].value in ('class', 'interface')
                and type != NameType.NAME):

            # Process globals
            g_resolver[name] = new_name
            print(type, name, new_name)

        else:
            if name in f_resolver: return

            # Process locals
            f_resolver[name] = new_name
            print(type, name, new_name)



