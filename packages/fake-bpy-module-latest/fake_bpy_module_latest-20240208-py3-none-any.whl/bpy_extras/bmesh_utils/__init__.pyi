import sys
import typing

GenericType = typing.TypeVar("GenericType")

def bmesh_linked_uv_islands(bm, uv_layer): ...
def match_uv(face, vert, uv, uv_layer): ...
