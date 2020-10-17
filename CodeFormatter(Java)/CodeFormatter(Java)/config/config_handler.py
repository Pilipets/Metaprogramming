import json

def load_config(path):
    config_dic = {}

    with open(path, 'r') as fin:
        config_dict = json.loads(fin.read())
    module_attrs = globals()

    def set_params_from_list(config_dict, main_key, attr_list):
        arr = config_dict.get(main_key, None)
        if not arr:
            return

        for key in attr_list:
            val = arr.get(key, None)
            if val is not None:
                module_attrs[key] = val

    set_params_from_list(config_dict, 'tabs_indents_menu',
                         ('use_tab_character',
                          'tab_size',
                          'indent',
                          'continuation_indent',
                          'label_indent',
                          'absolute_label_indent'
                          ))

    spaces_menu = config_dic.get('spaces_menu', None)
    if spaces_menu:
        set_params_from_list(spaces_menu, 'before_parentheses',
                             ('space_before_method_p',
                              'space_before_if_p',
                              'space_before_for_p',
                              'space_before_while_p',
                              'space_before_switch_p',
                              'space_before_try_p',
                              'space_before_catch_p',
                              'space_before_synchronized_p',
                              'space_before_annotation_p'
                              ))

        set_params_from_list(spaces_menu, 'before_braces',
                             ('space_before_class_b',
                              'space_before_method_b',
                              'space_before_if_b',
                              'space_before_else_b',
                              'space_before_for_b',
                              'space_before_while_b',
                              'space_before_do_b',
                              'space_before_switch_b',
                              'space_before_try_b',
                              'space_before_catch_b',
                              'space_before_finally_b',
                              'space_before_synchronized_b',
                              'space_before_initialization_b',
                              'space_before_annotation_b',
                              'space_before_lambda_b'
                              ))

        set_params_from_list(spaces_menu, 'before_keywords',
                             ('space_before_while_keyword',
                              'space_before_else_keyword',
                              'space_before_catch_keyword',
                              'space_before_finally_keyword'
                              ))

        set_params_from_list(spaces_menu, 'within_keywords',
                             ('space_after_semicolon',
                              'space_before_semicolon'
                              ))

        set_params_from_list(spaces_menu, 'type_arguments',
                             ('space_around_colon_for_each'
                              ))

        set_params_from_list(spaces_menu, 'around_parentheses',
                             ('space_around_equality',
                              'space_around_logical',
                              'space_around_bitwise',
                              'space_around_assignment',
                              'space_around_relational',
                              'space_around_method_reference',
                              'space_around_unary',
                              'space_around_lambda_arrow',
                              'space_around_additive',
                              'space_around_shift',
                              'space_around_operator',
                              'space_around_ternary'
                              ))



    set_params_from_list(config_dict, 'wrapping_and_braces',
                         ('brace_in_class_declaration',
                          'brace_in_method_declaration',
                          'brace_in_lambda_declaration',
                          'brace_other',
                          'new_line_before_else',
                          'new_line_while',
                          'indent_case_branches',
                          'catch_on_new_line',
                          'finally_on_new_line'
                          ))



### Config file for the code formatter

### Tabs and indents

use_tab_character = False

# the number of spaces included in a tab.
tab_size = 4

# the number of spaces (or tabs if the Use tab character checkbox is selected)
# to be inserted for each indent level.
indent = 4

# the number of spaces (or tabs) to be inserted between the elements of an
# array, in expressions, method declarations and method calls.
continuation_indent = 1

# the number of spaces (or tabs if the Use tab character checkbox is selected)
# to be inserted at the next line before a label statement.
label_indent = 2

# If this checkbox is selected, label indentation is counted as an
# absolute number of spaces. Otherwise, label indentation is counted
# relative to previous indent levels.
absolute_label_indent = False

### Spaces

# Before parentheses
space_before_method_p = False
space_before_if_p = True
space_before_for_p = True
space_before_while_p = False
space_before_switch_p = True
space_before_try_p = False
space_before_catch_p = False
space_before_synchronized_p = True
space_before_annotation_p = True

# Before brace
space_before_class_b = True
space_before_method_b = True
space_before_if_b = True
space_before_else_b = True
space_before_for_b = True
space_before_while_b = True
space_before_do_b = True
space_before_switch_b = True
space_before_try_b = False
space_before_catch_b = True
space_before_finally_b = True
space_before_synchronized_b = True
space_before_initialization_b = True
space_before_annotation_b = False
space_before_lambda_b = True

# Before keywords
space_before_while_keyword = True
space_before_else_keyword = True
space_before_catch_keyword = True
space_before_finally_keyword = True

# type arguments
space_after_comma = True

# other in for, try, ...
space_after_semicolon = True
space_before_semicolon = False
space_around_colon_for_each = True

# Around parentheses
space_around_equality = True
space_around_logical = True
space_around_bitwise = False
space_around_assignment = True
space_around_relational = True
space_around_method_reference = False
space_around_unary = False
space_around_lambda_arrow = False
space_around_additive = True
space_around_shift = True
space_around_operator = False
space_around_ternary = True

# braces placement
# next_line, end_of_line
brace_in_class_declaration = 'end_of_line'
brace_in_method_declaration = 'end_of_line'
brace_in_lambda_declaration = 'next_line'
brace_other = 'end_of_line'

# if statement
new_line_before_else = True

# do ... while
new_line_while = False

# switch statement
indent_case_branches = True

# try statement
catch_on_new_line = False
finally_on_new_line = False
