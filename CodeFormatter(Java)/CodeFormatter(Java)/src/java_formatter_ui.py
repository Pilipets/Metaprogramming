import os
import sys

from src.java_formatter_core import JavaFormatterCore, java_lexer
from config.config_handler import load_config

class JavaFormatterUI:
    def __init__(self, *args, **kwargs):
        raise NotImplementedError("not intended to initialize the class")

    help_text = (
        "------------------This is simple Python formatter for Java code---------------------\n"
        "Available execution templates are:\n"
        "1) name, action{--help, -h};\n"
        "2) name, action{--beautify, -b, --verify, -v}, "
        "(--config|-c)=path, option{-(p|d|f)}, input_path.\n"
        "-------------------------------------------------------------------------------------")

    @staticmethod
    def report_error(err):
        print("Error: {}, use --help for more details!".format(err))
        sys.exit()

    @staticmethod
    def prepare_formatting_files(option, path):
        res = []
        if option == '-p':
            if not os.path.isdir(path):
                JavaFormatterUI.report_error("given path=%s isn't a directory" % path)
            else:
                for root, dirs, files in os.walk(path):
                    for file in files:
                        if (file.endswith('.java') and not file.startswith('formatted_')
                                and not file.startswith('verified_')):
                            res.append(os.path.join(root, file))
                return res

        elif option == '-d':
            if not os.path.isdir(path):
                JavaFormatterUI.report_error("given path=%s isn't a directory" % path)
            else:
                for file in os.listdir(path):
                    if (file.endswith('.java') and not file.startswith('formatted_')
                            and not file.startswith('verified_')):
                        res.append(os.path.join(path, file))
                return res

        elif option == '-f':
            if not path.endswith('.java'):
                JavaFormatterUI.report_error("incorrect format of the file=%s" % path)
            elif not os.path.isfile(path):
                JavaFormatterUI.report_error("given path=%s isn't a file" % path)
            else:
                return [path]

        return res

    @staticmethod
    def process_files(action, files):
        formatter = JavaFormatterCore()

        format_flag, func = True, formatter.format
        if action in ('--verify', '-v'):
            format_flag, func = False, formatter.verify

        success_cnt, errors_cnt = 0, 0
        for file in files:
            try:
                with open(file, "r") as fin:
                    javacode = fin.read()

                output = func(java_lexer.tokenize(javacode, raise_errors=False))
            except Exception as ex:
                print("Exception received when formatting file={}, ex={}".format(file, ex))
                errors_cnt += 1
                output = ''
            else:
                success_cnt += 1

            head, tail = os.path.split(file)
            if format_flag:
                result_file = os.path.join(head, 'formatted_' + tail)
            else:
                result_file = os.path.join(head, 'verified_' + os.path.splitext(tail)[0] + '.log')

            with open(result_file, "w") as fout:
                fout.write(output)

        print('Processed %d files successfully, %d files with errors' % (success_cnt, errors_cnt))

    @staticmethod
    def run_debug():
        with open(os.path.join("input", "code3.txt"), "r") as fin:
            javacode = fin.read()

        tokens_stream = java_lexer.tokenize(javacode, raise_errors=False)
        formatter = JavaFormatterCore()
        output = formatter.format(tokens_stream)
        print(output)

    @staticmethod
    def handle_parameters():
        params = set(sys.argv)

        if len(sys.argv) != len(params) or len(params) < 2:
            JavaFormatterUI.report_error('incorrect parameters amount of the script')

        if '--admin' in params:
            JavaFormatterUI.run_debug()

        elif '-h' in params or '--help' in params:
            # name, action{--help, -h}
            if len(params) != 2:
                JavaFormatterUI.report_error(
                    "option '%s' isn't supported by the script" %sys.argv[1])

            print(JavaFormatterUI.help_text)

        else:
            # name, action{--beautify, -b, --verify, -v},
            # {--config, -c}=path, option{-(p|d|f)}, in_path
            if len(params) > 5:
                JavaFormatterUI.report_error(
                    "incorrect amount(%d) of the script arguments"% len(params))

            action = [c for c in ('-b', '--beautify', '--verify', '-v') if c in params]
            if len(action) > 1:
                JavaFormatterUI.report_error("incorrect usage of action flags %s" % action)
            else:
                action = action[0] if action else '-b'

            config = [c for c in params if c.startswith('--config=') or c.startswith('-c=')]
            if len(config) > 1 or not config:
                JavaFormatterUI.report_error("incorrect config file options")

            config = config[0].split('=', 1)[1]
            try:
                load_config(config)
            except Exception as ex:
                JavaFormatterUI.report_error("error encountered when loading config file, %s" % ex)

            option = [c for c in ('-p', '-d', '-f') if c in params]
            if len(option) > 1 or len(option) == 0:
                JavaFormatterUI.report_error("incorrect usage of option flags %s" % option)
            else:
                option = option[0]

            files = JavaFormatterUI.prepare_formatting_files(option, sys.argv[-1])
            JavaFormatterUI.process_files(action, files)
