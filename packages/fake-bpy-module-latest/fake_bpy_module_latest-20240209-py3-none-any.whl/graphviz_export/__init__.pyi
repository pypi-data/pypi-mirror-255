import sys
import typing

GenericType = typing.TypeVar("GenericType")

def compat_str(text, line_length): ...
def graph_armature(obj, filepath, FAKE_PARENT, CONSTRAINTS, DRIVERS, XTRA_INFO): ...
