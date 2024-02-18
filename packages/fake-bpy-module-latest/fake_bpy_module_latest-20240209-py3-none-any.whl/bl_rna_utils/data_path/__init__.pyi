import sys
import typing

GenericType = typing.TypeVar("GenericType")

class _TokenizeDataPath:
    data_path: typing.Any

def decompose_data_path(data_path): ...
def property_definition_from_data_path(base, data_path): ...
