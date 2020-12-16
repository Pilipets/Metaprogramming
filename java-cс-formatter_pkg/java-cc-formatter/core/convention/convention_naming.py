from enum import Enum

class NameType(Enum):
    CLASS = 0
    ANNOTATION = 1
    METHOD = 2
    VARIABLE = 3
    CONST_VARIABLE = 4
    NAME = 5
 
class ConventionNaming:
    @staticmethod
    def _strip_invalid_prefix(name : str):
        idx = 0
        while idx < len(name) and (name[idx] in '_$' or name[idx].isdigit()): idx += 1
        return name[idx:len(name)]

    @staticmethod
    def _get_name_partitions(name : str, append_upper = False):
        x = ConventionNaming._strip_invalid_prefix(name)

        res = []
        idx = 0
        while idx < len(x):
            ch, start = x[idx], idx
            if ch in '_$':
                while idx < len(x) and x[idx] in '_$': idx += 1
                start = idx
                continue

            if ch.isupper():
                if append_upper:
                    while idx < len(x) and x[idx].isupper():
                        idx += 1
                else:
                    idx += 1
                while idx < len(x) and x[idx].islower(): idx += 1
                while idx < len(x) and x[idx].isdigit(): idx += 1

            elif ch.islower() or ch.isdigit():
                while idx < len(x) and x[idx].isdigit(): idx += 1
                while idx < len(x) and x[idx].islower(): idx += 1
                while idx < len(x) and x[idx].isdigit(): idx += 1

            else:
                # Something wrong is passed here
                idx += 1

            if start != idx: res.append(x[start:idx])

        return res

    @staticmethod
    def get_constant_name(name : str):
        res = ConventionNaming._get_name_partitions(name, True)
        return '_'.join(x.upper() for x in res)

    @staticmethod
    def get_class_name(name : str):
        res = ConventionNaming._get_name_partitions(name, False)
        return ''.join(x.capitalize() for x in res)

    @staticmethod
    def get_annotation_name(name : str):
        res = ConventionNaming._get_name_partitions(name, False)
        return ''.join(x.capitalize() for x in res)

    @staticmethod
    def get_method_name(name : str):
        res = ConventionNaming._get_name_partitions(name, '_' in name)
        if not res: return ''
        return res[0].lower() + ''.join(x.capitalize() for x in res[1:])

    @staticmethod
    def get_variable_name(name : str):
        res = ConventionNaming._get_name_partitions(name, '_' in name or name.isupper())
        if not res: return ''
        return res[0].lower() + ''.join(x.capitalize() for x in res[1:])

def get_convention_rename(type : NameType, name : str):
    if type == NameType.CLASS or type == NameType.ANNOTATION:
        return ConventionNaming.get_class_name(name)

    elif type == NameType.METHOD:
        return ConventionNaming.get_method_name(name)

    elif type == NameType.VARIABLE:
        return ConventionNaming.get_variable_name(name)

    elif type == NameType.CONST_VARIABLE:
        return ConventionNaming.get_constant_name(name)

    else:
        return name