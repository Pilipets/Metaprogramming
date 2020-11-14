from collections import defaultdict
from .utils import NamesResolverError

class LocalUnit(dict):
    def __init__(self, path, parent):
        self._path = path
        self._parent = parent
        self._pending = defaultdict(list)

    def add_pending(self, token):
        self._pending[token.value].append(token)
        self._parent.add_pending(token.value, self)

    def process_pending(self, name, new_name):
        for x in self._pending.get(name, []):
            x.value = new_name
        del self._pending[name]

        if len(self._pending) == 0:
            # Finished pending for this file
            pass

    def is_pending(self):
        return len(self._pending) > 0

    def get_pending_count(self):
        return len(self._pending)

    def get_pending(self):
        return self._pending.keys()

class GlobalUnit(dict):
    def __init__(self):
        self._pending = defaultdict(list)

    def __setitem__(self, name, new_name):
        if name in self._pending:
            for unit in self._pending.get(name, []):
                unit.process_pending(name, new_name)
            del self.pending[name]

        super().__setitem__(name, new_name)

    def add_pending(self, name, unit):
        self._pending[name].append(unit)

    def is_pending(self):
        return len(self._pending) > 0

class NamesResolver:
    def __init__(self):
        self._global_unit = GlobalUnit()
        self._local_units = {}

    def new_file_resolver(self, path):
        obj = LocalUnit(path, self._global_unit)
        uuid = id(obj)

        self._local_units[uuid] = obj
        return uuid

    def get_file_resolver(self, uuid):
        return self._local_units.get(uuid, None)

    def remove_file_resolver(self, uuid):
        unit = self._local_units.get(uuid, None)
        if not unit: return True
        if unit.is_pending():
            raise NamesResolverError(
                'Unable to remove unit({}): {} pending names found'.format(
                    uuid, unit.pending_count()))
        del self._local_units[uuid]
        return True

    def get_global_resolver(self):
        return self._global_unit

    def is_pending(self):
        return self._global_unit.is_pending()

