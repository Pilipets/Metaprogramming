from collections import namedtuple

Position = namedtuple('Position', ['line', 'column'])

class JavaToken():
    def __init__(self, value, position=None, javadoc=None):
        self.value, self.position = value, position

        self.javadoc = javadoc

    def __str__(self):
        if not self.position:
            return '%s "%s"' % (self.__class__.__name__, self.value)

        return '%s "%s" line %d, column %d' % (
            self.__class__.__name__, self.value, self.position[0], self.position[1])

    def __eq__(self, other):
        raise NotImplementedError

class Keyword(JavaToken):
    VALUES_SET = {'abstract', 'assert', 'boolean', 'break', 'byte', 'case',
                  'catch', 'char', 'class', 'const', 'continue', 'default',
                  'do', 'double', 'else', 'enum', 'extends', 'final',
                  'finally', 'float', 'for', 'goto', 'if', 'implements',
                  'import', 'instanceof', 'int', 'interface', 'long', 'native',
                  'new', 'package', 'private', 'protected', 'public', 'return',
                  'short', 'static', 'strictfp', 'super', 'switch',
                  'synchronized', 'this', 'throw', 'throws', 'transient', 'try',
                  'void', 'volatile', 'while'}

class Modifier(Keyword):
    VALUES_SET = {'abstract', 'default', 'final', 'native', 'private',
                  'protected', 'public', 'static', 'strictfp', 'synchronized',
                  'transient', 'volatile'}

class BasicType(Keyword):
    VALUES_SET = {'boolean', 'byte', 'char', 'double', 'float', 'int', 'long', 'short'}

class Literal(JavaToken):
    pass

# Literal includes integers, strings, bool, and so on
# For the moment it doesn't matter

class Comment(JavaToken):
    pass

class SingleLineComment(Comment):
    pass

class MultiLineComment(Comment):
    pass

class Separator(JavaToken):
    VALUES_SET = {'(', ')', '{', '}', '[', ']', ';', ',', '.'}

class Operator(JavaToken):
    MAX_LEN = 4
    VALUES_SET = {'>>>=', '>>=', '<<=', '%=', '^=', '|=', '&=', '/=',
                  '*=', '-=', '+=', '<<', '--', '++', '||', '&&', '!=',
                  '>=', '<=', '==', '%', '^', '|', '&', '/', '*', '-',
                  '+', ':', '?', '~', '!', '<', '>', '=', '...', '->', '::'}

    PREFIX_SET = {'++', '--', '!', '~', '+', '-'}
    ASSIGNMENT_SET = {'=', '+=', '-=', '*=', '/=', '&=', '|=', '^=', '%=', '<<=', '>>=', '>>>='}

    def is_prefix(self):
        return self.value in self.PREFIX_SET

    def is_assignment(self):
        return self.value in self.ASSIGNMENT_SET


class Annotation(JavaToken):
    pass

class Identifier(JavaToken):
    pass
