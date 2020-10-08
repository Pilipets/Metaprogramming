import javalang as jl
import enum
from config import *


def my_method():
    with open("code2.txt","r") as f: javacode = f.read()
    
    tokens = jl.tokenizer.tokenize(javacode, ignore_errors= True)
    output = ''
    stack = [None]
    indent_level = 0
    idx = 0
    tokens = list(tokens)
    for x in tokens:
        if isinstance(x, jl.tokenizer.EndOfInput):
            print('End of input')
    tokens.append(jl.tokenizer.EndOfInput())

    for idx in range(len(tokens)):
        print(tokens[idx])
        cur = tokens[idx]
        add_output = cur.value
        if cur.value == '(':
            if idx == 0: # report error
                continue
            pre = tokens[idx-1]
            if isinstance(pre, jl.tokenizer.Identifier):
                stack.append(pre)
                add_output = (' ' if space_before_method else '') + add_output
            elif isinstance(pre, jl.tokenizer.Keyword):
                if pre.value in ('for', 'while', 'if', 'catch', 'try', 'synchronized'):
                    stack.append(pre)
                    add_output = (' ' if space_before_keyword else '') + add_output
                else: # report error
                    pass
            else: # expression parentheses
                #stack.append(BlockType.OpenBrace)
                pass
        elif cur.value == ')':
            if idx == 0: # report error
                continue
            pre = tokens[idx-1]
            if isinstance(stack[-1], jl.tokenizer.Identifier) or isinstance(stack[-1], jl.tokenizer.Keyword):
                stack.pop()
            else: # expression parentheses
                pass
        elif cur.value == ';':
            if isinstance(stack[-1], jl.tokenizer.Keyword) and stack[-1].value in ('for', 'try'):
                add_output += ' '
            else:
                add_output += '\n';
        else:
            if idx == 0: continue
            pre = tokens[idx-1]
            if cur.value == '.' or pre.value in ('.', ';', '('): pass
            else: add_output = ' ' + add_output
        output += add_output

    print(output)
if __name__ == '__main__':
    my_method()