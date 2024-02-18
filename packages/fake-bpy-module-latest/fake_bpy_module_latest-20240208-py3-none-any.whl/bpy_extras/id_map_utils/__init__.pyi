import sys
import typing

GenericType = typing.TypeVar("GenericType")

def get_all_referenced_ids(i, ref_m):
    """Return a set of IDs directly or indirectly referenced by id."""

    ...

def get_id_reference_map():
    """Return a dictionary of direct datablock references for every datablock in the blend file."""

    ...

def recursive_get_referenced_ids(ref_map, id, referenced_ids, visited): ...
