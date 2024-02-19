import sys
import typing

GenericType = typing.TypeVar("GenericType")

class AppOverrideState:
    addon_paths: typing.Any
    addons: typing.Any
    class_ignore: typing.Any
    ui_ignore_classes: typing.Any
    ui_ignore_label: typing.Any
    ui_ignore_menu: typing.Any
    ui_ignore_operator: typing.Any
    ui_ignore_property: typing.Any

    def setup(self): ...
    def teardown(self): ...
