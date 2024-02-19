import sys
import typing
import bpy.types

from . import types
from . import ops
from . import utils
from . import app
from . import props
from . import msgbus
from . import path

GenericType = typing.TypeVar("GenericType")
context: "bpy.types.Context"

data: "bpy.types.BlendData"
""" Access to Blender's internal data
"""
