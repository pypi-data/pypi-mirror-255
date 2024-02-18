import sys
import typing

GenericType = typing.TypeVar("GenericType")

def build_property_typemap(skip_classes, skip_typemap): ...
def print_ln(data): ...
def rna2xml(
    fw,
    root_node,
    root_rna,
    root_rna_skip,
    root_ident,
    ident_val,
    skip_classes,
    skip_typemap,
    pretty_format,
    method,
): ...
def xml2rna(root_xml, root_rna): ...
def xml_file_run(context, filepath, rna_map): ...
def xml_file_write(context, filepath, rna_map, skip_typemap): ...
