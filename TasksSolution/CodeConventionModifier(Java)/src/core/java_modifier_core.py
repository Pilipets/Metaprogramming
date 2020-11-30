from logging import DEBUG as logging_DEBUG

from .tokenizer import java_tokens
from .tokenizer.java_lexer import tokenize
from .convention import NameType
from .analyzer import AdvancedConsumer as Consumer
from .analyzer import NamesResolver
from .utils import setup_logger, ModifierError

# Initialize logging
core_logger = setup_logger(__name__, logging_DEBUG)

class JavaModifierCore:
    def __init__(self):
        pass

    def _prepare_one(self, fp):
        javacode = ''
        with open(fp, 'r') as fin:
            javacode = fin.read()

        tokens = list(tokenize(javacode, raise_errors=True))
        stack = [java_tokens.JavaToken('')]
        consumer = Consumer()
        return tokens, stack, consumer

    def initialize(self, file_paths):
        core_logger.debug('Initializing modify...'.center(60, '-'))

        self.names_resolver = NamesResolver()
        resolver = self.names_resolver.get_global_resolver()

        for fp in file_paths:
            try:
                self._analyze_one(*self._prepare_one(fp), resolver, True)
            except Exception as ex:
                print("Exception received when initializing the file={}, ex={}.".format(fp, ex))

    def verify_one(self, file_path, touch_docs):
        self.modify_one(file_path, touch_docs, produce_file = False)

    def modify_one(self, file_path, touch_docs, produce_file = True):
        # Initialization part
        tokens, stack, consumer = self._prepare_one(file_path)

        resolver = self.names_resolver.new_file_resolver(file_path, tokens,
                                                         produce_file, touch_docs)

        # Analyzing part
        core_logger.debug(f'Analyzing "{file_path}"'.center(60, '-'))
        self._analyze_one(tokens, stack, consumer, resolver)

        # Renaming part
        core_logger.debug(f'Renaming for "{file_path}"'.center(60, '-'))
        self._finalize_one(stack, resolver)

    def finalize(self):
        core_logger.debug('Finalizing modify...'.center(60, '-'))

        self.names_resolver.close()
        self.names_resolver = None

    def _analyze_one(self, tokens, stack, consumer, resolver, preprocess_flag = False):
        idx = 0
        while idx < len(tokens):

            # ----------------------Specials and not important--------------------
            if isinstance(tokens[idx], java_tokens.Separator):
                idx = self._process_separator(idx, tokens, stack)
                continue

            elif ((preprocess_flag and len(stack) > 3)
                    or isinstance(tokens[idx], java_tokens.Comment)):
                idx += 1
                continue

            # --------------------------------------------------------------------

            doc_idx = idx
            # ----------------Modifiers and annotations--------------------------
            if consumer.try_anotation_invocations(idx, tokens):
                # make sure we don't misinterpret declaration with annotation
                _, idx = consumer.get_consume_res()

            modifiers = []
            if consumer.try_instances(java_tokens.Modifier, idx, tokens):
                modifiers, idx = consumer.get_consume_res()

            # --------------------------------------------------------------------

            # ------------------------------Declarations--------------------------
            start_idx = idx
            if consumer.try_class_declaration(idx, tokens):
                cls, idx = consumer.get_consume_res()

                resolver.add_name_declaration(NameType.CLASS, cls, modifiers, stack)
                resolver.add_doc_declaration((doc_idx, start_idx, idx), NameType.CLASS, modifiers, stack)
                stack.append(tokens[start_idx])

            elif consumer.try_annotation_declaration(idx, tokens):
                cls, idx = consumer.get_consume_res()

                resolver.add_name_declaration(NameType.ANNOTATION, cls, modifiers, stack)
                stack.append(tokens[start_idx+1])

            elif consumer.try_anonymous_class(idx, tokens):
                _, idx = consumer.get_consume_res()

                stack.append(tokens[start_idx])
                stack.append(tokens[idx-1])

            elif (len(stack) > 1 and stack[-1].value == '{'
                    and stack[-2].value in ('class', 'interface', 'new')
                        and consumer.try_method_declaration(idx, tokens)):
                method, idx = consumer.get_consume_res()

                resolver.add_name_declaration(NameType.METHOD, method, modifiers, stack)
                resolver.add_doc_declaration((doc_idx, start_idx, idx), NameType.METHOD, modifiers, stack)

            elif (consumer.try_multiple_vars_declaration(idx, tokens)
                    or consumer.try_var_single_declaration(idx, tokens)):
                vars, idx = consumer.get_consume_res()

                if 'static' in modifiers and 'final' in modifiers:
                    resolver.add_name_declaration(NameType.CONST_VARIABLE, vars, modifiers, stack)
            
                else:
                    resolver.add_name_declaration(NameType.VARIABLE, vars, modifiers, stack)

            elif doc_idx == idx:
                idx += 1


            # -------------------------------------------------------------------

    def _finalize_one(self, stack, resolver):
        if len(stack) != 1:
            raise ModifierError('Invalid Java code semantics encountered, stack size:', len(stack))

        resolver.close()

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