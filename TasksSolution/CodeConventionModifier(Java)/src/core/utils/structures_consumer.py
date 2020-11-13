from ...core.tokenizer import java_lexer

class StructuresConsumer:
    idx = 0
    consume_res = None

    @classmethod
    def get_consume_res(cls):
        return cls.consume_res

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

    @classmethod
    def try_class_const_declaration(cls, idx, tokens):
        cls.consume_res = None
        if tokens[idx].value not in ('static', 'final'): return False

        # if static then final, otherwise static
        term_token = 'final' if (tokens[idx].value == 'static') else 'static'
        
        idx += 1
        while idx < len(tokens) and isinstance(tokens[idx], java_lexer.Keyword):
            if term_token and tokens[idx].value == term_token:
                term_token = None
            idx += 1

        if term_token: return False

        start, end = idx, None
        if cls.try_var_declaration(idx, tokens):
            end = cls.consume_res[-1]

        if not end: return False
        cls.consume_res = (tokens[start].value, tokens[end-1].value, end)
        return True

    @classmethod
    def try_var_declaration(cls, idx, tokens, check_first = True):
        cls.consume_res = None
        allowed_templates = True

        if check_first:
            if isinstance(tokens[idx], java_lexer.Identifier):
                allowed_templates = True

            elif isinstance(tokens[idx], java_lexer.SimpleType):
                allowed_templates = False

            else:
                return False

        start, end = idx, None
        idx += 1

        if allowed_templates and tokens[idx].value == '<':
            if StructuresConsumer.try_template(idx, tokens, False):
                idx = cls.consume_res[-1]

        if (idx + 1 < len(tokens)
            and tokens[idx].value == '[' and tokens[idx+1].value == ']'):
            idx += 2

        if idx < len(tokens) and isinstance(tokens[idx], java_lexer.Identifier):
            end = idx+1

        if not end: return False
        cls.consume_res = (tokens[start].value, tokens[end-1].value, end)
        return True

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
    def try_void_method_declaration(cls, idx, tokens, check_first = True):
        cls.consume_res = None
        if check_first and not tokens[idx].value == 'void':
            return False
        
        start, end = idx, None
        idx += 1
        if (idx + 1 < len(tokens)
                and isinstance(tokens[idx], java_lexer.Identifier)
                    and tokens[idx+1].value == '('):

            end = idx+2

        if not end: return False
        cls.consume_res = (tokens[start].value, tokens[end-2].value, end)
        return True

    @classmethod
    def try_simple_method_declaration(cls, idx, tokens, check_first = True):
        cls.consume_res = None
        if check_first and not isinstance(tokens[idx], java_lexer.SimpleType):
            return False
        
        start, end = idx, None
        idx += 1
        if (idx + 1 < len(tokens)
            and tokens[idx].value == '[' and tokens[idx+1].value == ']'):
            idx += 2

        if (idx + 1 < len(tokens)
                and isinstance(tokens[idx], java_lexer.Identifier)
                    and tokens[idx+1].value == '('):
            end = idx+2

        if not end: return False
        cls.consume_res = (tokens[start].value, tokens[end-2].value, end)
        return True

