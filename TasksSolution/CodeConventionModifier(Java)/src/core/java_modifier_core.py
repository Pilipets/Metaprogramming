import logging, sys, os

from .tokenizer import java_lexer
from .tokenizer.java_lexer import tokenize
from .java_modifier_utils import ConventionNaming as naming_utils, ModifierError

class JavaModifierCore:
    def __init__(self):
        pass

    def initialize_modify(self):
        self.tokens_left = dict()
        self.format_names = dict()
        self.output = ''
        self.stack = [java_lexer.JavaToken('')]
        self.idx = 0
        self.pre, self.cur = None, None

    def modify_one(self, text : str):
        tokens = list(tokenize(text, raise_errors=True))
        tokens.append(java_lexer.JavaToken(''))

        while self.idx < len(tokens)-1:
            self.cur = tokens[self.idx]

            # process tokens
            if isinstance(self.cur, java_lexer.Identifier):
                self._process_identifier(tokens)

            self.pre = tokens[self.idx]
            self.idx += 1


        if len(self.stack) > 1:
            err_msg = 'Error encountered when formatting file, stack size: %d\n' % (len(stack) - 1)
            logging.error(err_msg + '\n'.join(str(x) for x in stack[1:]))
            raise FormatterError(err_msg)
        else:
            tokens.pop()

    def _process_identifier(self, tokens : list):
        pre, cur = self.pre, self.cur
        stack = self.stack
        if pre:
            if (isinstance(pre, java_lexer.Keyword)
                    and pre.value in ('class', 'interface')):
                #stack.append(pre)
                print(naming_utils.get_class_name(cur.value))