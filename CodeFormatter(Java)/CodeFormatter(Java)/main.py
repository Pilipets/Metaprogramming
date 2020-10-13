import sys

from src.FormatterUI import FormatterUI, CodeFormatter, jl

def debug():
    with open("input/code.java", "r") as fin:
        javacode = fin.read()

    tokens = list(jl.tokenizer.tokenize(javacode, ignore_errors=True))
    formatter = CodeFormatter()
    output = formatter.format(tokens)
    print(output)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        FormatterUI.handle_parameters()
    else:
        debug()
