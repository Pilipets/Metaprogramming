import logging, sys, os

from .tokenizer import java_lexer
from .tokenizer.java_lexer import tokenize
from .utils.convention_naming import ConventionNaming
from .utils.structures_consumer import StructuresConsumer
from .utils.names_resolver import NamesResolver

from collections import defaultdict

class ModifierError(Exception):
    pass

class JavaModifierCore:
    def __init__(self):
        pass

    def initialize_modify(self):
        self.names_resolver = NamesResolver()
        self.stack = [java_lexer.JavaToken('')]
        self.idx = 0
        self.pre, self.cur = None, None

    def modify_one(self, text : str):
        tokens = list(tokenize(text, raise_errors=True))

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

    def _process_keyword(self, tokens):
        idx, cur = self.idx, self.cur
        stack = self.stack

        # void
        if cur.value == 'void':
            if StructuresConsumer.try_void_method_declaration(idx, tokens, False):
                res = StructuresConsumer.get_consume_res()
                print('Method declaration:', res[0], res[1])
                self.idx = res[-1] - 1

        elif cur.value in ('class', 'interface'):
            if StructuresConsumer.try_class_declaration(idx, tokens, False):
                res = StructuresConsumer.get_consume_res()
                print('Class:', res[0])

                stack.append(cur)
                self.idx = res[-1] - 1

        elif (len(stack) > 2 and stack[-1].value == '{'
                and stack[-2].value in ('class', 'interface')):

            if StructuresConsumer.try_class_const_declaration(idx, tokens):
                res = StructuresConsumer.get_consume_res()
                print('Const:', res[0], res[1])

                self.idx = res[-1] - 1

    def _process_simple_type(self, tokens):
        idx = self.idx

        if StructuresConsumer.try_simple_method_declaration(idx, tokens, False):
            res = StructuresConsumer.get_consume_res()
            print('Method declaration:', res[0], res[1])
            self.idx = res[-1] - 1

        elif StructuresConsumer.try_var_declaration(idx, tokens):
            res = StructuresConsumer.get_consume_res()
            print('Var declaration:', res[0], res[1])
            self.idx = res[-1] - 1

    def _process_identifier(self, tokens : list):
        cur = self.cur

        if StructuresConsumer.try_var_declaration(self.idx, tokens, False):
            # Name declaration found
            res = StructuresConsumer.get_consume_res()
            end = res[-1]

            # Try method declaration first
            if (end < len(tokens) and tokens[end].value == '('):
                print('Method declaration:', res[0], res[1])
                self.idx = end

            # Method declaration not found, proceed with variable
            else: 
                print('Var declaration:', res[0], res[1])
                self.idx = end-1

        else:
            print('Name:', cur.value)