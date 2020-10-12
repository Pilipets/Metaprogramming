from src.CodeFormatter import *

if __name__ == '__main__':
    with open("input/code.txt", "r") as f: javacode = f.read()
   
    tokens = jl.tokenizer.tokenize(javacode, ignore_errors= True)
    formatter = CodeFormatter()
    output = formatter.format(tokens)
    print(output)