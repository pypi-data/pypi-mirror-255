import sys
import typing

GenericType = typing.TypeVar("GenericType")

class RestrictBlend:
    context: typing.Any
    data: typing.Any

class _RestrictContext:
    preferences: typing.Any
    window_manager: typing.Any

class _RestrictData: ...
