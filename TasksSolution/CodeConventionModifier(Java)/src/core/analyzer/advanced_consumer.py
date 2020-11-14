from .structures_consumer import *
from ...core.tokenizer import java_lexer

class MultiVarStruct:
    def __init__(self, var_type, var_names):
        self._type = var_type
        self._names = var_names

    def __str__(self):
        res = "%s %s" % (self._type, ', '.join(self._names))
        return res

class MethodStruct:
    def __init__(self, templ, var_type, name, params):
        self._type = var_type
        self._name = name
        self._params = params
        self._templ = templ

    def __str__(self):
        res = f'{self._type} {self._name} ('
        if self._templ: res = f'{self._templ} ' + res
        if self._params: res += ', '.join(str(x) for x in self._params)
        res += ')'
        return res

class AdvancedStructuresConsumer(StructuresConsumer):
    def try_multiple_vars_declaration(self, idx, tokens):
        if not self.try_var_type(idx, tokens): return False
        var_type, idx = self.consume_res

        var_names = []
        state = 1
        while idx < len(tokens) and state > 0:
            next_state = None

            if state == 1:
                if isinstance(tokens[idx], java_lexer.Identifier):
                    var_names.append(tokens[idx].value)
                    next_state = 2

            elif state == 2:
                if tokens[idx].value == ',': next_state = 1
                elif tokens[idx].value == ';': idx, next_state = idx-1, 0
                elif tokens[idx].value == '=': next_state = 3
                # Treated specially to recognize (...) declaration
                elif tokens[idx].value == ')': idx, next_state = idx-1, 0

            elif state == 3:
                if tokens[idx].value == ';': idx, next_state = idx-1, 0
                # Treated specially to recognize (...) declaration
                elif tokens[idx].value == ')': idx, next_state = idx-1, 0
                elif tokens[idx].value == ',': next_state = 1
                elif self.try_template_invocation(idx, tokens):
                    idx = self.consume_res[-1] - 1
                    next_state = 3

                elif tokens[idx].value == '(':
                    cnt, idx = 1, idx + 1
                    while idx < len(tokens) and cnt > 0:
                        if tokens[idx].value == '(': cnt += 1
                        elif tokens[idx].value == ')': cnt -= 1
                        idx += 1

                    if cnt == 0:
                        next_state = 3
                        idx -= 1

                else: next_state = 3

            if next_state is None: break
            idx, state = idx+1, next_state

        if state != 0: return False

        multi_var_struct = MultiVarStruct(var_type, var_names)
        self.consume_res = (multi_var_struct, idx)
        return True

    def try_method_declaration(self, idx, tokens):

        # This should be replaced with another templates reader
        templ = None
        if self.try_template_declaration(idx, tokens):
            templ, idx = self.consume_res

        method_type = None
        if self.try_var_type(idx, tokens):
            method_type, idx = self.consume_res

        elif idx < len(tokens) and tokens[idx].value == 'void':
            method_type = VarTypeStruct('void', None, False)
            idx += 1

        else:
            return False

        method_name = None
        if idx < len(tokens) and isinstance(tokens[idx], java_lexer.Identifier):
            method_name = tokens[idx].value
            idx += 1

        else:
            return False

        if idx < len(tokens) and tokens[idx].value == '(':
            idx += 1

        else:
            return False

        params = []
        state = 1
        while idx < len(tokens) and state > 0:
            next_state = None

            if state == 1:
                if tokens[idx].value == ')': next_state = 0
                elif self.try_var_single_declaration(idx, tokens):
                    var, idx = self.consume_res
                    params.append(var)
                    idx -= 1
                    next_state = 2

            elif state == 2:
                if tokens[idx].value == ',': next_state = 1
                elif tokens[idx].value == '=': next_state = 3
                elif tokens[idx].value == ')': next_state = 0

            elif state == 3:
                if tokens[idx].value == ',': next_state = 1
                elif tokens[idx].value == ')': next_state = 0
                elif self.try_template_invocation(idx, tokens):
                    temp, end = self.consume_res
                    idx = self.consume_res[-1] - 1
                    next_state = 3

                elif tokens[idx].value == '(':
                    inner_cnt, idx = 1, idx + 1
                    while idx < len(tokens) and inner_cnt > 0:
                        if tokens[idx].value == '(': inner_cnt += 1
                        elif tokens[idx].value == ')': inner_cnt -= 1
                        idx += 1

                    if inner_cnt == 0:
                        next_state = 2
                        idx -= 1

                else: next_state = 3

            if next_state is None: break
            idx, state = idx+1, next_state

        if state != 0: return False

        method_struct = MethodStruct(templ, method_type, method_name, params)
        self.consume_res = (method_struct, idx)
        return True
