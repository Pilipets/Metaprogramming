import os
from copy import deepcopy
from logging import DEBUG as logging_DEBUG

from ...utils.utils import out_logger, setup_logger, tricky_reformat, unwind_tokens
from ...convention.convention_naming import NameType, ConventionNaming
from ...tokenizer.java_tokens import Identifier

from .global_resolver import AbstractResolver
from .scope_resolver import ScopeNamesResolver
from .doc_resolver import ScopeDocResolver

logger = setup_logger(__name__, logging_DEBUG)

class FileResolver(AbstractResolver):
    def _reset(self):
        self._p_resolver = None
        self._g_resolver = None

        self._scope_resolver = None
        self._doc_resolver = None

        self._path = None
        self._tokens = []
        self._changed_tokens = []
        self._produce_file = False
        self._touch_docs = False

    def __init__(self, p_resolver, g_resolver,
                 path, tokens,
                 produce_file, touch_docs):

        logger.debug('Opening file resolver for "{}"'.format(path))

        self._p_resolver = p_resolver
        self._g_resolver = g_resolver

        changed_tokens = deepcopy(tokens)
        changed_named_tokens = [(idx, x) for idx, x in enumerate(changed_tokens) if isinstance(x, Identifier)]

        self._scope_resolver = ScopeNamesResolver(g_resolver, changed_named_tokens)
        self._doc_resolver = ScopeDocResolver(changed_tokens)

        self._path = path
        self._tokens = tokens
        self._changed_tokens = changed_tokens
        self._produce_file = produce_file
        self._touch_docs = touch_docs

    # ----------------------PRIVATE----------------------------

    def _add_var_declaration(self, is_global, type, vars):
        if is_global: return

        logger.debug("Adding local vars declaration: %s", vars)
        resolver = self._scope_resolver
        if type == NameType.VARIABLE:
            renamer = ConventionNaming.get_variable_name
        elif type == NameType.CONST_VARIABLE:
            renamer = ConventionNaming.get_constant_name

        for x in vars._names:
            resolver[x] = renamer(x)

    def _add_class_declaration(self, is_global, type, cls):
        if is_global: return

        logger.debug("Adding local class declaration: %s", cls)
        resolver = self._scope_resolver
        resolver[cls._name] = ConventionNaming.get_class_name(cls._name)

        if not cls._templ: return
        for x in cls._templ._names:
            resolver[x] = ConventionNaming.get_class_name(x)

    def _add_annotation_declaration(self, is_global, type, ann):
        if is_global: return

        logger.debug("Adding local annotation declaration: %s", ann)
        resolver = self._scope_resolver
        resolver[ann._name] = ConventionNaming.get_annotation_name(ann._name)

    def _add_method_declaration(self, is_global, type, method):
        if is_global: return

        logger.debug("Adding local method declaration: %s", method)
        resolver = self._scope_resolver
        if not method._type:
            resolver[method._name] = ConventionNaming.get_class_name(method._name)
        else:
            resolver[method._name] = ConventionNaming.get_method_name(method._name)

        for x in method._params:
            x = x._names[0]
            resolver[x] = ConventionNaming.get_variable_name(x)

        if not method._templ: return
        for x in method._templ._names:
            resolver[x] = ConventionNaming.get_class_name(x)

    def _get_cmp_renamed_file_path(self, path):
        head, tail = os.path.split(path)
        name, format = os.path.splitext(tail)
        new_name = ConventionNaming.get_class_name(name)
        res = os.path.join(head, f'modified_{new_name}{format}')
        if name != new_name:
            return (name, new_name), res
        return None, res

    # ---------------------INTERFACE-----------------------

    def get_file_path(self):
        return self._path

    def add_doc_declaration(self, pos, type, modifiers, stack):
        if not (self._touch_docs and self._is_global_scope(modifiers, stack)):
            return

        if type == NameType.CLASS or type == NameType.METHOD:
            self._doc_resolver.add_pending(pos, type)

    def close(self):
        logger.debug('Closing file resolver for "{}"'.format(self._path))
        out_logger.info('Renaming for file "{}"'.format(self._path).center(80, '-'))

        if self._produce_file:
            renamed, out_path = self._get_cmp_renamed_file_path(self._path)
            if renamed: out_logger.info('Renaming file: {} -> {}'.format(renamed[0], renamed[1]))
            out_logger.info('Output path: {}'.format(out_path))

        n_idx = self._scope_resolver.close()
        d_idx = self._doc_resolver.close()

        out_logger.info(''.center(80, '-'))
        if not self._produce_file:
            self._reset()
            return

        # Make tokens and changed_tokens equal length
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
        with open(out_path, "w") as f:
            f.write(output_str)

        self._reset()
    # ------------------------------------------------------