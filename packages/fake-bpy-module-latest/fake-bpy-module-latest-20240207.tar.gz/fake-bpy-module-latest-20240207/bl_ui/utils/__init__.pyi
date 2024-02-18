import sys
import typing

GenericType = typing.TypeVar("GenericType")

class PresetPanel:
    bl_label: typing.Any
    bl_region_type: typing.Any
    bl_space_type: typing.Any

    def draw(self, context): ...
    def draw_menu(self, layout, text): ...
    def draw_panel_header(self, layout): ...
    def path_menu(
        self,
        searchpaths,
        operator,
        props_default,
        prop_filepath,
        filter_ext,
        filter_path,
        display_name,
        add_operator,
    ): ...
