from pathlib import Path
import importlib

from ta import instruments
from ta import tests

TEST_CLASSES = {}
INSTR_CLASSES = {}


def _register_class(add_class, registry):
    name = add_class.__name__
    if name in registry:
        curr_class = registry[name]
        raise Exception(f"This class, '{add_class}' overrides an already-defined class, '{curr_class}")

    registry[name] = add_class


def register_test(test):
    _register_class(add_class=test, registry=TEST_CLASSES)
    TEST_CLASSES[test.__name__] = test


def register_instr(instr):
    _register_class(add_class=instr, registry=INSTR_CLASSES)


def register_classes(module):
    mod_path = Path(module.__path__._path[0])
    for mods in sorted(mod_path.glob('*.py')):
        importlib.import_module(name=f'{module.__name__}.{mods.stem}')


register_classes(tests)
register_classes(instruments)