import sys
import typing

GenericType = typing.TypeVar("GenericType")

class I18nSettings:
    BLENDER_I18N_PO_DIR: typing.Any
    BLENDER_I18N_ROOT: typing.Any
    FILE_NAME_POT: typing.Any
    POTFILES_SOURCE_DIR: typing.Any
    PRESETS_DIR: typing.Any
    PY_SYS_PATHS: typing.Any
    TEMPLATES_DIR: typing.Any
    WORK_DIR: typing.Any

    def from_dict(self, mapping): ...
    def from_json(self, string): ...
    def load(self, fname, reset): ...
    def save(self, fname): ...
    def to_dict(self): ...
    def to_json(self): ...
