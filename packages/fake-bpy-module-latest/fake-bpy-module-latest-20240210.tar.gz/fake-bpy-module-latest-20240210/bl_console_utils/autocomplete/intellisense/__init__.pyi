import sys
import typing

GenericType = typing.TypeVar("GenericType")

def complete(line, cursor, namespace, private): ...
def expand(line, cursor, namespace, private): ...
