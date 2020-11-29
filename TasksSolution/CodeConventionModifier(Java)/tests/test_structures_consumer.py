from src.core.analyzer import StructuresConsumer as Consumer
from src.core.tokenizer.java_lexer import tokenize

consumer = Consumer.get_consumer()

templates_invocation_data = [
    ('<String, byte[]>', (True, ['String', 'byte'])),
    ('<Try, ?, Object[]>', (True, ['Try', 'Object'])),
    ('<Object<Yet.Simple.Temp<Another>, v[]>>', (True, ['Object', 'Temp', 'Another', 'v'])),
    ('<T, Y, Z>', (True, ['T', 'Y', 'Z'])),
    ('<Dummy, asas[], Object<W, C, R>>', (True, ['Dummy', 'asas', 'Object', 'W', 'C', 'R'])),

    ('<T extends Bar & Y.Abba, U>', (False, )),
    ('<temp super Object<Txt, wew>>', (False, )),
    ('<Object extends Other>', (False, )),
    ('<T super Bar & yh.Abba, U, Z>', (False, )),
    ('<T, Y extends Other, Z>', (False, )),
]
def test_try_template_invocation():
    for in_txt, out in templates_invocation_data:
        tokens = list(tokenize(in_txt))
        
        assert consumer.try_template_invocation(0, tokens) == out[0]
        if not out[0]: continue
        tmpl, end = consumer.get_consume_res()

        assert end == len(tokens)
        assert tmpl._names == out[1]

templates_declaration_data = [
    ('<T super Bar & yh.Abba, U, Z>', (True, ['T', 'U', 'Z'])),
    ('<temp super Object<Txt, wew[]>>', (True, ['temp'])),
    ('<T, Y extends Other, Z>', (True, ['T', 'Y', 'Z'])),
    ('<Object, Other>', (True, ['Object', 'Other'])),
    ('<D extends Other<A, B<C,E>> & This, Ok>', (True, ['D', 'Ok'])),

    ('<Bar.T>', (False, )),
    ('<Try, ?, Object[]>', (False, )),
    ('<Object<Temp<Another>>>', (False, )),
    ('<temp super Object<Txt, wew>[]>', (False,)),
    ('<Dummy, asas[], Object<W, C, R>>', (False,)),
]
def test_try_template_declaration():
    for in_txt, out in templates_declaration_data:
        tokens = list(tokenize(in_txt))
        
        assert consumer.try_template_declaration(0, tokens) == out[0]
        if not out[0]: continue

        tmpl, end = consumer.get_consume_res()
        assert end == len(tokens)
        assert tmpl._names == out[1]


class_data = [
    ('class Foo<T extends Bar & Abba, U>', ('Foo', True, 11)),
    ('class Simple extends Whatever implements Damn<T, Y>', ('Simple', False, 2)),
    ('class Another  {', ('Another', False, 2))
]
def test_try_class_declaration():
    for in_txt, out in class_data:
        tokens = list(tokenize(in_txt))
        
        assert consumer.try_class_declaration(0, tokens)
        cls, end = consumer.get_consume_res()

        assert cls._name == out[0]
        assert bool(cls._templ) == out[1]
        assert end == out[2]


var_type_data = [
    ('E<>', ('E', True, False)),
    ('E<?>', ('E', True, False)),
    ('Foo<T[], U<Te, SDsd>>[]', ('Foo', True, True)),
    ('int[]', ('int', False, True)),
    ('Wyg', ('Wyg', False, False)),
    ('AR<A<B<C<?>, E[][]>, Z<INT>[]>, Another>', ('AR', True, False)),
    ('Why.Am.E[]', ('E', False, True)),
    ('Simple.E', ('E', False, False))
]
def test_try_var_type():
    for in_txt, out in var_type_data:
        tokens = list(tokenize(in_txt))
        
        assert consumer.try_var_type(0, tokens)
        type, end = consumer.get_consume_res()

        assert end == len(tokens)
        assert type._name == out[0]
        assert bool(type._templ) == out[1]
        assert type._is_array == out[2]

var_single_data = [
    ('Foo<T[], U<Te, SDsd>>[][][] var   ;', ('Foo', 'var')),
    ('Type<?> rs ,', ('Type', 'rs')),
    ('Wyg ass =', ('Wyg', 'ass'))
]
def test_try_var_single_declaration():
    for in_txt, out in var_single_data:
        tokens = list(tokenize(in_txt))
        
        assert consumer.try_var_single_declaration(0, tokens)
        var, end = consumer.get_consume_res()

        assert end == len(tokens) - 1
        assert var._type._name == out[0]
        assert var._names[0] == out[1]

stacked_chars_data = [
    ('{sdsd method(,(e = ;){dd{}dsfd}2323d = ;}', '{}'),
    ('( <other<sdfs>>; {sdsd method(,(e = ;){dd{}dsfd}232)3d = ;} })', '()')
]
def test_try_stacked_chars_data():
    for in_txt, chars in stacked_chars_data:
        tokens = list(tokenize(in_txt))
        
        assert consumer.try_stacked_chars(chars, 0, tokens)
        _, end = consumer.get_consume_res()

        assert end == len(tokens)