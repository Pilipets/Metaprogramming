import os
import sys

from src.java_formatter_core import JavaFormatterCore, java_lexer
from config.config_handler import load_config

class JavaFormatterUI:
    def __init__(self, *args, **kwargs):
        raise NotImplementedError("not intended to initialize the class")

    help_text = (
"------------------Java code formatting or prettifying console application---------------------\n"
"Description:\n"
"    Briefly, the app uses command-line arguments to either format or verify .java files collected\n"
"    from the given directory, project, file location. The user can adjust formatting, verification\n"
"    options through a custom or default configuration file.\n\n"
"Usage instructions:\n"
"    1. Use --admin command-line option to run run_debug(...) method from java_formatter_ui.py\n"
"       - debug purposes. You can modify this method as you want.\n"
"    2. Use --help cmd argument to print the description info.\n"
"    3. The app supports up to 4 additional arguments:\n"
"      -> input_path{'string'} - required argument. It is a relative or absolute path to the\n"
"         folder, project, file, that is expecting to be processed by the app.\n"
"         Must be the last execution argument;\n"
"      -> option{-(p|d|f)} - required argument. Specifies the execution policy - directory\n"
"         recursively, directory without recursion, one file. The app uses the input path and\n"
"         provided option argument to get the files with .java format that don't start with\n"
"         'formatted_', 'verified_' prefixes - those prefixes are reserved;\n"
"      -> (--config|-c)=path - optional argument. If not provided, options from config/config_handler.py\n"
"         are used. Specifies the code formatting options - the user can view all the supported\n"
"         options in the config/example_config.json file;\n"
"      -> action{--beautify, -b, --verify, -v} - optional argument. Specifies the execution mode:\n"
"         either formats or verifies the input files considering config and 'option' argument,\n"
"         locates the result files in the input_path directory with the prefixes 'formatted_' and\n"
"         'verified_' respectively.\n"
"    4. To RUN the application, you must execute java_formatter_app.py script with the respective\n"
"       arguments, ending with the input_path.\n"
"       Example: python3 CodeFormatter\(Java\)/java_formatter_app.py -b -d\n"
"       --config=/mnt/c/Debug/app_config.json /mnt/e/Documents/input_files\n"
"-----------------------------------------------------------------------------------------------------\n"
"                             Feel free to modify the code as you wish!!!\n")

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

        elif option == '-d':
            if not os.path.isdir(path):
                JavaFormatterUI.report_error("given path=%s isn't a directory" % path)
            else:
                for file in os.listdir(path):
                    if os.path.isfile(os.path.join(path, file)) and (
                            file.endswith('.java') and not file.startswith('formatted_')
                            and not file.startswith('verified_')):
                        res.append(os.path.join(path, file))

        elif option == '-f':
            if not path.endswith('.java'):
                JavaFormatterUI.report_error("incorrect format of the file=%s" % path)
            elif not os.path.isfile(path):
                JavaFormatterUI.report_error("given path=%s isn't a file" % path)
            else:
                res = [path]

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
                with open(file, "r", encoding='utf-8') as fin:
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

            with open(result_file, "w", encoding='utf-8') as fout:
                fout.write(output)

        print('Processed %d files successfully, %d files with errors' % (success_cnt, errors_cnt))

    @staticmethod
    def run_debug():
        with open(os.path.join("input", "code3.txt"), "r", encoding='utf-8') as fin:
            javacode = fin.read()

        tokens_stream = java_lexer.tokenize(javacode, raise_errors=True)
        formatter = JavaFormatterCore()
        output = formatter.verify(tokens_stream)
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
            if len(config) > 1:
                JavaFormatterUI.report_error("incorrect config file options")
            elif len(config) == 1:
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
