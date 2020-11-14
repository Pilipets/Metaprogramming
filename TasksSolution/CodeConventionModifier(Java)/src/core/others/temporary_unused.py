'''
    def _consume_scope_declaration(self, idx : int, tokens) -> bool:
        params, state = '', 1
        while idx < len(tokens) and state > 0:
            next_state = -1

            if state == 1:
                if StructuresConsumer.try_var_declaration(idx, tokens):
                    res = StructuresConsumer.get_consume_res()
                    params += f'{res[0]} {res[1]}'
                    idx, next_state = res[-1], 2

            elif state == 2:
                if tokens[idx].value == ',':
                    params += ', '
                    next_state = 1

                elif tokens[idx].value == ')':
                    next_state = 0

                else:
                    next_state = 2

                idx  += 1

            state = next_state

        if state == 0:
            print('Params:', params)
            self.idx = idx - 1
            return True

        return False

    @classmethod
    def try_complex_method_var_declaration(cls, idx, tokens, check_first = True):
        cls.consume_res = None
        if check_first and not isinstance(tokens[idx], java_lexer.Identifier):
            return False

        start, end = idx, None
        cls.idx = idx + 1

        if tokens[cls.idx].value == '<':
            if cls.try_template(cls.idx, tokens, False):
                cls.idx = cls.consume_res[-1]

        if (cls.idx + 1 < len(tokens)
                and tokens[cls.idx].value == '['
                    and tokens[cls.idx+1].value == ']'):
            cls.idx += 2

        if cls.idx < len(tokens) and isinstance(tokens[cls.idx], java_lexer.Identifier):
            end = cls.idx + 1
            cls.consume_res = (tokens[start].value, tokens[end-1].value, end)

        if end < len(tokens) and tokens[end].value == '(':
            cls.consume_res = (tokens[start].value, tokens[end-1].value, '(', end + 1)

        if not end: return False
        return True

    @classmethod
    def try_method_declaration(cls, idx, tokens):
        cls.consume_res = None

        if isinstance(tokens[idx], java_lexer.SimpleType):
            return cls.try_simple_method_declaration(idx, tokens, False)

        elif tokens[idx].value == 'void':
            return cls.try_void_method_declaration(idx, tokens, False)

        elif isinstance(tokens[idx], java_lexer.Identifier):
            if cls.try_var_declaration(idx, tokens, False):
                pass


    def remove_local_resolver(self, uuid):
        unit = self._resolvers.get(uuid, None)
        if not unit: return True
        if unit.is_pending():
            raise NamesResolverError(
                'Unable to remove unit({}): {} pending names found'.format(
                    uuid, unit.pending_count()))
        del self._resolvers[uuid]
        return True
'''