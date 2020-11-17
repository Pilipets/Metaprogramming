from enum import Enum
import os

class NameType(Enum):
    CLASS = 0
    METHOD = 1
    VARIABLE = 2
    CONST_VARIABLE = 3
    NAME = 4
 
class ConventionNaming:
    @staticmethod
    def _strip_invalid_prefix(name : str):
        idx = 0
        while idx < len(name) and (name[idx] in '_$' or name[idx].isdigit()): idx += 1
        return name[idx:len(name)]

    @staticmethod
    def _get_name_partitions(name : str):
        x = ConventionNaming._strip_invalid_prefix(name)
        res = []
        idx = 0
        while idx < len(x):
            ch, start = x[idx], idx
            if ch in '_$':
                while idx < len(x) and x[idx] in '_$': idx += 1
                start = idx
                continue

            if ch.isupper() or ch.isdigit():
                while idx < len(x) and (x[idx].isupper() or x[idx].isdigit()): idx += 1
                while idx < len(x) and (x[idx].islower() or x[idx].isdigit()): idx += 1

            elif ch.islower() or ch.isdigit():
                while idx < len(x) and (x[idx].islower() or x[idx].isdigit()): idx += 1

            if start != idx: res.append(x[start:idx])

        return res

    @staticmethod
    def get_constant_name(name : str):

        res = ConventionNaming._get_name_partitions(name)
        return '_'.join(x.upper() for x in res)

    @staticmethod
    def get_class_name(name : str):

        res = ConventionNaming._get_name_partitions(name)
        return ''.join(x.capitalize() for x in res)

    @staticmethod
    def get_method_name(name : str):
        return ConventionNaming.get_variable_name(name)

    @staticmethod
    def get_variable_name(name : str):
        res = ConventionNaming._get_name_partitions(name)
        if not res: return ''
        return res[0].lower() + ''.join(x.capitalize() for x in res[1:])

    @staticmethod
    def get_file_name(name):
        return ConventionNaming.get_class_name(name)

def get_convention_rename(type : NameType, name : str):
    if type == NameType.CLASS:
        return ConventionNaming.get_class_name(name)

    elif type == NameType.METHOD:
        return ConventionNaming.get_method_name(name)

    elif type == NameType.VARIABLE:
        return ConventionNaming.get_variable_name(name)

    elif type == NameType.CONST_VARIABLE:
        return ConventionNaming.get_constant_name(name)

    else:
        return name

def get_convention_file_path(path):
    head, tail = os.path.split(path)
    name, format = os.path.splitext(tail)
    name = ConventionNaming.get_file_name(name)
    return os.path.join(head, f'modified_{name}{format}')