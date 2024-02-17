"""Factory of checker classes"""
from pplog.config import get_class_from_dot_path, get_ppconfig


def get_class(key):
    """Given a configuration, retrieves the correct class and arguments passed."""
    config: dict = get_ppconfig()
    params: dict = config[key]
    check_class_str: str = params["log_check_class"]
    check_class_arguments = params.get("arguments", {})
    check_class = get_class_from_dot_path(check_class_str)
    return check_class, check_class_arguments
