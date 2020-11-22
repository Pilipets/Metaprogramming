from collections import namedtuple

from ..consumers import AdvancedConsumer as Consumer
from ...convention import NameType
from ...tokenizer.java_tokens import MultiLineComment
from ...utils.utils import out_logger
from ...convention.doc_generator import generate_method_doc, generate_class_doc

StructPos = namedtuple('StructPos', ['doc', 'start', 'end'])

class ScopeDocResolver:
    def _reset(self):
        self._changed_tokens = list()
        self._pending = list()

    def __init__(self, changed_tokens):
        self._changed_tokens = changed_tokens
        self._pending = list()

    def _format_doc(self, consumer, pos, type, doc_idx):
        doc_token = self._changed_tokens[doc_idx]
        col_indent = doc_token.position.column
        is_new = doc_token.javadoc is None

        if type == NameType.CLASS:
            consumer.try_class_declaration(pos.start, self._changed_tokens)
            cls, _ = consumer.get_consume_res()

            if is_new:
                out_logger.info('Adding class javadoc for {} at Pos({})'.format(
                    cls, self._changed_tokens[pos.start].position))
                doc_token.javadoc = MultiLineComment(generate_class_doc(cls, col_indent))
            else:
                #doc_token.javadoc.value = generate_class_doc(cls, javadoc.position.column)
                pass

        elif type == NameType.METHOD:
            consumer.try_method_declaration(pos.start, self._changed_tokens)
            method, _ = consumer.get_consume_res()

            if is_new:
                out_logger.info('Adding method javadoc for {} at {}'.format(
                    method, self._changed_tokens[pos.start].position))
                doc_token.javadoc = MultiLineComment(generate_method_doc(method, col_indent))
            else:
                # doc_token.javadoc: doc_token.javadoc.value = generate_method_doc(method)
                pass

    def add_pending(self, pos, type):
        self._pending.append((StructPos(*pos), type))

    def close(self):
        consumer = Consumer()
        res = []
        for pos, type in self._pending:
            doc_idx = pos.doc if self._changed_tokens[pos.start].javadoc is None else pos.start
            self._format_doc(consumer, pos, type, doc_idx)
            res.append(doc_idx)

        self._reset()
        return res