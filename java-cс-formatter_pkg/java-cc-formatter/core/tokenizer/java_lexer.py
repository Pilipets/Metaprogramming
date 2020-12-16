import re

from .java_tokens import *

def tokenize(code, raise_errors=True):
    return JavaLexer(code, raise_errors).tokenize()

class LexerError(Exception):
    pass

class JavaLexer():
    def __init__(self, input_data, raise_errors=True):
        self.data = input_data
        self.raise_errors = raise_errors
        self.errors = []

        self.current_line, self.start_of_line = 1, -1
        self.idx, self.next_idx = 0, 0
        self.length = len(self.data)
        self.javadoc = None
        self.current_column = 1

        # categorize operators by their length
        self.operators_by_len = [set() for _ in range(Operator.MAX_LEN)]
        for op_ in Operator.VALUES_SET:
            self.operators_by_len[len(op_) - 1].add(op_)

        self.whitespace_matcher = re.compile(r'[^\s]')

    def report_error(self, message, char=None):
        line_number = self.current_line
        if not char:
            char = self.data[self.next_idx]

        start_line = self.data.rfind('\n', 0, self.idx) + 1
        end_line = self.data.find('\n', self.idx)
        line = self.data[start_line:end_line].strip()

        message = '"%s" at %s, position %d: %s' % (message, char, line_number, line)
        self.errors.append(LexerError(message))

        if self.raise_errors:
            raise self.errors[-1]

    def _read_column_indent(self, idx, end_idx):
        for t_idx in range(idx, end_idx):
            if self.data[t_idx] == '\t':
                self.current_column += 4
                self.current_column -= (self.current_column - 1) % 4
            else:
                self.current_column += 1

    def tokenize(self):
        while self.idx < self.length:
            token_type = None

            ch_cur, ch_next = self.data[self.idx], None
            prefix = ch_cur

            if self.idx + 1 < self.length:
                ch_next = self.data[self.idx + 1]
                prefix += ch_next

            if ch_cur.isspace():
                self.read_whitespace()
                continue

            elif ch_cur in Separator.VALUES_SET:
                token_type = Separator
                self.next_idx = self.idx + 1

            elif prefix in ("//", "/*"):
                text, pos = self.read_comment()
                token_type = SingleLineComment if text[1] == '/' else MultiLineComment

                if text.startswith("/**"):
                    if self.javadoc: yield self.javadoc
                    self.javadoc = token_type(text, pos, None)
                else:
                    yield token_type(text, pos, self.javadoc)
                    self.javadoc = None
                continue

            elif prefix == '..' and self.read_operator():
                token_type = Operator

            elif ch_cur in ("'", '"'):
                token_type = Literal
                self.read_string()

            elif ch_cur.isdigit():
                token_type = self.read_integer_or_float(ch_cur, ch_next)

            elif ch_cur == '@':
                token_type = Annotation
                self.next_idx = self.idx + 1

            elif ch_cur == '.' and ch_next and ch_next.isdigit():
                token_type = self.read_decimal_float_or_integer()

            elif ch_cur.isalpha() or ch_cur in '_$':
                token_type = self.read_identifier_or_reserved()

            elif self.read_operator():
                token_type = Operator

            else:
                self.report_error('Unknown token', ch_cur)
                self.idx += 1
                continue

            position = Position(self.current_line, self.current_column)
            token = token_type(self.data[self.idx:self.next_idx], position, self.javadoc)
            yield token

            self.javadoc = None
            self.current_column += self.next_idx - self.idx
            self.idx = self.next_idx

        if self.javadoc: yield self.javadoc

    def read_whitespace(self):
        match_obj = self.whitespace_matcher.search(self.data, self.idx + 1)

        if not match_obj:
            self.idx = self.length
            return 0

        idx = match_obj.start()
        start_of_line = self.data.rfind('\n', self.idx, idx)

        if start_of_line != -1:
            self.current_line += self.data.count('\n', self.idx, idx)
            self.current_column = 1

        self._read_column_indent(max(start_of_line+1, self.idx), idx)

        self.idx = idx

    def read_string(self):
        delim = self.data[self.idx]
        state = 0

        for next_idx in range(self.idx + 1, self.length):
            if state == 0:
                if self.data[next_idx] == '\\': state = 1
                elif self.data[next_idx] == delim: break

            elif state == 1:
                if self.data[next_idx] in 'btnfru"\'\\': state = 0
                elif self.data[next_idx] in '0123': state = 2
                elif self.data[next_idx] in '01234567': state = 3
                else: self.report_error('Illegal character in string', self.data[next_idx])

            elif state == 2:
                # Possibly long octal
                if self.data[next_idx] in '01234567': state = 3
                elif self.data[next_idx] == '\\': state = 1
                elif self.data[next_idx] == delim: break

            elif state == 3:
                if self.data[next_idx] == '\\': state = 1
                elif self.data[next_idx] == delim: break
                else: state = 0

        if next_idx == self.length:
            self.report_error('Unfinished string literal')

        self.next_idx = next_idx + 1

    def read_operator(self):
        # try matching starting from largest len
        for op_len in range(min(self.length - self.idx, Operator.MAX_LEN), 0, -1):
            try_op = self.data[self.idx : self.idx + op_len]
            if try_op in self.operators_by_len[op_len - 1]:
                self.next_idx = self.idx + op_len
                return True
        return False

    def read_comment(self):
        if self.data[self.idx + 1] == '/': term = '\n', True
        else: term = '*/', False

        idx = self.data.find(term[0], self.idx + 2)

        if idx != -1:
            idx += len(term[0])
        elif term[1]:
            # accepts end of file
            idx = self.length
        else:
            self.report_error('Unfinished comment block')
            comment = self.data[self.idx:]
            self.idx = self.length
            return comment, Position(self.current_line, self.current_column)

        comment = self.data[self.idx:idx]
        position = Position(self.current_line, self.current_column)

        start_of_line = self.data.rfind('\n', self.idx, idx)
        if start_of_line != -1:
            self.start_of_line = start_of_line
            self.current_line += self.data.count('\n', self.idx, idx)
            self.current_column = 1

        self._read_column_indent(max(start_of_line+1, self.idx), idx)
        self.idx = idx
        return comment, position

    def read_decimal_float_or_integer(self):
        initial_i = self.idx
        self.next_idx = self.idx

        self.read_from_set('0123456789')

        if self.next_idx >= self.length or self.data[self.next_idx] not in '.eEfFdD':
            return Literal

        if self.data[self.next_idx] == '.':
            self.idx = self.next_idx + 1
            self.next_idx = self.idx
            self.read_from_set('0123456789')

        if self.next_idx < self.length and self.data[self.next_idx] in 'eE':
            self.next_idx = self.next_idx + 1

            if self.next_idx < self.length and self.data[self.next_idx] in '-+':
                self.next_idx = self.next_idx + 1

            self.idx = self.next_idx
            self.read_from_set('0123456789')

        if self.next_idx < self.length and self.data[self.next_idx] in 'fFdD':
            self.next_idx = self.next_idx + 1

        self.idx = initial_i
        return Literal

    def read_hex_integer_or_float(self):
        initial_i = self.idx

        self.next_idx = self.idx + 2
        self.read_from_set('0123456789abcdefABCDEF')

        if self.next_idx >= self.length or self.data[self.next_idx] not in '.pP':
            return Literal

        if self.data[self.next_idx] == '.':
            self.next_idx = self.next_idx + 1
            self.read_from_set('0123456789abcdefABCDEF')

        if self.next_idx < self.length and self.data[self.next_idx] in 'pP':
            self.next_idx = self.next_idx + 1
        else:
            self.report_error('Invalid number literal')

        if self.next_idx < self.length and self.data[self.next_idx] in '-+':
            self.next_idx = self.next_idx + 1

        self.idx = self.next_idx
        self.read_from_set('0123456789')

        if self.next_idx < self.length and self.data[self.next_idx] in 'fFdD':
            self.next_idx = self.next_idx + 1

        self.idx = initial_i
        return Literal

    def read_from_set(self, ch_set):
        ch_cur = None

        for tmp_idx in range(self.next_idx, self.length):
            ch_cur = self.data[tmp_idx]

            if ch_cur == '_': pass
            elif ch_cur in ch_set: self.next_idx = tmp_idx + 1
            else: break

        if ch_cur in 'lL': # long suffix
            self.next_idx += 1

    def read_integer_or_float(self, ch_cur, ch_next):
        if ch_cur == '0' and ch_next in 'xX':
            return self.read_hex_integer_or_float()

        if ch_cur == '0' and ch_next in 'bB':
            self.next_idx = self.idx + 2
            self.read_from_set('01')
            return Literal

        if ch_cur == '0' and ch_next in '01234567':
            self.next_idx = self.idx + 1
            self.read_from_set('01234567')
            return Literal

        return self.read_decimal_float_or_integer()

    def read_identifier_or_reserved(self):
        self.next_idx = self.idx + 1

        while self.next_idx < self.length:
            ch_cur = self.data[self.next_idx]
            if ch_cur.isalnum() or ch_cur in '$_':
                self.next_idx += 1
            else:
                break

        res = self.data[self.idx:self.next_idx]

        token_type = Identifier
        if res in Keyword.VALUES_SET:

            token_type = Keyword
            if res in BasicType.VALUES_SET:
                token_type = BasicType
            elif res in Modifier.VALUES_SET:
                token_type = Modifier

        elif res in {'true', 'false', 'null'}:
            # For the moment it doesn't matter
            token_type = Literal

        return token_type