import os
import sys

from src.CodeFormatter import CodeFormatter, jl

class FormatterUI:
    def __init__(self, *args, **kwargs):
        raise NotImplementedError("not intended to initialize the class")

    help_text = (
        "------------------This is simple Python formatter for Java code---------------------\n"
        "Available execution templates are:\n"
        "1) name, action{--help, -h};\n"
        "2) name, action{--beautify, -b, --verify, -v}, "
        "template={path|default}, option{-(p|d|f)}, path.\n"
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
                FormatterUI.report_error("given path=%s isn't a directory" % path)
            else:
                for root, dirs, files in os.walk(path):
                    for file in files:
                        if (file.endswith('.java') and not file.startswith('formatted_')
                                and not file.startswith('verified_')):
                            res.append(os.path.join(root, file))
                return res

        elif option == '-d':
            if not os.path.isdir(path):
                FormatterUI.report_error("given path=%s isn't a directory" % path)
            else:
                for file in os.listdir(path):
                    if (file.endswith('.java') and not file.startswith('formatted_')
                            and not file.startswith('verified_')):
                        res.append(os.path.join(path, file))
                return res

        elif option == '-f':
            if not path.endswith('.java'):
                FormatterUI.report_error("incorrect format of the file=%s" % path)
            elif not os.path.isfile(path):
                FormatterUI.report_error("given path=%s isn't a file" % path)
            else:
                return [path]

    @staticmethod
    def process_files(action, files, in_path):
        formatter = CodeFormatter()

        format_flag = False
        if action in ('--beautify', '-b'):
            func = formatter.format
            format_flag = True
        elif action in ('--verify', '-v'):
            func = formatter.verify
            format_flag = False

        success_cnt, errors_cnt = 0, 0
        for file in files:
            with open(file, "r") as f: javacode = f.read()

            tokens = jl.tokenizer.tokenize(javacode, ignore_errors=True)
            try:
                output = func(tokens)
            except BaseException as ex:
                print("Exception received when formatting file={}, ex={}".format(file, ex))
                errors_cnt += 1
                output = ''
            else:
                success_cnt += 1

            head, tail = os.path.split(file)
            result_file = os.path.join(head, ('formatted_' if format_flag else 'verified_') + tail)
            with open(result_file, "w") as f: f.write(output)

        print('Processed %d files successfully, %d files with errors' % (success_cnt, errors_cnt))

    @staticmethod
    def handle_parameters():
        params = set(sys.argv)

        if len(sys.argv) != len(params):
            FormatterUI.report_error('incorrect parameters amount of the script')

        if '-h' in params or '--help' in params:
            # name, action{--help, -h}
            if len(params) != 2:
                FormatterUI.report_error("option '%s' isn't supported by the script" % sys.argv[1])

            print(help_text)

        else:
            # name, action{--beautify, -b, --verify, -v}, {--config, -c}=path, option{-(p|d|f)}, in_path
            if len(params) > 5:
                FormatterUI.report_error("incorrect amount(%d) of the script arguments" % len(params))

            action = [c for c in ('-b', '--beautify', '--verify', '-v') if c in params]
            if len(action) > 1:
                FormatterUI.report_error("incorrect usage of action flags %s" % action)
            else:
                action = action[0] if len(action) else '-b'

            if '--config' in params or '-c' in params:
                FormatterUI.report_error("config path isn't supported")

            option = [c for c in ('-p', '-d', '-f') if c in params]
            if len(option) > 1 or len(option) == 0:
                FormatterUI.report_error("incorrect usage of option flags %s" % option)
            else:
                option = option[0]

            in_path = sys.argv[-1]

            files = FormatterUI.prepare_formatting_files(option, in_path)
            FormatterUI.process_files(action, files, in_path)
