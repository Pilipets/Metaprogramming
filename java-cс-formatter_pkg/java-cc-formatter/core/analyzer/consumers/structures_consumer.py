from . import java_tokens

class TemplateStruct:
    def __init__(self, names, str):
        self._names = names
        self._str = str

    def __str__(self):
        return self._str

class AnnotationStruct():
    def __init__(self, name):
        self._name = name

    def __str__(self):
        return f'@{self._name}'

class AnnotationInvocationsStruct:
    def __init__(self, annotations):
        self._annotations = annotations

    def __str__(self):
        return ', '.join(str(x) for x in self._annotations)

class VarTypeStruct:
    def __init__(self, name, templ, is_array):
        self._name = name
        self._templ = templ
        self._is_array = is_array

    def __str__(self):
        res = self._name
        if self._templ: res += f' {self._templ}'
        if self._is_array: res += ' [...]'
        return res

class StructuresConsumer:
    def __init__(self):
        self.consume_res = None

    @classmethod
    def get_consumer(cls):
        return cls()

    def get_consume_res(self):
        return self.consume_res

    def try_stacked_chars(self, chars : str, idx, tokens):
        self.consume_res = None
        if len(chars) != 2: return False

        start_ch, end_ch = chars[0], chars[1]
        if idx >= len(tokens) or tokens[idx].value != start_ch:
            return False
        
        cnt, idx = 1, idx + 1
        while idx < len(tokens) and cnt > 0:
            if tokens[idx].value == start_ch: cnt += 1
            elif tokens[idx].value == end_ch: cnt -= 1
            idx += 1
            
        if cnt == 0:
            self.consume_res = (None, idx)
            return True

        return False

    def try_instances(self, type, idx, tokens):
        self.consume_res = None
        res = []

        while idx < len(tokens) and isinstance(tokens[idx], type):
            res.append(tokens[idx].value)
            idx += 1

        if not res: return False

        self.consume_res = (res, idx)
        return True

    def try_outer_identifier(self, idx, tokens):
        self.consume_res = None

        state = 1
        while idx < len(tokens):
            cur, next_state = tokens[idx], None

            if state == 1:
                if isinstance(cur, java_tokens.Identifier): next_state = 2

            elif state == 2:
                if cur.value == '.': next_state = 1

            if next_state is None: break
            idx, state = idx+1, next_state

        if state != 2: return False

        self.consume_res = (tokens[idx-1].value, idx)
        return True

    def try_annotation_declaration(self, idx, tokens):
        self.consume_res = None
        if idx + 2 >= len(tokens): return False

        annotation = None
        if (isinstance(tokens[idx], java_tokens.Annotation)
                and tokens[idx+1].value == 'interface'
                    and isinstance(tokens[idx+2], java_tokens.Identifier)):
            annotation = AnnotationStruct(tokens[idx+2].value)

        if not annotation: return False
        self.consume_res = (annotation, idx+3)
        return True

    def try_anotation_invocations(self, idx, tokens):
        self.consume_res = None

        annotations = []
        while idx+1 < len(tokens):
            if (isinstance(tokens[idx], java_tokens.Annotation)
                    and self.try_outer_identifier(idx+1, tokens)):
                name, idx = self.consume_res
                annotations.append(name)

            else:
                break

            if self.try_stacked_chars('()', idx, tokens):
                idx = self.consume_res[-1]

        if not annotations: return False

        annotations = AnnotationInvocationsStruct(annotations)
        self.consume_res = (annotations, idx)
        return True
    
    def try_template_declaration(self, idx, tokens):
        '''In classes or template methods'''
        self.consume_res = None
        if idx >= len(tokens): return False

        start, names = idx, [] # declared names
        if tokens[idx].value != '<': return False

        idx += 1
        # Simple automata to handle complex cases
        open_cnt, state = 1, 1
        while idx < len(tokens) and open_cnt > 0:
            next_state, cur = None, tokens[idx]

            if state == 1:
                if isinstance(cur, java_tokens.Identifier):
                    names.append(cur.value)
                    next_state = 2

            elif state == 2:
                if cur.value in ('extends', 'super'): next_state = 3
                elif cur.value == ',': next_state = 1
                elif cur.value == '>': next_state, open_cnt = 5, open_cnt-1

            elif state == 3:
                if self.try_anotation_invocations(idx, tokens):
                    idx = self.consume_res[-1]

                    if self.try_outer_identifier(idx, tokens):
                        idx = self.consume_res[-1]-1
                        next_state = 4


                elif self.try_outer_identifier(idx, tokens):
                        idx = self.consume_res[-1]-1
                        next_state = 4
                
            elif state == 4:
                if cur.value == '&': next_state = 3
                elif cur.value == ',': next_state = 1
                elif cur.value == '>': next_state, open_cnt = 5, open_cnt-1
                elif self.try_template_invocation(idx, tokens):
                    idx = self.consume_res[-1]-1
                    next_state = 4

            elif state == 5:
                if cur.value == '>': next_state, open_cnt = 5, open_cnt-1

            if next_state is None: break
            state, idx = next_state, idx+1

        if open_cnt != 0: return False

        tmpl = TemplateStruct(names, ' '.join(x.value for x in tokens[start:idx]))
        self.consume_res = (tmpl, idx)
        return True

    def try_template_invocation(self, idx, tokens):
        self.consume_res = None
        if idx >= len(tokens): return False

        start, names = idx, [] # for TemplateStructCreation
        if tokens[idx].value != '<': return False

        idx += 1
        if idx < len(tokens) and tokens[idx].value == '>':
            tmpl = TemplateStruct([], '<>')
            self.consume_res = tmpl, idx+1
            return True

        # Simple automata to handle complex cases
        open_cnt, state = 1, 1
        while idx < len(tokens) and open_cnt > 0:
            next_state, cur = None, tokens[idx]

            if state == 1:
                if cur.value == '?': next_state = 2
                elif isinstance(cur, java_tokens.BasicType):
                    names.append(cur.value)
                    next_state = 8

                elif self.try_anotation_invocations(idx, tokens):
                    idx = self.consume_res[-1]

                    if self.try_outer_identifier(idx, tokens):
                        name, idx = self.consume_res
                        names.append(name)

                        idx -= 1
                        next_state = 4

                elif self.try_outer_identifier(idx, tokens):
                        name, idx = self.consume_res
                        names.append(name)

                        idx -= 1
                        next_state = 4

            elif state == 2:
                if cur.value == ',': next_state = 1
                elif cur.value == '>': next_state, open_cnt = 5, open_cnt-1
                elif cur.value in ('extends', 'super'): next_state = 9
                
            elif state == 4:
                if cur.value == '<': next_state, open_cnt = 1, open_cnt+1
                elif cur.value == '>': next_state, open_cnt = 5, open_cnt-1
                elif cur.value == ',': next_state = 1
                elif cur.value == '[': next_state = 7

            elif state == 5:
                if cur.value == '>': next_state, open_cnt = 5, open_cnt-1
                elif cur.value == '[': next_state = 7
                elif cur.value == ',': next_state = 1

            elif state == 7:
                if cur.value == ']': next_state = 5

            elif state == 8:
                if cur.value == '[': next_state = 7

            elif state == 9:
                if self.try_anotation_invocations(idx, tokens):
                    idx = self.consume_res[-1]

                    if self.try_outer_identifier(idx, tokens):
                        idx = self.consume_res[-1]-1
                        next_state = 4

                elif self.try_outer_identifier(idx, tokens):
                        idx = self.consume_res[-1]-1
                        next_state = 4

            if next_state is None: break
            state, idx = next_state, idx+1

        if open_cnt != 0: return False

        tmpl = TemplateStruct(names, ' '.join(x.value for x in tokens[start:idx]))
        self.consume_res = (tmpl, idx)
        return True

    def try_var_type(self, idx, tokens):
        allowed_templates = False

        if self.try_outer_identifier(idx, tokens):
            idx = self.consume_res[-1] - 1
            allowed_templates = True

        elif isinstance(tokens[idx], java_tokens.BasicType):
            allowed_templates = False

        else:
            return False

        type_name = tokens[idx].value
        idx += 1

        templ = None
        if allowed_templates and self.try_template_invocation(idx, tokens):
            templ, idx = self.consume_res

        is_array = False
        while idx + 1 < len(tokens) and tokens[idx].value == '[' and tokens[idx+1].value == ']':
            is_array = True
            idx += 2

        var_type_struct = VarTypeStruct(type_name, templ, is_array)
        self.consume_res = (var_type_struct, idx)
        return True