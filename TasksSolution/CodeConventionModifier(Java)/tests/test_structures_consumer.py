from src.core.analyzer import StructuresConsumer as Consumer
from src.core.tokenizer.java_lexer import tokenize

consumer = Consumer.get_consumer()

templates_invocation_data = [
    ('<SingleSource<? extends T>, What.Publisher<? extends Heh.T>>', (True, ['SingleSource', 'Publisher'])),
    ('<@NonNull T>', (True, ['T'])),
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

# TODO: add tests for annotation declaration, invocations