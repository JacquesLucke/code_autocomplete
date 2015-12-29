import bpy
from bpy.props import *

class AddonDevelopmentSceneProperties(bpy.types.PropertyGroup):
    addon_name = StringProperty(name = "Addon Name", default = "", description = "Name of the currently selected addon")
