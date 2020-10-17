import re
import unicodedata

from .java_tokens import *

class LexerError(Exception):
    pass

class JavaLexer():
    def __init__(self, input_data, raise_errors=True):
        self.data = input_data
        self.raise_errors = raise_errors
        self.errors = []

        self.current_line, self.start_of_line = 1, -1

        # categorize operators by their length
        self.operators = [set() for _ in range(Operator.MAX_LEN)]
        for v in Operator.VALUES:
            self.operators[len(v) - 1].add(v)

        self.whitespace_matcher = re.compile(r'[^\s]')

    def report_error(self, message, char=None):
        start_line = self.data.rfind('\n', 0, self.idx) + 1
        end_line = self.data.find('\n', self.idx)
        line = self.data[start_line:end_line].strip()

        line_number = self.current_line

        if not char:
            char = self.data[self.next_idx]

        message = '"%s" at %s, position %d: %d' % (message, char, line_number, line)
        self.errors.append(LexerError(message))

        if self.raise_errors:
            raise self.errors[-1]

    def tokenize(self):
        self.idx, self.next_idx = 0, 0
        self.length = len(self.data)

        while self.idx < self.length:
            token_type = None

            ch, ch_next = self.data[self.idx], None
            prefix = ch

            if self.idx + 1 < self.length:
                ch_next = self.data[self.idx + 1]
                prefix += ch_next


            if ch.isspace():
                self.read_whitespace()
                continue

            elif ch in Separator.VALUES:
                token_type = Separator
                self.next_idx = self.idx + 1

            elif prefix in ("//", "/*"):
                comment = self.read_comment()
                # Ignore comments for the moment
                continue

            elif prefix == '..' and self.read_operator():
                token_type = Operator

            elif ch in ("'", '"'):
                token_type = String
                self.read_string()

            elif ch.isdigit():
                token_type = self.read_integer_or_float(ch, ch_next)

            elif ch == '@':
                token_type = Annotation
                self.next_idx = self.idx + 1

            elif ch == '.' and ch_next and ch_next.isdigit():
                token_type = self.read_decimal_float_or_integer()

            elif ch.isalpha() or ch in '_$':
                token_type = self.read_identifier()

            elif self.read_operator():
                token_type = Operator

            else:
                self.report_error('Unknown token', ch)
                self.idx = self.idx + 1
                continue

            position = Position(self.current_line, self.idx - self.start_of_line)
            token = token_type(self.data[self.idx:self.next_idx], position)
            yield token

            self.idx = self.next_idx

    def read_whitespace(self):
        match_obj = self.whitespace_matcher.search(self.data, self.idx + 1)

        if not match_obj:
            self.idx = self.length
            return

        idx = match_obj.start()
        start_of_line = self.data.rfind('\n', self.idx, idx)

        if start_of_line != -1:
            self.start_of_line = start_of_line
            self.current_line += self.data.count('\n', self.idx, idx)

        self.idx = idx

    def read_string(self):
        delim = self.data[self.idx]

        state = 0
        next_idx = self.idx + 1
        length = self.length

        while True:
            if next_idx >= length:
                self.report_error('Unterminated character/string literal')
                break

            if state == 0:
                if self.data[next_idx] == '\\':
                    state = 1
                elif self.data[next_idx] == delim:
                    break

            elif state == 1:
                if self.data[next_idx] in 'btnfru"\'\\':
                    state = 0
                elif self.data[next_idx] in '0123':
                    state = 2
                elif self.data[next_idx] in '01234567':
                    state = 3
                else:
                    self.report_error('Illegal escape character', self.data[next_idx])

            elif state == 2:
                # Possibly long octal
                if self.data[next_idx] in '01234567':
                    state = 3
                elif self.data[next_idx] == '\\':
                    state = 1
                elif self.data[next_idx] == delim:
                    break

            elif state == 3:
                state = 0
                if self.data[next_idx] == '\\':
                    state = 1
                elif self.data[next_idx] == delim:
                    break

            next_idx += 1

        self.next_idx = next_idx + 1

    def read_operator(self):
        # try matching starting from largest len
        for l in range(min(self.length - self.idx, Operator.MAX_LEN), 0, -1):
            if self.data[self.idx:self.idx + l] in self.operators[l - 1]:
                self.next_idx = self.idx + l
                return True

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
            return comment

        comment = self.data[self.idx:idx]
        start_of_line = self.data.rfind('\n', self.idx, idx)

        if start_of_line != -1:
            self.start_of_line = start_of_line
            self.current_line += self.data.count('\n', self.idx, idx)

        self.idx = idx
        return comment

    def read_decimal_float_or_integer(self):
        initial_i = self.idx
        self.next_idx = self.idx

        self.read_decimal_integer()

        if self.next_idx >= len(self.data) or self.data[self.next_idx] not in '.eEfFdD':
            return DecimalInteger

        if self.data[self.next_idx] == '.':
            self.idx = self.next_idx + 1
            self.read_decimal_integer()

        if self.next_idx < len(self.data) and self.data[self.next_idx] in 'eE':
            self.next_idx = self.next_idx + 1

            if self.next_idx < len(self.data) and self.data[self.next_idx] in '-+':
                self.next_idx = self.next_idx + 1

            self.idx = self.next_idx
            self.read_decimal_integer()

        if self.next_idx < len(self.data) and self.data[self.next_idx] in 'fFdD':
            self.next_idx = self.next_idx + 1

        self.idx = initial_i
        return DecimalFloatingPoint

    def read_hex_integer_or_float(self):
        initial_i = self.idx

        self.next_idx = self.idx + 2
        self.read_digits('0123456789abcdefABCDEF')

        if self.next_idx >= len(self.data) or self.data[self.next_idx] not in '.pP':
            return HexInteger

        if self.data[self.next_idx] == '.':
            self.next_idx = self.next_idx + 1
            self.read_digits('0123456789abcdefABCDEF')

        if self.next_idx < len(self.data) and self.data[self.next_idx] in 'pP':
            self.next_idx = self.next_idx + 1
        else:
            self.report_error('Invalid hex float literal')

        if self.next_idx < len(self.data) and self.data[self.next_idx] in '-+':
            self.next_idx = self.next_idx + 1

        self.idx = self.next_idx
        self.read_decimal_integer()

        if self.next_idx < len(self.data) and self.data[self.next_idx] in 'fFdD':
            self.next_idx = self.next_idx + 1

        self.idx = initial_i
        return HexFloatingPoint

    def read_digits(self, digits):
        tmp_i = 0
        ch = None

        while self.next_idx + tmp_i < len(self.data):
            ch = self.data[self.next_idx + tmp_i]

            if ch in digits:
                self.next_idx += 1 + tmp_i
                tmp_i = 0
            elif ch == '_':
                tmp_i += 1
            else:
                break

        if ch in 'lL':
            self.next_idx += 1

    def read_decimal_integer(self):
        self.next_idx = self.idx
        self.read_digits('0123456789')

    def read_integer_or_float(self, ch, ch_next):
        if ch == '0' and ch_next in 'xX':
            return self.read_hex_integer_or_float()

        elif ch == '0' and ch_next in 'bB':
            self.next_idx = self.idx + 2
            self.read_digits('01')
            return BinaryInteger

        elif ch == '0' and ch_next in '01234567':
            self.next_idx = self.idx + 1
            self.read_digits('01234567')
            return OctalInteger

        else:
            return self.read_decimal_float_or_integer()

    def read_identifier(self):
        self.next_idx = self.idx + 1

        while self.next_idx < len(self.data) and (
            self.data[self.next_idx].isalpha() or self.data[self.next_idx].isdigit() or self.data[self.next_idx] in '$_'):
            self.next_idx += 1

        res = self.data[self.idx:self.next_idx]
        if res in Keyword.VALUES:
            token_type = Keyword

            if res in BasicType.VALUES:
                token_type = BasicType
            elif res in Modifier.VALUES:
                token_type = Modifier

        elif res in Boolean.VALUES:
            token_type = Boolean
        elif res == 'null':
            token_type = Null
        else:
            token_type = Identifier

        return token_type

def tokenize(code, raise_errors=True):
    lexer = JavaLexer(code, raise_errors)
    return lexer.tokenize()
