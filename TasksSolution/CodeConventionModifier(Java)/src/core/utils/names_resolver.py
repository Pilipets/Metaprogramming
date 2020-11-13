from collections import defaultdict

class NamesResolver:
    class NamesUnit:
        def __init__(self):
            self.tokens = []

        def add_tokens(self, tokens : list):
            self.tokens = tokens

    def __init__(self):
        self.path = ''

        self.unit_idx = 0
        self.map = defaultdict(NamesResolver.NamesUnit)

    @property
    def idx(self):
        return (self.unit_idx, self.scope_idx)

    def add_tokens(self, tokens : list):
       self.map[self.unit_idx].add_tokens(tokens)

    def add_declaration(self, name : str, new_name : str):
        pass

    def add_unit(self):
        self.unit_idx += 1

    def pop_unit(self):
        self.unit_idx -= 1
