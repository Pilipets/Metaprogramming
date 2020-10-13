from src.FormatterUI import *
import sys

if __name__ == '__main__':
    if len(sys.argv) > 1: FormatterUI.handle_parameters()
    else:
        with open("input/code.txt", "r") as f: javacode = f.read()
   
        tokens = list(jl.tokenizer.tokenize(javacode, ignore_errors= True))
        print(val)
        #formatter = CodeFormatter()
        #output = formatter.format(tokens)
        #print(output)