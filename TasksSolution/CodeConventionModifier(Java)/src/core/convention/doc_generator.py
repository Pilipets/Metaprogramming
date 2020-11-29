from ..analyzer.consumers import MethodStruct

# https://www.oracle.com/technical-resources/articles/java/javadoc-tool.html

def finalize_doc(lines, shift):
    indent = shift*' '
    res = f'\n{indent}* '.join(lines)
    return res + f'\n{indent}*/'

param_sym, param_text = '@param', 'Here goes param description.'
return_sym, return_text =  '@return', 'Here goes return description.'
def generate_method_doc(method, col_indent):
    def format_print(width, padding, *args):
        res = []
        for x, y, z in zip(width, padding, args):
            res.append(z.ljust(x + y))
        return ''.join(res)

    lines = ['/**',
             'This is default method javadoc,',
             'please specify method description here.',
             '']

    cols = [[''] for _ in range(3)]

    has_params = False
    if method._params:
        cols[0].append(param_sym)
        cols[1].extend((x._names[0] for x in method._params))
        cols[2].append(param_text)
        has_params = True

    has_return = False
    if method._type and method._type._name != 'void':
        cols[0].append(return_sym)
        cols[2].append(return_text)
        has_return = True
      
    widths = [max(map(len, col)) for col in cols]
    padding = [1, 2, 0]

    for x in method._params:
        name = x._names[0]
        lines.append(format_print(widths, padding, param_sym, name, param_text))

    if has_return:
        lines.append(format_print(widths, padding, return_sym, '', return_text))

    return finalize_doc(lines, col_indent)

def generate_class_doc(cls, col_indent):
    lines = ['/**',
             'This is default class javadoc,',
             'please specify class description here.']
    
    return finalize_doc(lines, col_indent)