from ...core.tokenizer import java_lexer

class ModifierError(Exception):
    pass

class ConventionNaming:
    @staticmethod
    def get_constant_name(name : str):
        # convention_name: ([A-Z]+(_[A-Z]+)*
        res = ''
        x, idx = name, 0

        while idx < len(x):
            ch, start = x[idx], idx
            if ch in '_$':
                while idx < len(x) and x[idx] in '_$': idx += 1
                start = idx

            elif ch.islower():
                while idx < len(x) and x[idx].islower(): idx += 1

            elif ch.isupper():
                while idx < len(x) and x[idx].isupper(): idx += 1
                while idx < len(x) and x[idx].islower(): idx += 1

            res += x[start:idx].upper()
            if idx != len(x): res += '_'
        return res

    @staticmethod
    def get_class_name(name : str):
        # convention_name: ([A-Z][a-z]*)+
        res = ''
        x, idx = name, 0

        while idx < len(x):
            ch, start = x[idx], idx
            if ch in '_$':
                while idx < len(x) and x[idx] in '_$': idx += 1
                start = idx

            elif ch.islower():
                while idx < len(x) and x[idx].islower(): idx += 1
                res += x[start].upper() + x[start+1:idx]

            elif ch.isupper():
                idx += 1
                while idx < len(x) and x[idx].islower(): idx += 1
                res += x[start:idx]
            
        return res

    @staticmethod
    def get_method_name(name : str):
        return get_variable_name(name)

    @staticmethod
    def get_variable_name(name : str):
        res = ''
        x, idx = name, 0

        while idx < len(x):
            ch, start = x[idx], idx
            if ch in '_$':
                while idx < len(x) and x[idx] in '_$': idx += 1
                start = idx

            elif ch.islower():
                while idx < len(x) and x[idx].islower(): idx += 1
                if not res: res = x[start:idx]
                else: res += x[start].upper() + x[start+1:idx]

            elif ch.isupper():
                idx += 1
                while idx < len(x) and x[idx].islower(): idx += 1
                if not res: res = x[start].lower() + x[start+1:idx]
                else: res += x[start:idx]

        return res


class StructuresConsumer:
    idx = 0
    consume_res = None

    @classmethod
    def get_consume_res(cls):
        return cls.consume_res

    @classmethod
    def try_template(cls, idx, tokens, check_first = False):
        cls.consume_res = None
        if check_first and not isinstance(tokens[idx], java_lexer.Identifier):
            return False

        idx += 1
        if idx < len(tokens) and tokens[idx].value == '>':
            cls.consume_res = idx+1,
            return True

        # Simple automata to handle complex cases
        open_cnt, state = 1, 1
        while idx < len(tokens) and state > 0 and open_cnt > 0:
            next_state, cur = -1, tokens[idx]

            if state == 1:
                if cur.value == '?': next_state = 2
                elif isinstance(cur, java_lexer.Identifier): next_state = 4
                elif isinstance(cur, java_lexer.SimpleType): next_state = 5

            elif state == 2:
                if cur.value in ('extends', 'super'): next_state = 3
                elif cur.value == ',': next_state = 1
                elif cur.value == '>': next_state, open_cnt = 5, open_cnt-1

            elif state == 3:
                if isinstance(cur, java_lexer.Identifier): next_state = 4
                elif isinstance(cur, java_lexer.SimpleType): next_state = 4
                
            elif state == 4:
                if cur.value in ('extends', 'super'): next_state = 3
                elif cur.value == '<': next_state, open_cnt = 1, open_cnt+1
                elif cur.value == '>': next_state, open_cnt = 5, open_cnt-1
                elif cur.value == ',': next_state = 1
                elif cur.value == '&': next_state = 3
                elif cur.value == '.': next_state = 6
                elif cur.value == '[': next_state = 7

            elif state == 5:
                if cur.value == '>': next_state, open_cnt = 5, open_cnt-1
                elif cur.value == '[': next_state = 7
                elif cur.value == ',': next_state = 1

            elif state == 6:
                if isinstance(cur, java_lexer.Identifier): next_state = 4

            elif state == 7:
                if cur.value == ']': next_state = 5

            state, idx = next_state, idx+1

        if open_cnt != 0: return False
        cls.consume_res = idx,
        return True

    @classmethod
    def try_var_declaration(cls, idx, tokens, check_first = True):
        cls.consume_res = None
        if check_first and not isinstance(tokens[idx], java_lexer.Identifier):
            return False

        start, end = idx, None
        cls.idx = idx + 1

        if tokens[cls.idx].value == '<':
            if StructuresConsumer.try_template(cls.idx, tokens, False):
                cls.idx = cls.consume_res[-1]

        if (cls.idx + 1 < len(tokens)
            and tokens[cls.idx].value == '[' and tokens[cls.idx+1].value == ']'):
            cls.idx += 2

        if cls.idx < len(tokens) and isinstance(tokens[cls.idx], java_lexer.Identifier):
            end = cls.idx + 1

        if not end: return False
        cls.consume_res = (tokens[start].value, tokens[end-1].value, end)
        return True

    @classmethod
    def try_void_method_declaration(cls, idx, tokens, check_first = True):
        cls.consume_res = None
        if check_first and not tokens[idx].value == 'void':
            return False
        
        idx += 1
        if (idx + 1 < len(tokens)
                and isinstance(tokens[idx], java_lexer.Identifier)
                    and tokens[idx+1].value == '('):

            cls.consume_res = ('void', tokens[idx].value, idx + 2)
            return True

        return False

    @classmethod
    def try_simple_method_declaration(cls, idx, tokens, check_first = True):
        cls.consume_res = None
        if check_first and not isinstance(tokens[idx], java_lexer.SimpleType):
            return False
        
        start, idx = idx, idx+1
        if (idx + 1 < len(tokens)
                and isinstance(tokens[idx], java_lexer.Identifier)
                    and tokens[idx+1].value == '('):

            cls.consume_res = (tokens[start].value, tokens[idx+1].value, idx+2)
            return True

        return False

    @classmethod
    def try_class_declaration(cls, idx, tokens, check_first = True):
        cls.consume_res = None
        if check_first and not tokens[idx].value in ('class', 'interface'):
            return False

        idx += 1
        if (idx < len(tokens)
                and isinstance(tokens[idx], java_lexer.Identifier)):

            cls.consume_res = (tokens[idx].value, idx + 1)
            return True

        return False

