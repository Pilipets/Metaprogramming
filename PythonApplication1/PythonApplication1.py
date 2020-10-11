from CodeFormatter import *

def my_method():
    with open("code.txt","r") as f: javacode = f.read()
    
    tokens = jl.tokenizer.tokenize(javacode, ignore_errors= True)
    formatter = CodeFormatter()
    output = formatter.format(tokens)
    print(output)


if __name__ == '__main__':
    my_method()