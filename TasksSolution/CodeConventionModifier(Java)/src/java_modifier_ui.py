import os, sys
from timeit import default_timer as timer

from src.core.java_modifier_core import JavaModifierCore

class JavaModifierUI:
    def __init__(self, *args, **kwargs):
        raise NotImplementedError('{} not intended to be instantiated'.format(
            self.__class__))

    help_text = ('Dummy help info!!!'.center(50, '-'))

    @staticmethod
    def report_error(err):
        print("Error: {}, use --help for more details!".format(err))
        sys.exit()

    @staticmethod
    def get_processing_file_paths(option, path):
        res = []
        if option == '-p':
            if not os.path.isdir(path):
                JavaModifierUI.report_error("given path=%s isn't a directory" % path)
            else:
                for root, dirs, files in os.walk(path):
                    for file in files:
                        if (file.endswith('.java') and not file.startswith('modified_')):
                            res.append(os.path.join(root, file))

        elif option == '-d':
            if not os.path.isdir(path):
                JavaModifierUI.report_error("given path=%s isn't a directory" % path)
            else:
                for file in os.listdir(path):
                    if os.path.isfile(os.path.join(path, file)) and (
                            file.endswith('.java') and not file.startswith('modified_')):
                        res.append(os.path.join(path, file))

        elif option == '-f':
            if not path.endswith('.java'):
                JavaModifierUI.report_error("incorrect format of the file=%s" % path)
            elif not os.path.isfile(path):
                JavaModifierUI.report_error("given path=%s isn't a file" % path)
            else:
                res = [path]

        return res

    @staticmethod
    def process_files(action, files, touch_docs):
        print('%d files collected, initializing the process...' % len(files))
        start = timer()
        modifier = JavaModifierCore()
        modifier.initialize(files)

        seconds, start = round(timer() - start, 4), timer()
        print(f'Initialization completed in {seconds} seconds')

        func = modifier.modify_one
        if action in ('--verify', '-v'):
            func = modifier.verify_one

        start = timer()
        success_cnt, errors_cnt = 0, 0
        for idx, file in enumerate(files):
            try:
                func(file, touch_docs)
            except Exception as ex:
                print("Exception received when processing file={}, ex={}".format(file, ex))
                errors_cnt += 1
            else:
                success_cnt += 1

            if (idx+1) % 100 == 0:
                percents = round((idx+1)/len(files)*100, 3)
                seconds = round(timer() - start, 4)
                print(f'{idx+1}({percents}%) files processed in {seconds} seconds')

        modifier.finalize()

        print('Processed %d files successfully, %d files with errors' % (success_cnt, errors_cnt))

    @staticmethod
    def run_debug():
        print('START'.center(60, '-'))
        file_path = os.path.join("input", "code.java")

        core = JavaModifierCore()
        core.initialize([file_path])
        core.modify_one(file_path, touch_docs = False, produce_file = False)
        core.finalize()

        print('END'.center(60, '-'))

    @staticmethod
    def handle_parameters():
        params = set(sys.argv)

        if len(sys.argv) != len(params) or len(params) < 2:
            JavaModifierUI.report_error('incorrect parameters amount of the script')

        if '--admin' in params:
            JavaModifierUI.run_debug()

        elif '-h' in params or '--help' in params:
            # name, action{--help, -h}
            if len(params) != 2:
                JavaModifierUI.report_error(
                    "option '%s' isn't supported by the script" % sys.argv[1])

            print(JavaModifierUI.help_text)

        else:
            # name, action{--modify, -m, --verify, -v}, option{-(p|d|f)}, optional(--doc) in_path
            if len(params) > 5:
                JavaModifierUI.report_error(
                    "incorrect amount(%d) of the script arguments"% len(params))

            action = [c for c in ('-m', '--modify', '--verify', '-v') if c in params]
            if len(action) > 1:
                JavaModifierUI.report_error("incorrect usage of action flags %s" % action)
            else:
                action = action[0] if action else '-m'

            option = [c for c in ('-p', '-d', '-f') if c in params]
            if len(option) > 1 or len(option) == 0:
                JavaModifierUI.report_error("incorrect usage of option flags %s" % option)
            else:
                option = option[0]

            touch_doc = True if '--doc' in params else False

            files = JavaModifierUI.get_processing_file_paths(option, sys.argv[-1])
            JavaModifierUI.process_files(action, files, touch_doc)