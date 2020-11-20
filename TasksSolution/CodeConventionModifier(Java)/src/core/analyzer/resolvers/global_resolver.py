class GlobalNamesResolver(dict):
    def __init__(self, root):
        self._root = root

    def _reset(self):
        self._root = None

    def __setitem__(self, name, new_name):
        self._root.slot_global_name_added(name, new_name)
        super().__setitem__(name, new_name)

    def close(self):
        self._reset()
