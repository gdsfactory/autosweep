from pathlib import Path
import importlib

TEST_CLASSES = {}
INSTR_CLASSES = {}

#
# from os.path import dirname, basename, isfile, join
# import glob
# modules = glob.glob(join(dirname(__file__), "*.py"))
# __all__ = [ basename(f)[:-3] for f in modules if isfile(f) and

def register_test(test):
    TEST_CLASSES[test.__name__] = test


def register_instr(instr):
    INSTR_CLASSES[instr.__name__] = instr


def register_classes(module):
    mod_path = Path(module.__path__._path[0])
    for mods in sorted(mod_path.glob('*.py')):
        importlib.import_module(name=f'{module.__name__}.{mods.stem}')
