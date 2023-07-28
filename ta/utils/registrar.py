from pathlib import Path
import importlib
import inspect

TEST_CLASSES = {}
INSTR_CLASSES = {}


def register_classes(module) -> None:
    """
    Used to register external instruments to be used with the instrument manager and tests to be used the test exec.

    :param module: The module or folder with modules which contain tests or instruments
    :return: None
    """

    def add_class(mod):
        for name, obj in inspect.getmembers(mod):
            if inspect.isclass(obj):
                if hasattr(obj, '_ta_instr') and obj._ta_instr:
                    INSTR_CLASSES[name] = obj
                elif hasattr(obj, '_ta_test') and obj._ta_test:
                    TEST_CLASSES[name] = obj

    try:
        mod_path = Path(module.__path__._path[0])
        for mods in sorted(mod_path.glob('*.py')):
            name = f'{module.__name__}.{mods.stem}'
            mod = importlib.import_module(name=name)
            add_class(mod)
    except AttributeError:
        add_class(module)





