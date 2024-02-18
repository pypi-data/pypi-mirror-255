import sys
import typing

GenericType = typing.TypeVar("GenericType")

class AssetBrowserPanel:
    bl_space_type: typing.Any

    def asset_browser_panel_poll(self, context): ...
    def poll(self, context): ...

class AssetMetaDataPanel:
    bl_region_type: typing.Any
    bl_space_type: typing.Any

    def poll(self, context): ...

class SpaceAssetInfo: ...
