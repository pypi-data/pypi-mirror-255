""" Configuration utility modules """
import importlib
from typing import Callable


def get_class_from_dot_path(path: str) -> Callable:
    """Imports module from dot notation string path"""
    module_path, class_name = path.rsplit(".", 1)
    try:
        module = importlib.import_module(module_path)
        return getattr(module, class_name)
    except (ModuleNotFoundError, AttributeError) as exp:
        raise ValueError(f"Provided log check class path <{path}> is invalid") from exp
