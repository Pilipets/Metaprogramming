import copy, logging

from .tokenizer import java_lexer
from .tokenizer.java_lexer import tokenize
from .utils.convention_naming import NameType, get_convention_rename, get_convention_file_path
from .utils.structures_consumer import StructuresConsumer
from .utils.names_resolver import NamesResolver
from .utils.utils import setup_logger, ModifierError

# Initialize logging
core_logger = setup_logger(__name__, logging.DEBUG)

# Not thread safe
class JavaModifierCore:
    def _reset(self):
        self.names_resolver = None
        self.stack = None
        self.idx = -1
        self.pre, self.cur = None, None
        self.uuid = None

    def __init__(self):
        self._reset()

    def initialize_modify(self):
        core_logger.debug('Initializing modify...'.center(60, '-'))
        self.names_resolver = NamesResolver()

    def modify_one(self, file_path, text):
        # Aliases
        names_resolver = self.names_resolver
        tokens = tuple(tokenize(text, raise_errors=True))

        # Preprocessing part
        names = [(idx, copy.copy(x)) for idx, x in enumerate(tokens) if isinstance(x, java_lexer.Identifier)]
        file_path = get_convention_file_path(file_path)
        self.uuid = names_resolver.new_local_resolver(file_path, tokens, names)
        self.stack = [java_lexer.JavaToken('')]
        self.idx = 0
        self.pre, self.cur = None, None

        # Analyzing part
        core_logger.debug(f'Analyzing "{file_path}"'.center(60, '-'))
        while self.idx < len(tokens):
            self.cur = tokens[self.idx]

            # process tokens
            if isinstance(self.cur, java_lexer.Identifier):
                self._process_identifier(tokens)

            elif isinstance(self.cur, java_lexer.SimpleType):
                self._process_simple_type(tokens)

            elif isinstance(self.cur, java_lexer.Keyword):
                self._process_keyword(tokens)

            elif isinstance(self.cur, java_lexer.Separator):
                self._process_separator(tokens)

            self.pre = tokens[self.idx]
            self.idx += 1

        # Renaming part
        core_logger.debug(f'Renaming for "{file_path}"'.center(60, '-'))
        f_resolver = names_resolver.get_local_resolver(self.uuid)
        g_resolver = names_resolver.get_global_resolver()

        res_names = f_resolver.get_names()
        for idx, x in res_names:
            name = x.value
            if name in f_resolver:
                x.value = f_resolver[name]

            elif name in g_resolver:
                x.value = g_resolver[name]

            # Store for post_processing - will be resolved on the fly
            else:
                f_resolver.add_pending(x)

            print(name, x.value)

        if f_resolver.is_pending():
            cnt = f_resolver.get_pending_count()
            core_logger.debug(
                '{} name conflicts encountered: {}'.format(
                    cnt,
                    ', '.join((x for x in f_resolver.get_pending()))
            ))
            core_logger.debug(f'Postponing renaming for "{file_path}"')

        else:
            names_resolver.close_resolver(self.uuid)

    def finalize_modify(self):
        core_logger.debug('Finalizing modify...'.center(60, '-'))

        self.names_resolver.close_all_resolvers()
        self._reset()

    def _add_renaming(self, type, name):

        stack = self.stack
        f_resolver = self.names_resolver.get_local_resolver(self.uuid)
        g_resolver = self.names_resolver.get_global_resolver()

        if name in (g_resolver):
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

    def _process_separator(self, tokens):
        cur = self.cur
        stack = self.stack

        if cur.value == '{':
            stack.append(cur)

        elif cur.value == '}':
            if stack[-1].value == '{':
                if (len(stack) > 2 and stack[-2].value in ('class', 'interface')):
                    stack.pop() # {
                    stack.pop() # class

                else:
                    stack.pop()

        elif cur.value == '(':
            stack.append(cur)

        elif cur.value == ')':
            if stack[-1].value == '(':
                stack.pop()

    def _process_keyword(self, tokens):
        idx, cur = self.idx, self.cur
        stack = self.stack

        # void
        if cur.value == 'void':
            if StructuresConsumer.try_void_method_declaration(idx, tokens, False):
                res = StructuresConsumer.get_consume_res()
                core_logger.debug('Method declaration: ({}) ({})'.format(res[0], res[1]))
                
                self._add_renaming(NameType.METHOD, res[1].value)
                self.idx = res[-1] - 1

        elif cur.value in ('class', 'interface'):
            if StructuresConsumer.try_class_declaration(idx, tokens, False):
                res = StructuresConsumer.get_consume_res()
                core_logger.debug('Class: ({})'.format(res[0]))

                self._add_renaming(NameType.CLASS, res[0].value)
                stack.append(cur)
                self.idx = res[-1] - 1

        elif (len(stack) > 2 and stack[-1].value == '{'
                and stack[-2].value in ('class', 'interface')):

            if StructuresConsumer.try_class_const_declaration(idx, tokens):
                res = StructuresConsumer.get_consume_res()
                core_logger.debug('Const: ({}) ({})'.format(res[0], res[1]))

                self._add_renaming(NameType.CONST_VARIABLE, res[1].value)
                self.idx = res[-1] - 1

    def _process_simple_type(self, tokens):
        idx = self.idx

        if StructuresConsumer.try_simple_method_declaration(idx, tokens, False):
            res = StructuresConsumer.get_consume_res()
            core_logger.debug('Method declaration: ({}) ({})'.format(res[0], res[1]))

            self._add_renaming(NameType.METHOD, res[1].value)
            self.idx = res[-1] - 1

        elif StructuresConsumer.try_var_declaration(idx, tokens):
            res = StructuresConsumer.get_consume_res()
            core_logger.debug('Variable declaration: ({}) ({})'.format(res[0], res[1]))

            self._add_renaming(NameType.VARIABLE, res[1].value)
            self.idx = res[-1] - 1

    def _process_identifier(self, tokens : list):
        cur = self.cur

        if StructuresConsumer.try_var_declaration(self.idx, tokens, False):
            # Name declaration found
            res = StructuresConsumer.get_consume_res()
            end = res[-1]

            # Try method declaration first
            if (end < len(tokens) and tokens[end].value == '('):
                core_logger.debug('Method declaration: ({}) ({})'.format(res[0], res[1]))

                self._add_renaming(NameType.METHOD, res[1].value)
                self.idx = end

            # Method declaration not found, proceed with variable
            else: 
                core_logger.debug('Variable declaration: ({}) ({})'.format(res[0], res[1]))

                self._add_renaming(NameType.VARIABLE, res[1].value)
                self.idx = end-1

        else:
            core_logger.debug('Name encountered: ({})'.format(cur))

            #self._add_renaming(NameType.NAME, cur.value)