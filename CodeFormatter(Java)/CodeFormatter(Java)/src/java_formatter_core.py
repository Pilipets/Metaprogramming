import logging

from src.tokenizer import java_lexer
from config.config_handler import *

logging.basicConfig(filename='output/app.log', filemode='w',
                    format='%(name)s - %(levelname)s - %(message)s')

class JavaFormatterCore:
    def __init__(self):
        # keywords that can be followed by parentheses
        self.p_keywords = set(['for', 'while', 'if', 'catch', 'try', 'synchronized', 'switch'])

        # keywords that can be followed by brace
        self.b_keywords = set(['try', 'do', 'finally', 'else'])

        self.add_indent = None
        self.output = ''
        self.stack = []
        self.indent_level, self.idx = 0, 0
        self.pre, self.cur = None, None
        self.need_indent_flag = False

    def _report_token_err(self, err):
        logging.error('Incorrect usage of the %s', err)

    def _reset(self):
        self.add_indent = lambda x, y: ' ' * x * y * tab_size
        if not use_tab_character:
            self.add_indent = lambda x, y: ' ' * x * y

        self.output = ''
        self.stack = [java_lexer.JavaToken('')]
        self.indent_level, self.idx = 0, 0
        self.pre, self.cur = None, None
        self.need_indent_flag = False

    def verify(self, tokens):
        tokens = list(tokens)
        output = self.format(tokens)
        res_tokens = list(java_lexer.tokenize(output))

        if len(res_tokens) != len(tokens):
            err_msg = ('Internal error: tokens size mismatch(%d vs %d)'
                       % len(res_tokens), len(tokens))
            logging.error(err_msg)
            raise AssertionError(err_msg)

        output = "Ignorring whitespaces, %d tokens received!!!\n" % len(tokens)
        mismatch_cnt = 1
        diff_func = lambda x, y: (x[y+1].position.line-x[y].position.line,
                                  x[y+1].position.column-x[y].position.column)

        for idx in range(len(tokens)-1):
            diff1, diff2 = diff_func(res_tokens, idx), diff_func(tokens, idx)

            if diff1 != diff2:
                output += ("%d. Incorrect relative position of the %s\n"
                           % (mismatch_cnt, res_tokens[idx]))
                mismatch_cnt += 1

        return output

    def format(self, tokens):
        self._reset()
        add_indent, stack = self.add_indent, self.stack

        if not isinstance(tokens, list):
            tokens = list(tokens)

        tokens.append(java_lexer.JavaToken(''))

        while self.idx < len(tokens)-1:
            self.cur = tokens[self.idx]

            # process special tokens that mightn't follow indent rules
            if self._format_special(tokens):
                continue

            # process indent
            self._format_indent()

            add_output = self.cur.value

            # process tokens
            if self.cur.value == '@':
                if (self.idx + 2 < len(tokens) and tokens[self.idx+2].value == '('
                        and isinstance(tokens[self.idx+1], java_lexer.Identifier)):
                    stack.append(self.cur)
                    add_output += (tokens[self.idx+1].value +
                                   (' ' if space_before_annotation_p else '') +
                                   tokens[self.idx+2].value)
                    self.idx += 2
                elif isinstance(tokens[self.idx+1], java_lexer.Identifier):
                    # decorator
                    self.need_indent_flag = True
                    add_output += tokens[self.idx+1].value + '\n'
                    self.idx += 1

            elif isinstance(self.cur, java_lexer.Separator):
                add_output = self._format_separator(tokens)

            elif isinstance(self.cur, java_lexer.Operator):
                add_output = self._format_operator(tokens)

            elif isinstance(self.cur, java_lexer.Keyword):
                add_output = self._format_keyword(tokens)

            elif (not self.pre or isinstance(self.pre, (java_lexer.Separator, java_lexer.Operator))
                  or len(self.output) == 0 or self.output[-1].isspace()):
                pass

            else:
                add_output = ' ' + add_output

            self.output += add_output
            self.pre = tokens[self.idx]
            self.idx += 1

        if len(stack) > 1:
            logging.error('Error encountered when formatting for lexems %s', stack[1:])

        return self.output

    def _format_keyword(self, tokens):
        cur, stack, add_indent = self.cur, self.stack, self.add_indent
        add_output = cur.value

        if cur.value in ('case', 'default'):

            if stack[-1].value == ':':
                stack[-1] = cur
                self.indent_level -= 1
                if not self.need_indent_flag:
                    self._report_token_err(self.cur)
            else:
                stack.append(cur)

            self.output += add_indent(self.indent_level, indent)
            self.need_indent_flag = False

        elif cur.value == 'new':
            if isinstance(tokens[self.idx+1], java_lexer.Identifier):
                add_output += ' ' + tokens[self.idx+1].value
                self.idx += 1
                stack.append(cur)

        elif cur.value in ('class', 'assert', 'interface'):
            stack.append(cur)

        if (self.pre and not isinstance(self.pre, (java_lexer.Separator, java_lexer.Operator))
                and len(self.output) > 0 and not self.output[-1].isspace()):
            add_output = ' ' + add_output

        return add_output

    def _format_indent(self):
        ''' Used for inserting indent before current token'''
        if self.need_indent_flag and not self.cur.value in ('}', 'case', 'default'):
            self.output += self.add_indent(self.indent_level, indent)
            self.need_indent_flag = False

    def _format_special(self, tokens):
        ''' Used for formatting labels that mightn't follow indent rules'''
        if (isinstance(self.cur, java_lexer.Identifier)
                and tokens[self.idx+1].value == ':'
                and self.stack[-1].value not in ('for', '?', 'assert')):
            if not absolute_label_indent:
                self.output += self.add_indent(self.indent_level, indent)
            self.output += self.add_indent(1, label_indent) + self.cur.value + ':\n'
            self.idx += 2
            self.need_indent_flag = True
            self.pre = tokens[self.idx-1]
            return True
        return False

    def _format_separator(self, tokens):
        ''' Used for formatting cur if it's a separator'''

        pre, cur, stack = self.pre, self.cur, self.stack
        add_output, add_indent = cur.value, self.add_indent

        if cur.value == '(':
            if isinstance(pre, java_lexer.Identifier) or stack[-1].value == 'new':
                # method call or object creating
                if stack[-1].value == 'new': stack.append(cur)
                else: stack.append(pre)
                add_output = (' ' if space_before_method_p else '')  + cur.value

            elif isinstance(pre, java_lexer.Keyword):
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

                    if flag:
                        add_output = ' ' + cur.value
                else:
                    self._report_token_err(cur)
            else: # expression
                stack.append(cur)

        elif cur.value == ')':
            if isinstance(stack[-1], java_lexer.Keyword):
                if stack[-1].value in self.p_keywords:
                    if tokens[self.idx+1].value == '{':
                        if brace_other == 'next_line':
                            add_output += '\n'
                            self.need_indent_flag = True

                        else:
                            temp, flag = stack[-1], False
                            if temp.value == 'for': flag = space_before_for_b
                            elif temp.value == 'if': flag = space_before_if_b
                            elif temp.value == 'while': flag = space_before_while_b
                            elif temp.value == 'try': flag = space_before_try_b
                            elif temp.value == 'switch': flag = space_before_switch_b
                            elif temp.value == 'catch': flag = space_before_catch_b
                            elif temp.value == 'synchronized': flag = space_before_synchronized_b

                            if flag: add_output += ' '

                        stack.append(cur)

                    elif tokens[self.idx+1].value != ';':
                        # keywords without braces are tricky
                        # we will decrease indent and delete keywords after meeting ;
                        self.indent_level += 1
                        self.need_indent_flag = True
                        stack.append(java_lexer.JavaToken('indent'))
                        add_output += '\n'

                    else:
                        stack.append(cur)

                else:
                    self._report_token_err(cur)
                    stack.pop() # clearing

            elif isinstance(stack[-1], java_lexer.Identifier):
                # without new
                if tokens[self.idx+1].value == '{':
                    # method declaration
                    if brace_in_method_declaration == 'next_line':
                        add_output += '\n'
                        self.need_indent_flag = True

                    elif space_before_method_b:
                        add_output += ' '

                    stack.append(cur)

                elif tokens[self.idx+1].value == 'throws':
                    # method declaration
                    self.idx += 1
                    add_output += ' ' + tokens[self.idx].value
                    stack.append(tokens[self.idx])

                else:
                    # method call
                    stack.pop()

            elif stack[-1].value == '(':
                if len(stack) > 1 and stack[-2].value == 'new':
                    if self.idx + 1 < len(tokens) and tokens[self.idx+1].value == '{':
                        # anonymous class
                        stack[-1] = java_lexer.Keyword('class')

                    else:
                        # object creation
                        stack.pop() # (
                        stack.pop() # new
                else:
                    # expression
                    stack.pop()

            elif stack[-1].value == '@':
                add_output += '\n'
                self.need_indent_flag = True
                stack.pop()

            else:
                self._report_token_err(cur)

        elif cur.value == '[':
            if tokens[self.idx+1].value == ']':
                add_output += ']'
                if self.idx + 2 < len(tokens):
                    if tokens[self.idx+2].value == '{':
                        stack.append(java_lexer.JavaToken('[]'))
                    elif tokens[self.idx+2].value != ')':
                        add_output += ' '
                self.idx += 1

        elif cur.value == ';':
            if isinstance(stack[-1], java_lexer.Keyword) and stack[-1].value in ('for', 'try'):
                if space_before_semicolon: add_output = ' ' + cur.value
                elif space_after_semicolon: add_output += ' '
            else:
                self.need_indent_flag = True
                add_output += '\n'

                # clear stack for current statement if something is there
                # better to use state machine here
                while len(stack) > 1:
                    if stack[-1].value == 'assert': stack.pop()
                    elif (stack[-1].value == 'indent' and len(stack) > 2
                          and isinstance(stack[-2], java_lexer.Keyword)
                          and stack[-2].value in self.p_keywords):
                        self.indent_level -= 1
                        stack.pop()
                        stack.pop()

                    elif (stack[-1].value == ')' and len(stack) > 2
                          and isinstance(stack[-2], java_lexer.Keyword)
                          and stack[-2].value in self.p_keywords):
                        # p_keyword(...);
                        stack.pop()
                        stack.pop()

                    else:
                        break

        elif cur.value == '.': # don't add space
            pass

        elif cur.value == '{':
            if stack[-1].value == '[]':
                if space_before_initialization_b: add_output = ' ' + cur.value
                stack.append(cur)

            elif stack[-1].value == '@':
                if space_before_annotation_b: add_output = ' ' + cur.value
                stack.append(cur)

            else:
                if isinstance(pre, java_lexer.Keyword) and pre.value in self.b_keywords:
                    stack.append(pre)
                    stack.append(cur)

                    if brace_other == 'next_line':
                        self.output += '\n' + add_indent(self.indent_level, indent)

                    else:
                        flag = False
                        if pre.value == 'try': flag = space_before_try_b
                        elif pre.value == 'do': flag = space_before_do_b
                        elif pre.value == 'finally': flag = space_before_finally_b
                        elif pre.value == 'else': flag = space_before_else_b

                        if flag:
                            add_output = ' ' + cur.value

                elif stack[-1].value == ')' and len(stack) > 1:
                    if (isinstance(stack[-2], java_lexer.Keyword)
                            and stack[-2].value in self.p_keywords):
                        # whitespaces set in ')'
                        if stack[-2].value == 'switch' and not indent_case_branches:
                            self.indent_level -= 1

                    # elif isinstance(stack[-2], java_lexer.Identifier): pass
                    stack[-1] = cur

                elif stack[-1].value in ('class', 'interface'):
                    if brace_in_class_declaration == 'next_line':
                        self.output += '\n' + add_indent(self.indent_level, indent)
                    elif space_before_class_b:
                        add_output = ' ' + add_output
                    stack.append(cur)

                elif isinstance(pre, java_lexer.Operator) and pre.value == '->':
                    if brace_in_lambda_declaration == 'next_line':
                        self.output += '\n' + add_indent(self.indent_level, indent)
                    elif space_before_lambda_b and not space_around_lambda_arrow:
                        add_output = ' ' + add_output

                    stack.append(pre)

                elif stack[-1].value == 'throws':
                    if brace_in_method_declaration == 'next_line':
                        self.output += '\n' + self.add_indent(self.indent_level, indent)
                    elif space_before_method_b:
                        add_output = ' ' + add_output

                    stack[-1] = cur

                elif stack[-1].value in ('case', 'default'):
                    stack[-1] = cur

                else:
                    stack.append(cur)

                self.indent_level += 1
                self.need_indent_flag = True
                add_output += '\n'

        elif cur.value == '}':
            if stack[-1].value == '->':
                self.indent_level -= 1
                self.output += add_indent(self.indent_level, indent)
                self.need_indent_flag = False
                stack.pop()

            elif len(stack) > 1 and stack[-1].value in (':', '{'):
                indent_flag_needed = self.need_indent_flag
                self.need_indent_flag = False

                if isinstance(stack[-2], java_lexer.Keyword):

                    if stack[-2].value in self.b_keywords:
                        if stack[-2].value == 'do':
                            if tokens[self.idx+1].value == 'while':
                                if new_line_while:
                                    add_output += '\n'
                                    self.need_indent_flag = True
                                elif space_before_while_keyword:
                                    add_output += ' '
                            else:
                                add_output += '\n'
                                self.need_indent_flag = True

                        elif stack[-2].value == 'try':
                            if self.idx + 1 < len(tokens):
                                if tokens[self.idx+1].value == 'catch':
                                    if catch_on_new_line:
                                        add_output += '\n'
                                        self.need_indent_flag = True
                                    elif space_before_catch_keyword:
                                        add_output += ' '

                                elif tokens[self.idx+1].value == 'finally':
                                    if finally_on_new_line:
                                        add_output += '\n'
                                        self.need_indent_flag = True
                                    elif space_before_finally_keyword:
                                        add_output += ' '

                                else:
                                    add_output += '\n'
                                    self.need_indent_flag = True

                        elif tokens[self.idx+1].value != ';':
                            add_output += '\n'
                            self.need_indent_flag = True

                        stack.pop() # {
                        stack.pop() # b_keyword

                    elif stack[-2].value in self.p_keywords:

                        if stack[-2].value == 'if':
                            if tokens[self.idx+1].value == 'else':
                                if new_line_before_else:
                                    self.need_indent_flag = True
                                    add_output += '\n'
                                elif space_before_else_keyword:
                                    add_output += ' '

                            elif tokens[self.idx+1].value != ';':
                                add_output += '\n'
                                self.need_indent_flag = True

                        elif stack[-2].value in ('try', 'catch'):
                            if tokens[self.idx+1].value == 'catch':
                                if catch_on_new_line:
                                    add_output += '\n'
                                    self.need_indent_flag = True
                                elif space_before_catch_keyword:
                                    add_output += ' '

                            elif tokens[self.idx+1].value == 'finally':
                                if finally_on_new_line:
                                    add_output += '\n'
                                    self.need_indent_flag = True
                                elif space_before_finally_keyword:
                                    add_output += ' '

                            else:
                                add_output += '\n'
                                self.need_indent_flag = True

                        elif tokens[self.idx+1].value != ';':
                            add_output += '\n'
                            self.need_indent_flag = True

                        else:
                            pass
                            # self.indent_level += 1

                        stack.pop() # {
                        stack.pop() # p_keyword

                    elif stack[-2].value in ('class', 'interface'):
                        # class declaration or anonymous class
                        stack.pop() # {
                        stack.pop() # stack[-2]
                        if stack[-1].value == 'new':
                            stack.pop()
                        else:
                            add_output += '\n'
                            self.need_indent_flag = True

                elif isinstance(stack[-2], java_lexer.Identifier):
                    # method declaration
                    stack.pop()
                    stack.pop()

                    add_output += '\n'
                    self.need_indent_flag = True

                elif stack[-2].value == '[]':
                    stack.pop() # {
                    stack.pop() # []
                    self.indent_level += 1

                elif stack[-2].value == '@':
                    stack.pop() # {
                    self.indent_level += 1

                elif (len(stack) > 3 and stack[-1].value == ':'
                      and stack[-2].value == '{' and stack[-3].value == 'switch'):
                    self.indent_level -= 1
                    add_output += ('\n' if tokens[self.idx+1].value != ';' else '')
                    self.need_indent_flag = True
                    stack.pop()
                    stack.pop()
                    stack.pop()

                else:
                    stack.pop()
                    add_output += '\n'
                    self.need_indent_flag = True

                self.indent_level -= 1
                if indent_flag_needed:
                    self.output += add_indent(self.indent_level, indent)

                # clear stack if something is there
                # better to use state machine here
                while len(stack) > 1:
                    if (stack[-1].value == 'indent' and len(stack) > 2
                            and isinstance(stack[-2], java_lexer.Keyword)
                            and stack[-2].value in self.p_keywords):
                        self.indent_level -= 1
                        stack.pop()
                        stack.pop()

                    else:
                        break

            else:
                self._report_token_err(cur)


        elif cur.value == ',':
            if stack[-1].value in ('[]', '@', '(') or isinstance(stack[-1], java_lexer.Identifier):
                if space_after_comma:
                    add_output += add_indent(1, continuation_indent)

        return add_output

    def _format_operator(self, tokens):
        ''' Used for formatting cur if it's an operator'''

        def _consume_template(idx):
            # template can include |<|,|>|?|extends|super|&|Identifier|SimpleType

            if idx < len(tokens) and tokens[idx].value == '>': return '<>'

            # Simple automata to handle complex cases
            open_cnt, add_output, state = 1, '<', 1
            while idx < len(tokens) and state > 0 and open_cnt > 0:
                temp, next_state, cur = tokens[idx].value, -1, tokens[idx]
                if state == 1:
                    if cur.value == '?': next_state = 2
                    elif isinstance(cur, java_lexer.Identifier): next_state = 4
                    elif isinstance(cur, java_lexer.SimpleType): next_state = 5
                elif state == 2:
                    if cur.value in ('extends', 'super'): next_state, temp = 3, ' ' + temp + ' '
                    elif cur.value == ',': next_state, temp = 1, temp + ' '
                    elif cur.value == '>': next_state, open_cnt = 5, open_cnt-1
                elif state == 3:
                    if isinstance(cur, java_lexer.Identifier): next_state = 4
                elif state == 4:
                    if cur.value in ('extends', 'super'): next_state, temp = 3, ' ' + temp + ' '
                    elif cur.value == '<': next_state, open_cnt = 1, open_cnt+1
                    elif cur.value == '>': next_state, open_cnt = 5, open_cnt-1
                    elif cur.value == ',': next_state, temp = 1, temp + ' '
                    elif cur.value == '&': next_state, temp = 3, ' ' + temp + ' '
                elif state == 5:
                    if cur.value == '>': next_state, open_cnt = 5, open_cnt-1
                    elif cur.value == ',': next_state, temp = 1, temp + ' '

                state, idx, add_output = next_state, idx+1, add_output+temp

            if open_cnt == 0:
                return idx, add_output
            return idx, None

        pre, cur, stack = self.pre, self.cur, self.stack
        add_output = cur.value

        if (cur.is_prefix() and (cur.value not in {'+', '-'} or (
                isinstance(pre, (java_lexer.Separator, java_lexer.Keyword, java_lexer.Operator))
                and pre.value != ')'))):
            if (cur.value not in {'++', '--'} or (
                    isinstance(tokens[self.idx+1], (java_lexer.Identifier, java_lexer.Literal))
                    or tokens[self.idx+1].value == '(')):
                add_output += (' ' if space_around_unary else '')

        else:
            flag = False
            if cur.is_assignment(): flag = space_around_assignment
            elif cur.value in ('==', '!='): flag = space_around_equality
            elif cur.value in ('<', '>', '<=', '>='):
                if cur.value == '<':
                    idx, res = _consume_template(self.idx + 1)
                    if res:
                        # new Type<...>
                        self.idx = idx - 1
                        if (idx < len(tokens) and isinstance(tokens[idx], java_lexer.Identifier)
                                and isinstance(pre, java_lexer.Identifier)):
                            res += ' '
                        return res

                flag = space_around_relational
            elif cur.value in ('&&', '||'): flag = space_around_logical
            elif cur.value in ('<<', '>>', '>>>'): flag = space_around_shift
            elif cur.value == '::': flag = space_around_method_reference
            elif cur.value in ('&', '|', '^'): flag = space_around_bitwise
            elif cur.value == '->': flag = space_around_lambda_arrow
            elif cur.value in ('+', '-'): flag = space_around_additive
            elif cur.value == ':':
                if stack[-1].value == 'for':
                    flag = space_around_colon_for_each

                elif stack[-1].value == '?':
                    flag = space_around_ternary
                    stack.pop()

                elif stack[-1].value in ('case', 'default'):
                    if tokens[self.idx+1].value != '{':
                        self.indent_level += 1
                        self.need_indent_flag = True
                        add_output += '\n'
                        stack[-1] = cur

                    else:
                        if brace_other == 'new_line':
                            self.need_indent_flag = True
                            add_output += '\n'
                        else:
                            add_output += ' '

                elif stack[-1].value == 'assert':
                    flag = True
                    stack.pop()


            elif cur.value == '?':
                stack.append(cur)
                flag = space_around_ternary

            else:
                flag = space_around_operator

            if flag: add_output = ' ' + cur.value + ' '

        return add_output

'''
-------------(-------------
    1. new,(
    2. p_keyword
    3. Identifier
    4. (

-------------)--------------
 2->5. p_keyword,)
 2->6. p_keyword,'indent'
 3->7. Identifier,)
 3->8. Identifier,throws
 1->9. new,class
1->10. nothing
4->11. nothing

--------------[--------------
    12. []

-----------------------------
    13. class, interface
    15. assert
    26. case, default
    27. @
--------------{--------------
12->16. [],{
27->17. @, {
    18. b_keyword,{
 5->19. p_keyword,{
 7->20. Identifier,{
 9->21. new,class,{
13->22. class,{
    23. ->
 8->24. Identifier,{
    25. {
 
-------------}---------------
'''