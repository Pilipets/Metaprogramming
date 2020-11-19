from .structures_consumer import *
from ...core.tokenizer import java_lexer

class MethodStruct:
    def __init__(self, templ, var_type, name, params):
        self._type = var_type
        self._name = name
        self._params = params
        self._templ = templ

    def __str__(self):
        res = f'{self._name} ('
        if self._type: res += f'{self._type} '
        if self._templ: res = f'{self._templ} ' + res
        if self._params: res += ', '.join(str(x) for x in self._params)
        res += ')'
        return res

class AnnotationStruct(ClassStruct):
    def __init__(self, name):
        super().__init__(name, None)

class AnnotationInvocationsStruct:
    def __init__(self, annotations):
        self._annotations = annotations

    def __str__(self):
        return ', '.join(str(x) for x in self._annotations)

class AdvancedStructuresConsumer(StructuresConsumer):
    # Notice this might be object creation with initialization as well
    def try_anonymous_class(self, idx, tokens):
        self.consume_res = None

        if (idx + 2 < len(tokens) and tokens[idx].value == 'new'
                and isinstance(tokens[idx+1], java_lexer.Identifier)):
            idx += 2
        else:
            return False

        if self.try_template_invocation(idx, tokens):
            idx = self.consume_res[-1]

        if self.try_stacked_chars('()', idx, tokens):
            idx = self.consume_res[-1]
        else:
            return False

        res = False
        if idx < len(tokens) and tokens[idx].value == '{':
            idx += 1
            res = True

        if not res: return False

        self.consume_res = (res, idx)
        return True

    def try_annotation_declaration(self, idx, tokens):
        self.consume_res = None
        if idx + 2 >= len(tokens): return False

        annotation = None
        if (isinstance(tokens[idx], java_lexer.Annotation)
                and tokens[idx+1].value in ('class', 'interface')
                    and isinstance(tokens[idx+2], java_lexer.Identifier)):
            annotation = AnnotationStruct(tokens[idx+2])

        if not annotation: return False
        cls.consume_res = (annotation, idx+3)
        return True

    def try_anotation_invocations(self, idx, tokens):
        self.consume_res = None

        annotations = []
        while idx+1 < len(tokens):
            if (isinstance(tokens[idx], java_lexer.Annotation)
                    and self.try_outer_identifier(idx+1, tokens)):
                name, idx = self.consume_res
                annotations.append(AnnotationStruct(name))

            else:
                break

            if self.try_stacked_chars('()', idx, tokens):
                idx = self.consume_res[-1]

        if not annotations: return False

        annotations = AnnotationInvocationsStruct(annotations)
        self.consume_res = (annotations, idx)
        return True
   
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

                elif (self.try_stacked_chars('()', idx, tokens)
                      or self.try_stacked_chars('{}', idx, tokens)):
                    idx = self.consume_res[-1] - 1
                    next_state = 3

                else: next_state = 3

            if next_state is None: break
            idx, state = idx+1, next_state

        if state != 0: return False

        multi_var_struct = MultiVarStruct(var_type, var_names)
        self.consume_res = (multi_var_struct, idx)
        return True

    def try_method_declaration(self, idx, tokens):
        templ = None
        if self.try_template_declaration(idx, tokens):
            templ, idx = self.consume_res

        start = idx # We need to later consider method without the type
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

        # Constructor
        elif (idx < len(tokens) and idx-1 == start
                and isinstance(tokens[idx-1], java_lexer.Identifier)):
            method_name = method_type._name
            method_type = None

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
                elif (tokens[idx].value == 'final' and self.try_var_single_declaration(idx+1, tokens)):
                    var, idx = self.consume_res
                    params.append(var)
                    idx -= 1
                    next_state = 2

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
                    idx = self.consume_res[-1] - 1
                    next_state = 3

                elif (self.try_stacked_chars('()', idx, tokens)
                      or self.try_stacked_chars('{}', idx, tokens)):
                    idx = self.consume_res[-1] - 1
                    next_state = 3

                else: next_state = 3

            if next_state is None: break
            idx, state = idx+1, next_state

        if state != 0: return False

        method_struct = MethodStruct(templ, method_type, method_name, params)
        self.consume_res = (method_struct, idx)
        return True
