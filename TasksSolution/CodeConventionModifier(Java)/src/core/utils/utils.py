import logging, os, sys


class ModifierError(Exception):
    pass

class NamesResolverError(ModifierError):
    pass

rel_path = os.path.join(os.path.split(sys.argv[0])[0], 'output')

def setup_logger(logger_name, level=logging.WARNING):
    log_file = os.path.join(rel_path, f'{logger_name}.log')
    # Erase log if already exists
    if os.path.exists(log_file): os.remove(log_file)

    # Configure log file
    logger = logging.getLogger(logger_name)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    f_handler = logging.FileHandler(log_file, mode='w')
    f_handler.setFormatter(formatter)

    logger.setLevel(level)
    logger.addHandler(f_handler)

    return logger