import os

from .scope_resolver import ScopeNamesResolver
from .doc_resolver import ScopeDocResolver
from ...utils.utils import out_logger, tricky_reformat, unwind_tokens
from ...convention.convention_naming import NameType, ConventionNaming
from ...tokenizer.java_lexer import Identifier

class TokenChange:
    def __init__(self):
        self.name = False
        self.javadoc = False

class FileResolver:
    def _reset(self):
        self._p_resolver = None
        self._g_resolver = None

        self._names_resolver = None
        self._doc_resolver = None

        self._path = None
        self._tokens = []
        self._changed_tokens = []
        self._produce_file = False
        self._touch_docs = False

    def __init__(self, p_resolver, g_resolver,
                 path, tokens, changed_tokens,
                 produce_file, touch_docs):
        self._p_resolver = p_resolver
        self._g_resolver = g_resolver

        changed_named_tokens = [(idx, x) for idx, x in enumerate(changed_tokens)
                                if isinstance(x, Identifier)]

        self._names_resolver = ScopeNamesResolver(self, g_resolver, tokens, changed_named_tokens)
        self._doc_resolver = ScopeDocResolver(self, changed_tokens)

        self._path = path
        self._tokens = tokens
        self._changed_tokens = changed_tokens
        self._produce_file = produce_file
        self._touch_docs = touch_docs

    # ----------------------PRIVATE----------------------------
    def _is_global_scope(self, stack):
        if (len(stack) == 1 or
                (len(stack) == 3 and stack[-1].value == '{'
                    and stack[-2].value in ('class', 'interface'))):
            return True
        return False

    def _add_var_declaration(self, is_global, type, method):
        resolver = self._g_resolver if is_global else self._names_resolver
        if type == NameType.VARIABLE:
            renamer = ConventionNaming.get_variable_name
        elif type == NameType.CONST_VARIABLE:
            renamer = ConventionNaming.get_constant_name

        for x in method._names:
            resolver[x] = renamer(x)

    def _add_class_declaration(self, is_global, type, cls):
        resolver = self._g_resolver if is_global else self._names_resolver
        resolver[cls._name] = ConventionNaming.get_class_name(cls._name)

        if not cls._templ: return
        for x in cls._templ._names:
            self._names_resolver[x] = ConventionNaming.get_class_name(x)

    def _add_method_declaration(self, is_global, type, method):
        resolver = self._g_resolver if is_global else self._names_resolver

        if not method._type:
            resolver[method._name] = ConventionNaming.get_class_name(method._name)
        else:
            resolver[method._name] = ConventionNaming.get_method_name(method._name)

        for x in method._params:
            x = x._names[0]
            self._names_resolver[x] = ConventionNaming.get_variable_name(x)

        if not method._templ: return
        for x in method._templ._names:
            self._names_resolver[x] = ConventionNaming.get_class_name(x)

    def _get_cmp_renamed_file_path(self, path):
        head, tail = os.path.split(path)
        name, format = os.path.splitext(tail)
        new_name = ConventionNaming.get_class_name(name)
        res = os.path.join(head, f'modified_{name}{format}')
        if name != new_name:
            return (name, new_name), res
        return None, res

    # --------------------------SLOTS--------------------------
    def slot_global_name_added(self, name, new_name):
        is_empty = self._names_resolver.slot_global_name_added(name, new_name)
        if not is_empty: return

        self.close()

    def slot_child_pending_on(self, name, ins):
        self._p_resolver.slot_child_pending_on(name, self)

    # ---------------------INTERFACE-----------------------

    def get_file_path(self):
        return self._path

    def add_name_declaration(self, type, ins, stack):
        is_global = self._is_global_scope(stack)

        if type == NameType.VARIABLE or type == NameType.CONST_VARIABLE:
            self._add_var_declaration(is_global, type, ins)

        elif type == NameType.CLASS or type == NameType.ANNOTATION:
            self._add_class_declaration(is_global, type, ins)

        elif type == NameType.METHOD:
            self._add_method_declaration(is_global, type, ins)

        else:
            return False

    def add_doc_declaration(self, pos, type, stack):
        is_global = self._is_global_scope(stack)
        if not (is_global and self._touch_docs): return

        if type == NameType.CLASS or type == NameType.METHOD:
            self._doc_resolver.add_pending(pos, type)

    def process_declarations(self):
        is_empty = self._names_resolver.process_postpone_renamings()
        if not is_empty: return False

        self.close()

    def close(self):
        out_logger.info('Renaming for file "{}"'.format(self._path).center(80, '-'))

        renamed, out_path = self._get_cmp_renamed_file_path(self._path)
        if renamed: out_logger.info('Renaming file: {} -> {}'.format(renamed[0], renamed[1]))
        out_logger.info('Output path: {}'.format(out_path))

        n_idx = self._names_resolver.close()
        d_idx = self._doc_resolver.close()

        out_logger.info(''.center(80, '-'))
        if not self._produce_file:
            self._p_resolver.slot_child_closed(self)
            self._reset()
            return

        # Add tokens equal cnt
        for idx, x in enumerate(self._changed_tokens):
            if x.javadoc and not self._tokens[idx].javadoc:
                self._tokens[idx].javadoc = x.javadoc

        # Unwind javadoc for restoring the input text
        modified_tokens = unwind_tokens(self._changed_tokens)
        original_tokens = unwind_tokens(self._tokens)

        # Mark modified tokens with name or javadoc
        modified_indices = [False for _ in range(len(modified_tokens))]

        idx1, idx2 = 0, 0
        doc_cnt = 0
        for idx, x in enumerate(self._changed_tokens):
            if x.javadoc: doc_cnt += 1

            if idx1 == len(n_idx) and idx2 == len(d_idx):
                break

            if idx1 < len(n_idx) and idx == n_idx[idx1]:
                modified_indices[idx+doc_cnt] = True
                idx1 += 1

            if idx2 < len(d_idx) and idx == d_idx[idx2]:
                modified_indices[idx+doc_cnt-1] = True
                idx2 += 1

        output_str = tricky_reformat(original_tokens, modified_indices, modified_tokens)
        with open(out_path, "w") as f: f.write(output_str)

        self._p_resolver.slot_child_closed(self)
        self._reset()
    # ------------------------------------------------------