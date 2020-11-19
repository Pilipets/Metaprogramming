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
        pass

    def initialize(self):
        core_logger.debug('Initializing modify...'.center(60, '-'))

        self.names_resolver = NamesResolver()

    def verify_one(self, file_path, text):
        self.modify_one(file_path, text, produce_file = False)

    def modify_one(self, file_path, text, produce_file = True):
        #Aliases
        names_resolver = self.names_resolver

        # Initialization part
        tokens = tuple(tokenize(text, raise_errors=True))
        changed_tokens = [(idx, copy.copy(x)) for idx, x in enumerate(tokens)
                          if isinstance(x, java_lexer.Identifier)]

        scope_id = names_resolver.new_local_resolver(file_path, tokens, changed_tokens, produce_file)
        stack = [java_lexer.JavaToken('')]
        consumer = Consumer()

        # Analyzing part
        core_logger.debug(f'Analyzing "{file_path}"'.center(60, '-'))
        self._analyze_one(scope_id, tokens, stack, consumer, names_resolver)

        # Renaming part
        core_logger.debug(f'Renaming for "{file_path}"'.center(60, '-'))
        self._finalize_one(scope_id, stack, names_resolver)

    def finalize(self):
        core_logger.debug('Finalizing modify...'.center(60, '-'))

        self.names_resolver.close_all_resolvers()
        self.names_resolver = None

    def _analyze_one(self, scope_id, tokens,
                     stack, consumer, names_resolver):
        idx = 0
        while idx < len(tokens):
            # ----------------------Specials and not important--------------------
            if isinstance(tokens[idx], java_lexer.Separator):
                idx = self._process_separator(idx, tokens, stack)
                continue

            elif isinstance(tokens[idx], java_lexer.Comment):
                idx += 1
                continue

            # --------------------------------------------------------------------

            start = idx
            # ----------------Modifiers and annotations--------------------------
            if consumer.try_anotation_invocations(idx, tokens):
                # make sure we don't misinterpret declaration with annotation
                _, idx = consumer.get_consume_res()

            modifiers = []
            if consumer.try_instances(java_lexer.Modifier, idx, tokens):
                modifiers, idx = consumer.get_consume_res()

            # --------------------------------------------------------------------

            # ------------------------------Declarations--------------------------
            if consumer.try_class_declaration(idx, tokens):
                start_token = tokens[idx] # class
                cls, idx = consumer.get_consume_res()

                core_logger.debug('Class declaration: {}'.format(cls))
                names_resolver._add_declaration(
                    scope_id, NameType.CLASS , cls, stack)

                stack.append(start_token)

            elif consumer.try_annotation_declaration(idx, tokens):
                start_token = tokens[idx+1] # skip @
                cls, idx = consumer.get_consume_res()

                core_logger.debug('Annotation declaration: {}'.format(cls))
                names_resolver._add_declaration(
                    scope_id, NameType.CLASS , cls, stack)

                stack.append(start_token)

            elif consumer.try_anonymous_class(idx, tokens):
                start_token = tokens[idx]
                _, idx = consumer.get_consume_res()

                stack.append(start_token)
                stack.append(tokens[idx-1])

            elif (len(stack) > 1 and stack[-1].value == '{'
                    and stack[-2].value in ('class', 'interface', 'new')
                        and consumer.try_method_declaration(idx, tokens)):
                method, idx = consumer.get_consume_res()

                core_logger.debug('Method declaration: {}'.format(method))
                names_resolver._add_declaration(
                    scope_id, NameType.METHOD, method, stack)

            elif (consumer.try_multiple_vars_declaration(idx, tokens)
                    or consumer.try_var_single_declaration(idx, tokens)):
                vars, idx = consumer.get_consume_res()

                if 'static' in modifiers and 'final' in modifiers:
                    core_logger.debug('Const vars declaration: {}'.format(vars))
                    names_resolver._add_declaration(
                        self.uuid, NameType.CONST_VARIABLE, vars, stack)
            
                else:
                    core_logger.debug('Vars declaration: {}'.format(vars))
                    names_resolver._add_declaration(
                        scope_id, NameType.VARIABLE, vars, stack)

            elif start == idx:
                idx += 1

            # -------------------------------------------------------------------

    def _finalize_one(self, scope_id, stack, names_resolver):
        if len(stack) != 1:
            raise ModifierError('Invalid Java code semantics encountered, stack size:', len(stack))

        f_r = names_resolver.get_local_resolver(scope_id)
        g_r = names_resolver.get_global_resolver()

        renames = f_r.get_renames()
        for idx, x in renames:
            name = x.value
            if name in f_r:
                x.value = f_r[name]

            elif name in g_r:
                x.value = g_r[name]

            # Store for post processing - will be resolved on the fly
            else:
                f_r.add_pending(x)

        if f_r.is_pending():
            cnt = f_r.get_pending_count()
            core_logger.debug(
                '{} name conflicts encountered: {}'.format(
                    cnt, ', '.join(x for x in f_r.get_pending())
            ))
            core_logger.debug('Postponing renaming for "{}"'.format(f_r.get_file_path()))

        else:
            f_r.close()

    def _process_separator(self, idx, tokens, stack):
        cur = tokens[idx]

        if cur.value in '{(':
            stack.append(cur)

        elif cur.value == '}':
            if stack[-1].value == '{':
                stack.pop()

            if stack[-1].value in ('class', 'interface', 'new'):
                stack.pop()

        elif cur.value == ')':
            if stack[-1].value == '(':
                stack.pop()

        return idx + 1