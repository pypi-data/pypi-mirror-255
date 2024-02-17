""" Static configuration """


from enum import Enum
from operator import eq, gt, lt
from typing import Callable


class Operator(Enum):
    """Operator callables"""

    def __get__(self, instance, owner) -> Callable:
        return self.value

    LESSER_THAN = lt
    GREATER_THAN = gt
    EQUAL = eq
