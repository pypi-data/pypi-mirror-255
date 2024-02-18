from __future__ import annotations
from configparser import RawConfigParser
from decimal import Decimal
import re
from typing import Any, Callable, Iterable, TypeVar, overload

T = TypeVar('T')


def get_iterable_element_type(iterable: Iterable, *possible_types: type) -> type|None:
    """
    Get the type of all elements of the iterable amongst the possible types given as argument.
    """
    if not possible_types:
        raise NotImplementedError() # TODO: requires more thinking
    
    remaining_types = list(possible_types)

    for element in iterable:
        types_to_remove = []

        for possible_type in remaining_types:
            if not issubclass(type(element), possible_type):
                types_to_remove.append(possible_type)

        for type_to_remove in types_to_remove:
            remaining_types.remove(type_to_remove)
    
    return remaining_types[0] if remaining_types else None


def is_iterable_of(iterable: Iterable, element_type: type|tuple[type]):
    for element in iterable:
        if not isinstance(element, element_type):
            return False
        
    return True


@overload
def convert(value: Any, to: type[T], *, nullval = None, if_none = None) -> T:
    ...


def convert(value: Any, to: type[T]|Callable, *, nullval = None, if_none = None):
    if value == nullval:
        return None
    
    if not isinstance(to, type):
        return to(value)
    
    if isinstance(value, to):
        return value
    
    if value is None:
        return if_none
    
    strvalue = str(value)

    if to == str:
        return strvalue
    
    elif to == bool:
        lower = strvalue.lower()
        if lower not in RawConfigParser.BOOLEAN_STATES:
            raise ValueError('Not a boolean: %s' % strvalue)
        return RawConfigParser.BOOLEAN_STATES[lower]

    elif to in [float,Decimal]:
        return to(strvalue.replace(',', '.'))
    
    elif to == list:
        strvalue = strvalue.strip()
        if not strvalue:
            return []
        return re.split(r'[\W,;|]+', strvalue)
    
    else:
        return to(strvalue)


def convert_to_bool(value: Any, *, nullval = None, if_none = None):
    return convert(value, bool, nullval=nullval, if_none=if_none)

def convert_to_int(value: Any, *, nullval = None, if_none = None):
    return convert(value, int, nullval=nullval, if_none=if_none)

def convert_to_decimal(value: Any, *, nullval = None, if_none = None):
    return convert(value, Decimal, nullval=nullval, if_none=if_none)


def get_leaf_classes(cls: type[T]) -> list[type[T]]:
    cls_list = []

    def recurse(cls: type):
        subclasses = cls.__subclasses__()
        if subclasses:
            for subcls in subclasses:
                recurse(subcls)
        else:
            cls_list.append(cls)

    recurse(cls)
    return cls_list