import importlib
import importlib.util
import sys
from pathlib import Path
from typing import Union


def get_module_name(relative_path: Union[Path, str]):
    path = Path(relative_path).resolve()
    cwd = Path.cwd()
    try:
        relative_path = path.relative_to(cwd)
        module_name = str(relative_path).replace('/', '.').replace('\\', '.')
        if path.is_file():
            module_name = module_name.rsplit('.', 1)[0]
        return True, module_name
    except ValueError:
        return False, "Path is not a subpath of the current directory."


def load_module_by_spec(main_script: Union[Path, str]):
    flag, ret = get_module_name(main_script)
    if not flag:
        return False, ret
    spec = importlib.util.spec_from_file_location(ret, main_script)
    main = importlib.util.module_from_spec(spec)
    sys.modules[ret] = main
    spec.loader.exec_module(main)
    return True, "module loaded"
