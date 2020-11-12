import re

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