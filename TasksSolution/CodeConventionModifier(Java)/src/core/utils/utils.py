import logging, os, sys

from ..tokenizer import java_tokens

class ModifierError(Exception):
    pass

class FormatterType:
    EXTENSIVE = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    SHORT = logging.Formatter('%(levelname)s - %(message)s')

def setup_logger(logger_name, level=logging.WARNING, formatter = FormatterType.EXTENSIVE):
    log_file = os.path.join(rel_path, f'{logger_name}.log')
    # Erase log if already exists
    if os.path.exists(log_file): os.remove(log_file)

    # Configure log file
    logger = logging.getLogger(logger_name)
    f_handler = logging.FileHandler(log_file, mode='w')
    f_handler.setFormatter(formatter)

    logger.setLevel(level)
    logger.addHandler(f_handler)

    return logger

rel_path = 'output'
os.makedirs(rel_path, exist_ok = True)
out_logger = setup_logger('RENAMED', logging.INFO, FormatterType.SHORT)

def unwind_tokens(tokens):
    res = []
    for idx, x in enumerate(tokens):
        if x.javadoc: res.append(x.javadoc)
        res.append(x)

    return res

def tricky_reformat(tokens, indices, changed):
    if len(tokens) == 0 or len(changed) != len(tokens):
        return ''

    idx = 0
    output = ''
    line, col = 1, 1
    line_shift, col_shift = 0, 0
    while idx < len(changed):
        x = changed[idx]
        is_new = False

        if not x.position:
            x.position = changed[idx+1].position
            is_new = True

        t_line, t_col = x.position
        t_line += line_shift
        if t_line != line:
            output += (t_line - line)*'\n'

            col, col_shift = 1, 0
            line = t_line

        t_col += col_shift
        if t_col != col:
            output += (t_col - col)*' '
            col = t_col

        output += x.value
        if is_new:
            # new java doc
            if isinstance(x, java_tokens.SingleLineComment):
                diff = 1

            else:
                output += '\n'
                diff = x.value.count('\n') + 1
         
            line_shift += diff
            line += diff
            col, col_shift = 1, 0
            idx += 1
            continue

        if isinstance(x, java_tokens.Comment):

            if isinstance(x, java_tokens.SingleLineComment):
                line += 1
                col, col_shift = 1, 0

            else:
                new_h = x.value.count('\n')
                line += new_h
                if indices[idx]:
                    pre_h = tokens[idx].value.count('\n')
                    line_shift += (new_h - pre_h)

                if new_h > 1: col, col_shift = 1, 0
                new_last = 0
                for ch in x.value.rsplit('\n', 1)[-1]:
                    if ch == '\t':
                        new_last += 4
                        new_last -= (new_last % 4)
                    else:
                        new_last += 1

                pre_last = 0
                if indices[idx]:
                    for ch in tokens[idx].value.rsplit('\n', 1)[-1]:
                        if ch == '\t':
                            pre_last += 4
                            pre_last -= (pre_last % 4)
                        else:
                            pre_last += 1

                    col_shift += (new_last - pre_last)
                col += new_last

        else:
            col_shift += len(x.value) - len(tokens[idx].value)
            col += len(x.value)

        idx += 1

    return output