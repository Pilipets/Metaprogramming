from abc import ABC
from logging import DEBUG as logging_DEBUG

from ...convention.convention_naming import NameType, ConventionNaming
from ...utils.utils import setup_logger

logger = setup_logger(__name__, logging_DEBUG)

class AbstractResolver(ABC):
    def __init__(self):
        raise NotImplementedError("Not expected to be instantiated")

    # ------------------------------PUBLIC---------------------------------
    def add_doc_declaration(self, pos, type, modifiers, stack):
        pass

    def add_name_declaration(self, type, ins, modifiers, stack):
        is_global = self._is_global_scope(modifiers, stack)

        if type == NameType.VARIABLE or type == NameType.CONST_VARIABLE:
            self._add_var_declaration(is_global, type, ins)

        elif type == NameType.CLASS:
            self._add_class_declaration(is_global, type, ins)

        elif type == NameType.ANNOTATION:
            self._add_annotation_declaration(is_global, type, ins)

        elif type == NameType.METHOD:
            self._add_method_declaration(is_global, type, ins)

    # ----------------------PRIVATE----------------------------
    def _is_global_scope(self, modifiers, stack):
        if 'private' in modifiers: return False
        if (len(stack) == 1 or
                (len(stack) == 3 and stack[-1].value == '{'
                    and stack[-2].value in ('class', 'interface'))):
            return True
        return False



class GlobalNamesResolver(dict, AbstractResolver):
    def _reset(self):
        self._root = None
        super().clear()

    def __init__(self, root):
        self._root = root

    def close(self):
        self._reset()

    # ----------------------PRIVATE----------------------------

    def _add_var_declaration(self, is_global, type, vars):
        if not is_global: return

        logger.debug("Adding global vars declaration: %s", vars)
        if type == NameType.VARIABLE:
            renamer = ConventionNaming.get_variable_name
        elif type == NameType.CONST_VARIABLE:
            renamer = ConventionNaming.get_constant_name

        for x in vars._names:
            self[x] = renamer(x)

    def _add_class_declaration(self, is_global, type, cls):
        if not is_global: return

        logger.debug("Adding global class declaration: %s", cls)
        self[cls._name] = ConventionNaming.get_class_name(cls._name)

    def _add_annotation_declaration(self, is_global, type, ann):
        if is_global: return

        logger.debug("Adding global annotation declaration: %s", ann)
        resolver = self._scope_resolver
        resolver[ann._name] = ConventionNaming.get_annotation_name(ann._name)

    def _add_method_declaration(self, is_global, type, method):
        if not is_global: return

        logger.debug("Adding global method declaration: %s", method)
        if not method._type:
            rename = ConventionNaming.get_class_name(method._name)
        else:
            rename = ConventionNaming.get_method_name(method._name)

        self[method._name] = rename