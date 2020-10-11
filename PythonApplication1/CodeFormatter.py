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

        while idx < len(tokens):
            cur = tokens[idx]
            add_output = cur.value

            # process special (class, label, ...)
            if isinstance(cur, jl.tokenizer.Identifier) and idx + 1 < len(tokens) and tokens[idx+1].value == ':':
                if not absolute_label_indent: output += add_indent(indent_level, indent)
                output += add_indent(1, label_indent) + cur.value + ':\n'
                idx += 2
                need_indent_flag = True
                pre = tokens[idx-1]
                continue

            # process indent
            if need_indent_flag:
                output += add_indent(indent_level - (cur.value == '}'), indent)
                need_indent_flag = False

            # process separators
            if cur.value == '@':
                if (idx + 2 < len(tokens) and 
                    isinstance(tokens[idx+1], jl.tokenizer.Identifier) and 
                    tokens[idx+2].value == '('):
                    stack.append(cur)
                    add_output += tokens[idx+1].value + tokens[idx+2].value
                    idx += 2
                else:
                    logging.warning('Incorrect position of the %s', cur)
            elif cur.value == '(':
                if isinstance(pre, jl.tokenizer.Identifier):
                    stack.append(pre)
                    add_output = (' ' if space_before_method else '') + cur.value
                elif isinstance(pre, jl.tokenizer.Keyword):
                    if pre.value in ('for', 'while', 'if', 'catch', 'try', 'synchronized', 'switch'):
                        stack.append(pre)
                        add_output = (' ' if space_before_keyword else '') + cur.value
                    else:
                        logging.warning('Incorrect position of the %s', cur)
                else: # expression parentheses or template
                    stack.append(cur)
            elif cur.value == ')':
                if not pre: logging.warning('Incorrect position of the %s', cur)
                if (isinstance(stack[-1], (jl.tokenizer.Identifier, jl.tokenizer.Keyword)) or 
                    stack[-1].value == '('):
                    stack.pop()
                elif stack[-1].value == '@':
                    add_output += '\n'
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
                    add_output = (' ' if space_before_initialization else '') + cur.value
                elif stack[-1].value == '@': pass
                else:
                    indent_level += 1
                    if pre and pre.value == 'do': stack.append(pre)
                    else: stack.append(cur)
                    need_indent_flag = True
                    add_output += '\n'
            elif cur.value == '}':
                if stack[-1].value == '{':
                    indent_level -= 1
                    stack.pop()
                    if idx + 1 < len(tokens) and tokens[idx+1].value == ';':
                        add_output += ';'
                        idx += 1
                    need_indent_flag = True
                    add_output += '\n'
                elif stack[-1].value == 'do':
                    indent_level -= 1
                    stack.pop()
                elif stack[-1].value == '[]':
                    stack.pop()
                elif stack[-1].value == '@': pass
                else:
                    logging.warning('Incorrect position of the %s', cur)
            elif cur.value == ',':
                if (isinstance(stack[-1], jl.tokenizer.Identifier) or
                    stack[-1].value in ('[]', '@')):
                    add_output += add_indent(1, continuation_indent)
            elif isinstance(cur, jl.tokenizer.Operator):
                add_output = self._format_operator(pre, cur, idx, tokens)
            elif (isinstance(cur, jl.tokenizer.Separator) or
                  isinstance(pre, (jl.tokenizer.Separator, jl.tokenizer.Operator)) or 
                  not pre):
                pass
            else:
                add_output = ' ' + add_output

            output += add_output
            pre = tokens[idx]
            idx += 1

        print('\n\n')
        return output

    def _format_operator(self, pre, cur, idx, tokens):
        if (cur.is_prefix() and 
            (cur.value not in ('+', '-') or
             isinstance(pre, (jl.tokenizer.Separator, jl.tokenizer.Keyword, jl.tokenizer.Operator)))):
            if (not cur.is_postfix() or (idx + 1 < len(tokens) and
                (isinstance(tokens[idx+1], jl.tokenizer.Identifier) or tokens[idx+1].value == '('))):
                return (' ' if space_around_unary else '') + cur.value
        else:
            flag = False
            if cur.is_assignment(): flag = space_around_assignment
            elif cur.value in ('==', '!='): flag = space_around_equality
            elif cur.value in ('&&', '||'): flag = space_around_logical
            elif cur.value == '::': flag = space_around_method_reference
            elif cur.value in ('&', '|', '^'): flag = space_around_bitwise
            elif cur.value == '->': flag = space_around_lambda_arrow
            elif cur.value in ('+', '-'): flag = space_around_additive
            else: flag = space_around_operator
            if flag: return ' ' + cur.value + ' '

        return cur.value # no additional spaces
            