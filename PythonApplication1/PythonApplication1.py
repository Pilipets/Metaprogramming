import javalang as jl
import enum
import logging
from config import *

logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')

class BlockType(enum.Enum):
    OpenBrace = 0

def my_method():
    with open("code2.txt","r") as f: javacode = f.read()
    
    tokens = jl.tokenizer.tokenize(javacode, ignore_errors= True)
    output = ''
    stack = [jl.tokenizer.JavaToken('')]
    indent_level = 0
    idx = 0
    tokens = list(tokens)
    pre = None

    for idx in range(len(tokens)):
        print(tokens[idx])
        cur = tokens[idx]
        add_output = cur.value

        if cur.value == '(':
            if isinstance(pre, jl.tokenizer.Identifier):
                stack.append(pre)
                add_output = (' ' if space_before_method else '') + add_output
            elif isinstance(pre, jl.tokenizer.Keyword):
                if pre.value in ('for', 'while', 'if', 'catch', 'try', 'synchronized'):
                    stack.append(pre)
                    add_output = (' ' if space_before_keyword else '') + add_output
                else:
                    logging.warning('Incorrect position of the \'(\', {}', cur)
            else: # expression parentheses
                stack.append(BlockType.OpenBrace)
                pass
        elif cur.value == ')':
            if not pre: logging.warning('Incorrect position of the \')\', {}', cur)
            pre = tokens[idx-1]
            if isinstance(stack[-1], (jl.tokenizer.Identifier, jl.tokenizer.Keyword)) or stack[-1] in (BlockType.OpenBrace,):
                stack.pop()
            else:
                logging.warning('Incorrect position of the \')\', {}', cur)
        elif cur.value == ';':
            if isinstance(stack[-1], jl.tokenizer.Keyword) and stack[-1].value in ('for', 'try'):
                pass
            else:
                add_output += '\n';
        elif cur.value == '{':
            pass
        elif cur.value == '}':
            pass
        elif isinstance(cur, jl.tokenizer.Separator) or isinstance(pre, jl.tokenizer.Separator) or not pre:
            pass
        elif (space_within_operator and (isinstance(cur, jl.tokenizer.Operator)
                                         or isinstance(pre, jl.tokenizer.Operator))):
            add_output = ' ' + add_output
        else:
            add_output = ' ' + add_output
        output += add_output
        pre = cur

    print(output)
if __name__ == '__main__':
    my_method()