""" fleks.util.types

This module collects common imports and annotation-types, i.e.
various optional/composite types used in type-hints, underneath
one convenient namespace.
"""

import typing
from pathlib import Path as BasePath

from types import *  # noqa
from typing import *  # noqa

from pydantic import BaseModel, Field, validate_arguments  # noqa

validate = validate_arguments

OptionalAny = typing.Optional[typing.Any]
PathType = type(BasePath())

Bool = bool
NoneType = type(None)

BoolMaybe = typing.Optional[bool]
StringMaybe = typing.Optional[str]
CallableMaybe = typing.Optional[typing.Callable]
DictMaybe = typing.Optional[typing.Dict]
TagDict = typing.Dict[str, str]


Namespace = typing.Dict[str, typing.Any]
CallableNamespace = typing.Dict[str, typing.Callable]


def new_in_class(name: str, kls: typing.Type) -> bool:
    """ """
    return name in dir(kls) and not any([name in dir(base) for base in kls.__bases__])


def is_subclass(x, y, strict=True) -> bool:
    """
    returns True if first argument is a subclass of second one.
    """
    if isinstance(x, (typing.Type)) and issubclass(x, y):
        if strict and x == y:
            return False
        return True
    return False


class classproperty:
    """ """

    def __init__(self, fxn):
        self.fxn = fxn

    def __get__(self, obj, owner) -> OptionalAny:  # noqa
        # assert obj
        return self.fxn(owner)


class classproperty_cached(classproperty):
    """ """

    CLASSPROP_CACHES = {}

    def __get__(self, obj, owner) -> OptionalAny:  # noqa
        # assert obj
        result = self.__class__.CLASSPROP_CACHES.get(self.fxn, self.fxn(owner))
        self.__class__.CLASSPROP_CACHES[self.fxn] = result
        return self.__class__.CLASSPROP_CACHES[self.fxn]
