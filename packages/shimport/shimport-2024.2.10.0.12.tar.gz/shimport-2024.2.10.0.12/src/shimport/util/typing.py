""" shimport.util.types

This module collects common imports and annotation-types, i.e.
various optional/composite types used in type-hints, underneath
one convenient namespace.
"""

import typing

from types import *  # noqa
from typing import *  # noqa


def new_in_class(name: str, kls: typing.Type):
    """

    :param name: str:
    :param kls: typing.Type:
    """
    return name in dir(kls) and not any([name in dir(base) for base in kls.__bases__])


def is_subclass(x, y, strict=True):
    """ """
    if isinstance(x, (typing.Type)) and issubclass(x, y):
        if strict and x == y:
            return False
        return True
    return False


OptionalAny = typing.Optional[typing.Any]

Bool = bool
NoneType = type(None)

BoolMaybe = typing.Optional[bool]
StringMaybe = typing.Optional[str]
CallableMaybe = typing.Optional[typing.Callable]
DictMaybe = typing.Optional[typing.Dict]

Namespace = typing.Dict[str, typing.Any]
CallableNamespace = typing.Dict[str, typing.Callable]
