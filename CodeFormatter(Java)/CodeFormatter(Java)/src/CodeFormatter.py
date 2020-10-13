import javalang as jl
import logging
from config.config import *

logging.basicConfig(filename='output/app.log', filemode='w', 
                    format='%(name)s - %(levelname)s - %(message)s')

class CodeFormatter:
    def __init__(self):
        # keywords that can be followed by parentheses
        self.p_keywords = set(['for', 'while', 'if', 'catch', 'try', 'synchronized', 'switch'])

        # keywords that can be followed by brace
        self.b_keywords = set(['try', 'do', 'finally', 'else', 'if'])

    def verify(self, tokens):
        tokens = list(tokens)
        output = self.format(tokens)
        res_tokens = list(jl.tokenizer.tokenize(output))

        if len(res_tokens) != len(tokens):
            err_msg = ('Internal error: tokens size mismatch(%d vs %d)' % len(res_tokens), len(tokens))
            logging.error(err_msg)
            raise AssertionError(err_msg)
        
        output = "Ignorring whitespaces, %d tokens received!!!\n" % len(tokens)
        mismatch_cnt = 1
        diff_func = lambda x, y: (x[y+1].position.line-x[y].position.line, x[y+1].position.column-x[y].position.column)
        for idx in range(len(tokens)-1):
            diff1, diff2 = diff_func(res_tokens, idx), diff_func(tokens, idx)

            if diff1 != diff2:
                output += ("%d. Incorrect relative position of the %s\n" % (mismatch_cnt, res_tokens[idx]))
                mismatch_cnt += 1
        
        return output

    def format(self, tokens):
        self.add_indent = lambda x, y: ' ' * x * y * tab_size
        if not use_tab_character: self.add_indent = lambda x,y: ' ' * x * y

        self.output = ''
        self.stack = [jl.tokenizer.JavaToken('')]
        self.indent_level, self.idx = 0, 0
        self.pre, self.cur = None, None
        self.need_indent_flag = False

        add_indent, stack = self.add_indent, self.stack

        if not isinstance(tokens, list):
            tokens = list(tokens)

        while self.idx < len(tokens):
            self.cur = tokens[self.idx]

            # process special tokens that mightn't follow indent rules
            if (isinstance(self.cur, jl.tokenizer.Identifier) and self.idx + 1 < len(tokens)
                and tokens[self.idx+1].value == ':' and stack[-1].value not in ('for', '?')):
                if not absolute_label_indent: output += add_indent(indent_level, indent)
                self.output += add_indent(1, label_indent) + self.cur.value + ':\n'
                self.idx += 2
                self.need_indent_flag = True
                self.pre = tokens[self.idx-1]
                continue

            # process indent
            if (self.need_indent_flag and 
                not self.cur.value in ('}', 'case', 'default')):
                self.output += add_indent(self.indent_level, indent)
                self.need_indent_flag = False

            add_output = self.cur.value

            # process tokens
            if self.cur.value == '@':
                if (self.idx + 2 < len(tokens) and tokens[self.idx+2].value == '('
                    and isinstance(tokens[self.idx+1], jl.tokenizer.Identifier)):
                    stack.append(self.cur)
                    add_output += (tokens[self.idx+1].value +
                                   (' ' if space_before_annotation_p else '') +
                                   tokens[self.idx+2].value)
                    self.idx += 2
                else:
                    logging.error('Incorrect position of the %s', self.cur)

            elif isinstance(self.cur, jl.tokenizer.Separator):
                add_output = self._format_separator(tokens)

            elif isinstance(self.cur, jl.tokenizer.Operator):
                add_output = self._format_operator(tokens)

            elif self.cur.value in ('case', 'default'):
                if self.cur.value == 'default':
                    var = 3
                if stack[-1].value == ':':
                    stack.pop()
                    if not self.need_indent_flag:
                        logging.error('Incorrect position of the %s', self.cur)
                    self.indent_level -= 1

                self.need_indent_flag = False
                self.output += add_indent(self.indent_level, indent)
                stack.append(self.cur)

            elif (not self.pre or isinstance(self.pre, (jl.tokenizer.Separator, jl.tokenizer.Operator))):
                pass

            else:
                add_output = ' ' + add_output

            self.output += add_output
            self.pre = tokens[self.idx]
            self.idx += 1

        if len(stack) > 1:
            logging.error('Error encountered when formatting for lexems %s', stack[1:])

        return self.output
    
    def _format_separator(self, tokens):
        ''' Used for formatting cur if it's a separator'''

        pre, cur, stack = self.pre, self.cur, self.stack
        add_output, add_indent = cur.value, self.add_indent

        if cur.value == '(':
            if isinstance(pre, jl.tokenizer.Identifier):
                stack.append(pre)
                if space_before_method_p: add_output = ' ' + cur.value

            elif isinstance(pre, jl.tokenizer.Keyword):
                if pre.value in self.p_keywords:
                    stack.append(pre)
                    flag = False
                    if pre.value == 'for': flag = space_before_for_p
                    elif pre.value == 'while': flag = space_before_while_p
                    elif pre.value == 'if': flag = space_before_if_p
                    elif pre.value == 'catch': flag = space_before_catch_p
                    elif pre.value == 'try': flag = space_before_try_p
                    elif pre.value == 'synchronized': flag = space_before_synchronized_p
                    elif pre.value == 'switch': flag = space_before_switch_p

                    if flag: add_output = ' ' + cur.value
                else:
                    logging.error('Incorrect position of the %s', cur)
            else:
                stack.append(cur)

        elif cur.value == ')':
            if isinstance(stack[-1], jl.tokenizer.Keyword):
                if self.idx + 1 < len(tokens) and tokens[self.idx+1].value == '{':
                    temp, flag = stack[-1], False
                    if temp.value == 'for': flag = space_before_for_b
                    elif temp.value == 'if': flag = space_before_if_b
                    elif temp.value == 'while': flag = space_before_while_b
                    elif temp.value == 'try': flag = space_before_try_b
                    elif temp.value == 'switch': flag = space_before_switch_b
                    elif temp.value == 'catch': flag = space_before_catch_b
                    elif temp.value == 'synchronized': flag = space_before_synchronized_b

                    if flag: add_output += ' '

                elif self.idx + 1 < len(tokens) and tokens[self.idx+1].value != ';':
                    add_output += ' '
                stack.pop()

            elif isinstance(stack[-1], jl.tokenizer.Identifier):
                if self.idx + 1 < len(tokens) and tokens[self.idx+1].value == '{':
                    if space_before_method_b: add_output += ' '

                # tricky here is handling throw x,y after ')', but before '{'
                stack.pop()

            elif stack[-1].value == '(':
                stack.pop()

            elif stack[-1].value == '@':
                add_output += '\n'
                stack.pop()

            else:
                logging.error('Incorrect position of the %s', cur)

        elif cur.value == '[':
            if self.idx + 1 < len(tokens) and tokens[self.idx+1].value == ']':
                add_output += ']'
                if self.idx + 2 < len(tokens):
                    if tokens[self.idx+2].value == '{':
                        stack.append(jl.tokenizer.JavaToken('[]'))
                    elif isinstance(tokens[self.idx+2], jl.tokenizer.Identifier):
                        add_output += ' '
                self.idx += 1

        elif cur.value == ';':
            if isinstance(stack[-1], jl.tokenizer.Keyword) and stack[-1].value in ('for', 'try'):
                if space_before_semicolon: add_output = ' ' + cur.value
                elif space_after_semicolon: add_output += ' '
            else:
                self.need_indent_flag = True
                add_output += '\n'

        elif cur.value == '.': # don't add space
            pass

        elif cur.value == '{':
            if stack[-1].value == '[]':
                if space_before_initialization_b: add_output = ' ' + cur.value

            elif stack[-1].value == '@':
                if space_before_annotation_b: add_output = ' ' + cur.value

            else:
                if isinstance(pre, jl.tokenizer.Keyword) and pre.value in self.b_keywords:
                    stack.append(pre)
                    flag = False
                    if pre.value == 'try': flag = space_before_try_b
                    elif pre.value == 'if': flag = space_before_if_b
                    elif pre.value == 'do': flag = space_before_do_b
                    elif pre.value == 'finally': flag = space_before_finally_b
                    elif pre.value == 'else': flag = space_before_else_b

                    if flag: add_output = ' ' + cur.value

                elif stack[-1].value in ('case', 'default'):
                    stack[-1] = cur

                else:
                    stack.append(cur)

                self.indent_level += 1
                self.need_indent_flag = True
                add_output += '\n'

        elif cur.value == '}':
            if stack[-1].value == '[]':
                stack.pop()

            elif stack[-1].value == '@': # skip
                pass

            elif isinstance(stack[-1], jl.tokenizer.Keyword):
                self.indent_level -= 1
                if stack[-1].value == 'do':
                    if self.idx + 1 < len(tokens) and tokens[self.idx+1].value == 'while':
                        if space_before_while_keyword: add_output = ' ' + cur.value
                        self.need_indent_flag = False
                    else:
                        logging.error('Incorrect position of the %s', stack[-1])

                    self.need_indent_flag = False
                    self.output += add_indent(self.indent_level, indent)

                else:
                    if stack[-1].value in ('try') and self.idx + 1 < len(tokens):
                        if tokens[self.idx+1].value == 'catch':
                            if space_before_catch_keyword: add_output = ' ' + cur.value
                        elif tokens[self.idx+1].value == 'finally':
                            if space_before_finally_keyword: add_output = ' ' + cur.value

                    self.need_indent_flag = True
                    self.output += add_indent(self.indent_level, indent)
                    add_output += '\n'

                stack.pop()

            elif stack[-1].value in ('{', ':'):
                if self.idx + 1 < len(tokens):
                    if tokens[self.idx+1].value == ';':
                        add_output += ';'
                        self.idx += 1

                    elif stack[-1].value == ':':
                        self.indent_level -= 1
                        stack.pop()

                    else:
                        flag = False
                        if tokens[self.idx+1].value == 'catch':
                            flag = space_before_catch_keyword
                        elif tokens[self.idx+1].value == 'finally':
                            flag = space_before_finally_keyword
                        elif tokens[self.idx+1].value == 'else':
                            flag = space_before_else_keyword

                        if flag: add_output = ' ' + add_output

                self.indent_level -= 1
                self.output += add_indent(self.indent_level, indent)
                self.need_indent_flag = True
                add_output += '\n'
                stack.pop()

            else:
                logging.error('Incorrect position of the %s', cur)


        elif cur.value == ',':
            if (isinstance(stack[-1], jl.tokenizer.Identifier) or
                stack[-1].value in ('[]', '@')):
                add_output += add_indent(1, continuation_indent)

        return add_output

    def _format_operator(self, tokens):
        ''' Used for formatting cur if it's an operator'''

        pre, cur, stack = self.pre, self.cur, self.stack
        add_output = cur.value

        if (cur.is_prefix() and (cur.value not in ('+', '-') or
            isinstance(pre, (jl.tokenizer.Separator, jl.tokenizer.Keyword, jl.tokenizer.Operator)))):
            if (not cur.is_postfix() or (self.idx + 1 < len(tokens) and
                (isinstance(tokens[self.idx+1], (jl.tokenizer.Identifier,))
                            or tokens[self.idx+1].value == '('))):
                add_output += (' ' if space_around_unary else '')
        else:
            flag = False
            if cur.is_assignment(): flag = space_around_assignment
            elif cur.value in ('==', '!='): flag = space_around_equality
            elif cur.value in ('<', '>', '<=', '>='): flag = space_around_relational
            elif cur.value in ('&&', '||'): flag = space_around_logical
            elif cur.value in ('<<', '>>', '>>>'): flag = space_around_shift
            elif cur.value == '::': flag = space_around_method_reference
            elif cur.value in ('&', '|', '^'): flag = space_around_bitwise
            elif cur.value == '->': flag = space_around_lambda_arrow
            elif cur.value in ('+', '-'): flag = space_around_additive
            elif cur.value == ':':
                if stack[-1].value == 'for': flag = False
                elif stack[-1].value == '?':
                    flag = space_around_ternary
                    stack.pop()
                elif stack[-1].value in ('case', 'default'):
                    if self.idx+1 < len(tokens) and tokens[self.idx+1].value != '{':
                        self.indent_level += 1
                        self.need_indent_flag = True
                        add_output += '\n'
                        stack[-1] = cur
                    else:
                        add_output += ' '

            elif cur.value == '?':
                if (not (isinstance(pre, jl.tokenizer.Operator)
                         and pre.value == '<') and self.idx + 1 < len(tokens)):
                    flag = space_around_ternary
                    stack.append(cur)
                elif self.idx + 1 < len(tokens) and tokens[self.idx+1].value != '>':
                    add_output += ' '
            else: flag = space_around_operator

            if flag: add_output = ' ' + cur.value + ' '

        return add_output
            