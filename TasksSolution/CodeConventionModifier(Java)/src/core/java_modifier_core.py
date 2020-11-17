import copy, logging

from .tokenizer import java_lexer
from .tokenizer.java_lexer import tokenize
from .convention.convention_naming import NameType
from .analyzer.advanced_consumer import AdvancedStructuresConsumer as Consumer
from .analyzer.names_resolver import NamesResolver
from .utils.utils import setup_logger, ModifierError

# Initialize logging
core_logger = setup_logger(__name__, logging.DEBUG)

# Not thread safe
class JavaModifierCore:
    def __init__(self):
        self._reset()

    def initialize(self):
        core_logger.debug('Initializing modify...'.center(60, '-'))

        self.names_resolver = NamesResolver()
        self.consumer = Consumer()

    def verify_one(self, file_path, text):
        self.modify_one(file_path, text, produce_file = False)

    def modify_one(self, file_path, text, produce_file = True):
        # Preprocessing part
        self._initialize_one(file_path, text, produce_file)

        #Aliases
        tokens = self.tokens
        stack = self.stack

        # Analyzing part
        core_logger.debug(f'Analyzing "{file_path}"'.center(60, '-'))
        while self.idx < len(tokens):
            self.cur = tokens[self.idx]

            if isinstance(self.cur, java_lexer.Identifier):
                self._process_identifier()

            elif isinstance(self.cur, java_lexer.SimpleType):
                self._process_simple_type()

            elif isinstance(self.cur, java_lexer.Keyword):
                self._process_keyword()

            elif isinstance(self.cur, java_lexer.Separator):
                self._process_separator()

            elif isinstance(self.cur, java_lexer.Operator):
                self._process_operator()

            self.pre = tokens[self.idx]
            self.idx += 1

        # Renaming part
        self._finalize_one(file_path)

    def finalize(self):
        core_logger.debug('Finalizing modify...'.center(60, '-'))

        self.names_resolver.close_all_resolvers()
        self._reset()

    def _reset(self):
        self.names_resolver = None
        self.consumer = None
        self.tokens = None
        self.stack = None
        self.idx = -1
        self.pre, self.cur = None, None
        self.uuid = None

    def _initialize_one(self, file_path, text, produce_file):
        tokens = tuple(tokenize(text, raise_errors=True))
        names = [(idx, copy.copy(x)) for idx, x in enumerate(tokens) if isinstance(x, java_lexer.Identifier)]

        self.tokens = tokens
        self.uuid = self.names_resolver.new_local_resolver(file_path, tokens, names, produce_file)
        self.stack = [java_lexer.JavaToken('')]
        self.idx = 0
        self.pre, self.cur = None, None

    def _finalize_one(self, file_path):
        core_logger.debug(f'Renaming for "{file_path}"'.center(60, '-'))

        if len(self.stack) != 1:
            raise ModifierError('Invalid Java code semantics encountered, stack size:', len(self.stack))

        names_resolver = self.names_resolver
        f_resolver = names_resolver.get_local_resolver(self.uuid)
        g_resolver = names_resolver.get_global_resolver()

        renames = f_resolver.get_renames()
        for idx, x in renames:
            name = x.value
            if name in f_resolver:
                x.value = f_resolver[name]

            elif name in g_resolver:
                x.value = g_resolver[name]

            # Store for post processing - will be resolved on the fly
            else:
                f_resolver.add_pending(x)

        if f_resolver.is_pending():
            cnt = f_resolver.get_pending_count()
            core_logger.debug(
                '{} name conflicts encountered: {}'.format(
                    cnt, ', '.join((x for x in f_resolver.get_pending()))
            ))
            core_logger.debug(f'Postponing renaming for "{file_path}"')

        else:
            f_resolver.close()

    def _process_operator(self):
        idx = self.idx
        tokens, consumer = self.tokens, self.consumer
        stack, names_resolver = self.stack, self.names_resolver

        # Starting with generics method without preceding keywords
        if consumer.try_method_declaration(idx, tokens):
            method, idx = consumer.get_consume_res()

            core_logger.debug('Method declaration: {}'.format(method))

            names_resolver._add_declaration(
                self.uuid, NameType.METHOD, method, stack)

            self.idx = idx - 1

    def _process_separator(self):
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

    def _process_keyword(self):
        idx = self.idx
        tokens, consumer = self.tokens, self.consumer
        stack, names_resolver = self.stack, self.names_resolver

        # we know at least 1 keyword would be there
        consumer.try_keywords(idx, tokens)
        keywords, idx = consumer.get_consume_res()
        
        # Previous is either class or interface
        if consumer.try_class_declaration(idx-1, tokens):
            start_token = tokens[idx-1]
            cls, idx = consumer.get_consume_res()
            core_logger.debug('Class declaration: {}'.format(cls))
            names_resolver._add_declaration(
                self.uuid, NameType.CLASS , cls, stack)

            stack.append(start_token)

        # Previous is void or next is method
        elif (consumer.try_method_declaration(idx-1, tokens)
                or consumer.try_method_declaration(idx, tokens)):
            method, idx = consumer.get_consume_res()
            core_logger.debug('Method declaration: {}'.format(method))
            names_resolver._add_declaration(
                self.uuid, NameType.METHOD, method, stack)

        # Multiple vars
        elif consumer.try_multiple_vars_declaration(idx, tokens):
            vars, idx = consumer.get_consume_res()

            if 'static' in keywords and 'final' in keywords:
                core_logger.debug('Const vars declaration: {}'.format(vars))
                names_resolver._add_declaration(
                    self.uuid, NameType.CONST_VARIABLE, vars, stack)
            
            else:
                core_logger.debug('Vars declaration: {}'.format(vars))
                names_resolver._add_declaration(
                    self.uuid, NameType.VARIABLE, vars, stack)

        self.idx = idx - 1

    def _process_simple_type(self):
        idx = self.idx
        tokens, consumer = self.tokens, self.consumer
        stack, names_resolver = self.stack, self.names_resolver

        # Without preceding keywords
        if consumer.try_method_declaration(idx, tokens):
            method, idx = consumer.get_consume_res()
            core_logger.debug('Method declaration: {}'.format(method))
            names_resolver._add_declaration(
                self.uuid, NameType.METHOD, method, stack)

        elif (consumer.try_multiple_vars_declaration(idx, tokens)
                or consumer.try_var_single_declaration(idx, tokens)):
            vars, idx = consumer.get_consume_res()
            core_logger.debug('Vars declaration: {}'.format(vars))
            names_resolver._add_declaration(
                self.uuid, NameType.VARIABLE, vars, stack)

        else:
            idx += 1

        self.idx = idx - 1

    def _process_identifier(self):
        idx = self.idx
        tokens, consumer = self.tokens, self.consumer
        stack, names_resolver = self.stack, self.names_resolver

        if consumer.try_method_declaration(idx, tokens):
            method, idx = consumer.get_consume_res()
            core_logger.debug('Method declaration: {}'.format(method))
            names_resolver._add_declaration(
                self.uuid, NameType.METHOD, method, stack)

        elif (consumer.try_multiple_vars_declaration(idx, tokens)
                or consumer.try_var_single_declaration(idx, tokens)):
            vars, idx = consumer.get_consume_res()
            core_logger.debug('Vars declaration: {}'.format(vars))
            names_resolver._add_declaration(
                self.uuid, NameType.VARIABLE, vars, stack)

        else:
            # We know at least one name is there
            consumer.try_outer_identifier(idx, tokens)
            name, idx = consumer.get_consume_res()
            core_logger.debug('Outer name: {}'.format(name))

        self.idx = idx - 1