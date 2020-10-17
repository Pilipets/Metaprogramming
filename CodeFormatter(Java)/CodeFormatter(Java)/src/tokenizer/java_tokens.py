from collections import namedtuple

Position = namedtuple('Position', ['line', 'column'])
class JavaToken(object):
    def __init__(self, value, position=None):
        self.value, self.position = value, position

    def __repr__(self):
        if self.position:
            return '%s "%s" line %d, position %d' % (
                self.__class__.__name__, self.value, self.position[0], self.position[1]
                )
        else:
            return '%s "%s"' % (self.__class__.__name__, self.value)

    def __str__(self):
        return repr(self)

    def __eq__(self, other):
        raise Exception("Direct comparison not allowed")

class EndOfInput(JavaToken):
    pass

class Keyword(JavaToken):
    VALUES = set(['abstract', 'assert', 'boolean', 'break', 'byte', 'case',
                  'catch', 'char', 'class', 'const', 'continue', 'default',
                  'do', 'double', 'else', 'enum', 'extends', 'final',
                  'finally', 'float', 'for', 'goto', 'if', 'implements',
                  'import', 'instanceof', 'int', 'interface', 'long', 'native',
                  'new', 'package', 'private', 'protected', 'public', 'return',
                  'short', 'static', 'strictfp', 'super', 'switch',
                  'synchronized', 'this', 'throw', 'throws', 'transient', 'try',
                  'void', 'volatile', 'while'])


class Modifier(Keyword):
    VALUES = set(['abstract', 'default', 'final', 'native', 'private',
                  'protected', 'public', 'static', 'strictfp', 'synchronized',
                  'transient', 'volatile'])

class BasicType(Keyword):
    VALUES = set(['boolean', 'byte', 'char', 'double',
                  'float', 'int', 'long', 'short'])

class Literal(JavaToken):
    pass

class Integer(Literal):
    pass

class DecimalInteger(Literal):
    pass

class OctalInteger(Integer):
    pass

class BinaryInteger(Integer):
    pass

class HexInteger(Integer):
    pass

class FloatingPoint(Literal):
    pass

class DecimalFloatingPoint(FloatingPoint):
    pass

class HexFloatingPoint(FloatingPoint):
    pass

class Boolean(Literal):
    VALUES = set(["true", "false"])

class Character(Literal):
    pass

class String(Literal):
    pass

class Null(Literal):
    pass

class Separator(JavaToken):
    VALUES = set(['(', ')', '{', '}', '[', ']', ';', ',', '.'])

class Operator(JavaToken):
    MAX_LEN = 4
    VALUES = set(['>>>=', '>>=', '<<=',  '%=', '^=', '|=', '&=', '/=',
                  '*=', '-=', '+=', '<<', '--', '++', '||', '&&', '!=',
                  '>=', '<=', '==', '%', '^', '|', '&', '/', '*', '-',
                  '+', ':', '?', '~', '!', '<', '>', '=', '...', '->', '::'])

    INFIX = set(['||', '&&', '|', '^', '&', '==', '!=', '<', '>', '<=', '>=',
                 '<<', '>>', '>>>', '+', '-', '*', '/', '%'])

    PREFIX = set(['++', '--', '!', '~', '+', '-'])

    POSTFIX = set(['++', '--'])

    ASSIGNMENT = set(['=', '+=', '-=', '*=', '/=', '&=', '|=', '^=', '%=',
                      '<<=', '>>=', '>>>='])

    def is_infix(self):
        return self.value in self.INFIX

    def is_prefix(self):
        return self.value in self.PREFIX

    def is_postfix(self):
        return self.value in self.POSTFIX

    def is_assignment(self):
        return self.value in self.ASSIGNMENT


class Annotation(JavaToken):
    pass

class Identifier(JavaToken):
    pass