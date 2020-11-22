from collections import defaultdict

from ...utils.utils import out_logger

class ScopeNamesResolver(dict):
    def _reset(self):
        self._g_resolver = None
        self._changed_named_tokens = []
        super().clear()

    def __init__(self, g_resolver, changed_named_tokens):
        self._g_resolver = g_resolver
        self._changed_named_tokens = changed_named_tokens

    def close(self):
        changed_named_idx = []
        pending = []
        for _, x in self._changed_named_tokens:
            name = x.value
            if name in self:
                x.value = self[name]

            elif name in self._g_resolver:
                x.value = self._g_resolver[name]

            else:
                pending.append(name)
                continue

            if name != x.value:
                out_logger.info('Renaming at {}: {} -> {}'.format(
                    x.position, name, x.value))

        if pending:
            out_logger.info('{} names left untouched: {}'.format(
                len(pending), pending))

        self._reset()
        return changed_named_idx
        

