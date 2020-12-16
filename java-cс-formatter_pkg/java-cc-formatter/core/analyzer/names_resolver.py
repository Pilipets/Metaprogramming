from .resolvers.global_resolver import GlobalNamesResolver
from .resolvers.file_resolver import FileResolver

class NamesResolver:
    def __init__(self):
        self._g_resolver = GlobalNamesResolver(self)

    # ---------------------INTERFACE---------------------------
    def get_global_resolver(self):
        return self._g_resolver

    def new_file_resolver(self, path, tokens,
                          produce_file, touch_docs):

        return FileResolver(self, self._g_resolver,
                            path, tokens,
                            produce_file, touch_docs)

    def close(self):
        self._g_resolver.close()
