from collections import defaultdict

from .resolvers.global_resolver import GlobalNamesResolver
from .resolvers.file_resolver import FileResolver

class NamesResolver:
    def _reset(self):
        self._g_resolver = None
        self._file_resolvers = {}
        self._pending = defaultdict(list)

    def __init__(self):
        self._g_resolver = GlobalNamesResolver(self)
        self._file_resolvers = {}
        self._pending = defaultdict(list)

    # ----------------------SLOTS----------------------------
    def slot_global_name_added(self, name, new_name):
        if name in self._pending:
            for unit in self._pending.get(name, []):
                unit.slot_global_name_added(name, new_name)
            del self._pending[name]

    def slot_child_pending_on(self, name, ins):
        self._pending[name].append(ins)

    def slot_child_closed(self, ins):
        del self._file_resolvers[id(ins)]

    # ---------------------INTERFACE---------------------------
    def get_file_resolver(self, uuid):
        return self._file_resolvers.get(uuid, None)

    def new_file_resolver(self, path, tokens,
                          changed_tokens, produce_file,
                          touch_docs):

        obj = FileResolver(self, self._g_resolver,
                           path, tokens, changed_tokens,
                           produce_file, touch_docs)

        uuid = id(obj)
        self._file_resolvers[uuid] = obj
        return obj

    def close_all_resolvers(self):
        for unit in list(self._file_resolvers.values()):
            unit.close()

        self._g_resolver.close()
        self._reset()

    # -----------------------------------------------------------     
