from src.CodeFormatter import *
import sys
import os

class FormatterUI:
    @staticmethod
    def report_error(x):
        print("Error: {}, use --help for more details!".format(x))
        sys.exit()

    @staticmethod
    def prepare_formatting_files(option, path):
        option = sys.argv[3]
        res = []
        if option == '-p':
            if not os.path.isdir(path):
                report_error("given path=%s isn't a directory" % path)
            else:
                for root, dirs, files in os.walk(path):
                    for file in files:
                        if file.endswith('.java'):
                             res.append(os.path.join(root, file))
                return res

        elif option == '-d':
            if not os.path.isdir(path):
                report_error("given path=%s isn't a directory" % path)
            else:
                for file in os.listdir(path):
                    if file.endswith('.java'):
                        res.append(os.path.join(path, file))
                return res

        elif option == '-f':
            if not path.endswith('.java'):
                report_error("incorrect format of the file=%s" % path)
            elif not os.path.isfile(path):
                report_error("given path=%s isn't a file" % path)
            else:
                return [path]
        else:
            report_error("working option '%s' path isn't supported" % option)

    @staticmethod
    def process_files(action, files):
        formatter = CodeFormatter()

        if action in ('--format', '-f'):
            func = formatter.format
        elif action in ('--verify', '-v'):
            func = formatter.format
        else:
            report_error("action %s isn't supported" % sys.argv[2])

        for file in files:
            print("Processing file=%s" % file)
            with open(file, "r") as f: javacode = f.read()

            tokens = jl.tokenizer.tokenize(javacode, ignore_errors= True)
            try:
                output = formatter.format(tokens)
            except BaseException as ex:
                print("Exception received: %s" %ex)
            
            # TODO: add output to the respective directory
            print(output)

    @staticmethod
    def handle_parameters():
        if len(sys.argv) == 2:
            # name, action{--help, -h}
            if not sys.argv[1] in ('--help', '-h'):
                report_error("option '%s' isn't supported by the script" % sys.argv[1])

            print("------------------This is simple Python formatter for Java code---------------------\n"
                  "Available execution templates are:\n"
                  "1) name, action{--help, -h};\n"
                  "2) name, action{--format, -f, --verify, -v}, template={path|default}, option{-(p|d|f)}, path.\n"
                  "-------------------------------------------------------------------------------------")

        elif len(sys.argv) == 5:
            # name, action{--format, -f, --verify, -v}, template={path|default}, option{-(p|d|f)}, path
            config_path = sys.argv[2].split('=')[1]
            if config_path != 'default': report_error("config path isn't supported")

            files = prepare_formatting_files(sys.argv[3], path)

            process_files(sys.argv[3], files)
        else:
            report_error("incorrect amount of script arguments - %s" % len(sys.argv))
