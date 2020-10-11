import javalang as jl
import enum
import logging
from config import *

logging.basicConfig(filename='app.log', filemode='w', 
                    format='%(name)s - %(levelname)s - %(message)s')

class CodeFormatter:
    def __init__(self):
        pass

    def apply_config(self):
        self.add_indent = lambda x, y: ' ' * x * y * tab_size
        if not use_tab_character: self.add_indent = lambda x,y: ' ' * x * y

    def format(self, tokens):
        self.apply_config()

        output = ''
        stack = [jl.tokenizer.JavaToken('')]
        add_indent = self.add_indent
        indent_level, idx = 0, 0
        tokens = list(tokens)
        pre = None
        need_indent_flag = False

        for idx in range(len(tokens)):
            print(tokens[idx])
            cur = tokens[idx]
            add_output = cur.value

            # process indent
            if need_indent_flag:
                output += add_indent(indent_level - (cur.value == '}'), indent)
                need_indent_flag = False

            # process separators
            if cur.value == '(':
                if isinstance(pre, jl.tokenizer.Identifier):
                    stack.append(pre)
                    add_output = (' ' if space_before_method else '') + cur.value
                elif isinstance(pre, jl.tokenizer.Keyword):
                    if pre.value in ('for', 'while', 'if', 'catch', 'try', 'synchronized'):
                        stack.append(pre)
                        add_output = (' ' if space_before_keyword else '') + cur.value
                    else:
                        logging.warning('Incorrect position of the %s', cur)
                else: # expression parentheses or template
                    stack.append(cur)
            elif cur.value == ')':
                if not pre: logging.warning('Incorrect position of the %s', cur)
                pre = tokens[idx-1]
                if (isinstance(stack[-1], (jl.tokenizer.Identifier, jl.tokenizer.Keyword)) or 
                    stack[-1].value == '('):
                    stack.pop()
                else:
                    logging.warning('Incorrect position of the %s', cur)
            elif cur.value == ';':
                if isinstance(stack[-1], jl.tokenizer.Keyword) and stack[-1].value in ('for', 'try'):
                    add_output += (' ' if space_after_semicolon else '')
                else:
                    need_indent_flag = True
                    add_output += '\n'
            elif cur.value == '{':
                if idx >= 2 and pre.value == ']' and tokens[idx-2].value == '[':
                    stack.append(jl.tokenizer.JavaToken('[]'))
                else:
                    indent_level += 1
                    stack.append(cur)
                    need_indent_flag = True
                    add_output += '\n'
            elif cur.value == '}':
                if stack[-1].value == '{':
                    indent_level -= 1
                    stack.pop()
                    need_indent_flag = True
                    add_output += '\n'
                elif stack[-1].value == '[]':
                    stack.pop()
                else:
                    logging.warning('Incorrect position of the %s', cur)
            elif cur.value == ',':
                if (isinstance(stack[-1], jl.tokenizer.Identifier) or
                    stack[-1].value == '[]'):
                    add_output += add_indent(1, continuation_indent)
            elif isinstance(cur, jl.tokenizer.Operator):
                if cur.is_assignment() or cur.is_infix():
                    if space_within_operator: add_output = ' ' + cur.value + ' '
            elif (isinstance(cur, (jl.tokenizer.Separator)) or
                  isinstance(pre, (jl.tokenizer.Separator, jl.tokenizer.Operator)) or 
                  not pre):
                pass
            else:
                add_output = ' ' + add_output

            output += add_output
            pre = cur

        print('\n\n')
        return output