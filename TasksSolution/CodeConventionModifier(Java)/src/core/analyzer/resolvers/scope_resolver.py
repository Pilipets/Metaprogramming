from collections import defaultdict

from ...utils.utils import out_logger

class ScopeNamesResolver(dict):
    def _reset(self):
        self._p_resolver = None
        self._g_resolver = None
        self._tokens = []
        self._changed_named_tokens = []

        self._pending = defaultdict(list)

    def __init__(self, p_resolver, g_resolver,
                 tokens, changed_named_tokens):

        self._p_resolver = p_resolver
        self._g_resolver = g_resolver
        self._tokens = tokens
        self._changed_named_tokens = changed_named_tokens

        self._pending = defaultdict(list)

    # --------------------------PRIVATE------------------------------
    def _add_pending(self, token):
        name_present = self._pending.get(token.value, None) is not None
        self._pending[token.value].append(token)

        if name_present: return
        self._p_resolver.slot_child_pending_on(token.value, self)

    # --------------------------SLOTS-----------------------------------
    def slot_global_name_added(self, name, new_name):
        for x in self._pending.get(name, []): x.value = new_name
        del self._pending[name]

        return len(self._pending) == 0

    # ------------------------INTERFACE-----------------------------------
    def process_postpone_renamings(self):
        for idx, x in self._changed_named_tokens:
            name = x.value
            if name in self:
                x.value = self[name]

            elif name in self._g_resolver:
                x.value = self._g_resolver[name]

            # Store for post processing - will be resolved on the fly
            else:
                self._add_pending(x)

        return len(self._pending) == 0

    def close(self):
        changed_named_idx = []
        for origin_idx, x in self._changed_named_tokens:
            new_name, name = x.value, self._tokens[origin_idx].value
            if name != new_name:
                changed_named_idx.append(origin_idx)
                out_logger.info('Renaming at {}: {} -> {}'.format(
                    self._tokens[origin_idx].position, name, new_name))

        self._reset()
        # Needed for later input restoring
        return changed_named_idx
    # -------------------------------------------------------------------
        

