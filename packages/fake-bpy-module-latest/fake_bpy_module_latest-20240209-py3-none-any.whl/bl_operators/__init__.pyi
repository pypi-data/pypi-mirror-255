import sys
import typing
from . import vertexpaint_dirt
from . import file
from . import console
from . import rigidbody
from . import uvcalc_lightmap
from . import geometry_nodes
from . import node
from . import uvcalc_follow_active
from . import uvcalc_transform
from . import presets
from . import freestyle
from . import mesh
from . import spreadsheet
from . import screen_play_rendered_anim
from . import constraint
from . import wm
from . import view3d
from . import object
from . import object_quick_effects
from . import clip
from . import bmesh
from . import anim
from . import object_randomize_transform
from . import add_mesh_torus
from . import image
from . import userpref
from . import object_align
from . import sequencer
from . import assets

GenericType = typing.TypeVar("GenericType")

def register(): ...
def unregister(): ...
