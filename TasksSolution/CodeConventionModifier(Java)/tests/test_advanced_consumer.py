from src.core.analyzer import AdvancedConsumer as Consumer
from src.core.tokenizer.java_lexer import tokenize

consumer = Consumer.get_consumer()

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


vars_multi_declaration_data = [
    ('var scope =)', ('var', ('scope',))),
    ('int var)', ('int', ('var',))),
    ('float MyName = <T, P>Class.method(var, this.var);', ('float', ('MyName',))),
    ('Custom[] x, y, z = whatever;', ('Custom', ('x', 'y', 'z'))),
    ('Complex<TryVar[][], ?> x = method(2, 3), y, z = null or (String) temp;', ('Complex', ('x', 'y', 'z'))),
    ('var T1, T2 = Method(new Inst<we, we>(3, 5,6), nuyll, 23), T3 = (Conve);', ('var', ('T1', 'T2', 'T3'))),
    ('yet again = method(23, method2(t, DF.class, method4(...)));', ('yet', ('again',))),
    ('int simple = 34;', ('int', ('simple',))),
    ('Temp<?,?>[] x,y,u;', ('Temp', ('x','y','u')))
]
def test_try_multiple_vars_declaration():
    for in_txt, out in vars_multi_declaration_data:
        tokens = list(tokenize(in_txt))
        
        assert consumer.try_multiple_vars_declaration(0, tokens)
        vars, end = consumer.get_consume_res()

        assert end == len(tokens)-1
        assert vars._type._name == out[0]

        assert len(vars._names) == len(out[1])
        for idx, name in enumerate(vars._names):
            assert name == out[1][idx]

methods_data = [
    (
        '<T> Function<SingleSource<? extends T>, Publisher<? extends T>> toFlowable()',
        ('Function', 'toFlowable')
    ),
    (
        'Map<String, byte[]> getCustomMetadata()',
        ('Map', 'getCustomMetadata')
    ),
    (
        'wtf.TestSimple()',
        None
    ),
    (
        # This is considered as method as we can't distinguish
        # between ctor and method invocation here
        'TestSimple(Dummy.Double<Complex> x)',
        (None, 'TestSimple', ('Double', 'x'))
    ),
    (
        '<T,U> int simple()',
        ('int', 'simple')
    ),
    (
        '<T> S.T.More HowAbout(var x = <wew, Yet, df[]>)',
        ('More', 'HowAbout', ('var', 'x'))
    ),
    (
        'Yet.More[][] HowAbout(var x = another<wew, Simple, df[]>, From.dummy y = z, err x = 4)',
        ('More', 'HowAbout', ('var', 'x'), ('dummy', 'y'), ('err', 'x'))
    ),
    (
        'void Method(int x, double y, WTF z)',
        ('void', 'Method', ('int', 'x'),('double', 'y'), ('WTF', 'z'))
    ),
    (
        'Try<Cmp, S[]>[] Another(Wen.Then<ere, sds> x, ret y = method(23, MyArr[323]))',
        ('Try', 'Another', ('Then', 'x'), ('ret', 'y'))
    ),
    (
        '<Cmp, S extends K> Method(Where.Is.This.Double x, Simple y)',
        (None, 'Method', ('Double', 'x'), ('Simple', 'y'))
    ),
    (
        '<Cmp, S extends K> Method(Where.Is.This.Double x, Simple y)',
        (None, 'Method', ('Double', 'x'), ('Simple', 'y'))
    ),
    (
        '''<T, U extends T> ResponseEntity<Object> tripCancelled(
                @RequestParam(value = "forward")String forward,
                @RequestParam(value = "id") UUID id,
                final @RequestParam(value = "trip_id") @Nullable UUID tripId)''',
        ('ResponseEntity', 'tripCancelled', ('String', 'forward'), ('UUID', 'id'), ('UUID', 'tripId'))
    )
]
def test_try_method_declaration():
    for in_txt, out in methods_data:
        tokens = list(tokenize(in_txt))
        
        assert_res = out is not None
        assert consumer.try_method_declaration(0, tokens) == assert_res
        if not assert_res: continue

        method, end = consumer.get_consume_res()

        assert end == len(tokens)

        if method._type: assert method._type._name == out[0]
        else: assert method._type is None

        assert method._name == out[1]
        for x, y in zip(method._params, out[2:]):
            assert x._type._name == y[0]
            assert x._names[0] == y[1]

# TODO: add tests for anonymous classes