import os, sys, string

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
                        if (file.endswith('.java') and not file.startswith('modified_')
                                and not file.startswith('verified_')):
                            res.append(os.path.join(root, file))

        elif option == '-d':
            if not os.path.isdir(path):
                JavaModifierUI.report_error("given path=%s isn't a directory" % path)
            else:
                for file in os.listdir(path):
                    if os.path.isfile(os.path.join(path, file)) and (
                            file.endswith('.java') and not file.startswith('modified_')
                            and not file.startswith('verified_')):
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
    def process_files(action, files):
        pass

    @staticmethod
    def run_debug():
        javacode = ''
        with open(os.path.join("input", "code.java"), "r", encoding='utf-8') as fin:
            javacode = fin.read()

        core = JavaModifierCore()
        core.initialize_modify()
        core.modify_one(javacode)
        print('Done')

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
            pass