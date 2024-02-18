"""New hook for easily checking boolean flags."""
from pplog.factory import get_class


def log_check_boolean(key: str, boolean_value: bool):
    """Simple Hook to check a float value against monitoring configuration.

    Useful when a more specific hook is not available for the use case.
    """
    check_class, check_class_arguments = get_class(key)
    check_class(key, boolean_value, check_class_arguments).run_check()
