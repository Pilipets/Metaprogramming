import sys

from src.formatter_ui import FormatterUI, FormatterCore, jl

def debug():
    with open("input/code.java", "r") as fin:
        javacode = fin.read()

    tokens = list(jl.tokenizer.tokenize(javacode, ignore_errors=True))
    formatter = FormatterCore()
    output = formatter.format(tokens)
    print(output)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        FormatterUI.handle_parameters()
    else:
        debug()
