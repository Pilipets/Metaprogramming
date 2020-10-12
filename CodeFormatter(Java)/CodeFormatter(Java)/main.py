from src.FormatterUI import *
import sys

if __name__ == '__main__':
    if len(sys.argv) > 1: FormatterUI.handle_parameters()
    else:
        with open("input/code3.txt", "r") as f: javacode = f.read()
   
        tokens = jl.tokenizer.tokenize(javacode, ignore_errors= True)
        formatter = CodeFormatter()
        output = formatter.format(tokens)
        print(output)