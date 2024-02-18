import sys
import typing

GenericType = typing.TypeVar("GenericType")

class MotionPathButtonsPanel:
    bl_label: typing.Any
    bl_region_type: typing.Any
    bl_space_type: typing.Any

    def draw_settings(self, _context, avs, mpath, bones): ...

class MotionPathButtonsPanel_display:
    bl_label: typing.Any
    bl_region_type: typing.Any
    bl_space_type: typing.Any

    def draw_settings(self, _context, avs, mpath, bones): ...
