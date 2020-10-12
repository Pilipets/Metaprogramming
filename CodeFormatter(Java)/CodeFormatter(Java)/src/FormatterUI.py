from src.CodeFormatter import *
import sys
import os

class FormatterUI:
    help_text = ("------------------This is simple Python formatter for Java code---------------------\n"
                  "Available execution templates are:\n"
                  "1) name, action{--help, -h};\n"
                  "2) name, action{--format, -f, --verify, -v}, template={path|default}, option{-(p|d|f)}, path.\n"
                  "-------------------------------------------------------------------------------------")

    @staticmethod
    def report_error(x):
        print("Error: {}, use --help for more details!".format(x))
        sys.exit()

    @staticmethod
    def prepare_formatting_files(option, path):
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

    @staticmethod
    def process_files(action, files, in_path):
        formatter = CodeFormatter()

        format_flag = False
        if action in ('--format', '-f'):
            func = formatter.format
            format_option = True
        elif action in ('--verify', '-v'):
            report_error("{} isn't supported".format(action))

        success_cnt, errors_cnt = 0, 0
        for file in files:
            with open(file, "r") as f: javacode = f.read()

            tokens = jl.tokenizer.tokenize(javacode, ignore_errors= True)
            try:
                output = func(tokens)
            except BaseException as ex:
                print("Exception received when formatting file={}, ex={}".format(file, ex))
                errors_cnt += 1
            else:
                success_cnt += 1

            result_file = ('formatted_' if format_flag else 'verified_') + file
            with open(result_file, "r") as f: f.write(output)

        print(('Processed %d files successfully, %f files with errors' % success_cnt, errors_cnt))

    @staticmethod
    def handle_parameters():
        params = set(sys.argv)

        if len(sys.argv) != len(params):
            report_error('incorrect parameters amount of the script')

        if '-h' in params or '--help' in params:
            # name, action{--help, -h}
            if len(params) != 2:
                report_error("option '%s' isn't supported by the script" % sys.argv[1])

            print(help_text)

        else:
            # name, action{--format, -f, --verify, -v}, {--config, -c}=path, option{-(p|d|f)}, in_path
            if len(params) > 5:
                report_error("incorrect amount of the script arguments, given - %s" % len(params))

            action = [c for c in ('-f', '--format', '--verify', '-v') if c in params]
            if len(option) > 1:
                report_error("incorrect usage of flags %s" % action)
            else:
                action = action[0] if len(action) else '-f'

            if '--config' in params or '-c' in params:
                report_error("config path isn't supported")

            option = [c for c in ('-p', '-d', '-f') if c in params]
            if len(option) > 1 or len(option) == 0:
                report_error("incorrect usage of flags %s" % option)
            else:
                option = option[0]

            in_path = sys.argv[-1]

            files = prepare_formatting_files(option, in_path)
            process_files(action, files, in_path)