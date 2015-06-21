import bpy
import os
from bpy.props import *

addon_name = os.path.basename(os.path.dirname(__file__))


def prop_changed(self, context):
    for area in bpy.context.screen.areas:
        if area.type == "TEXT_EDITOR":
            area.tag_redraw()

class ContextBoxProperties(bpy.types.PropertyGroup):
    font_size = IntProperty(default = 80, name = "Font Size", min = 10, update = prop_changed)
    line_height = IntProperty(default = 23, name = "Line Height", min = 5, update = prop_changed)
    width = IntProperty(default = 200, name = "Width", min = 10, update = prop_changed)
    padding = IntProperty(default = 5, name = "Padding", min = 0, update = prop_changed)

class AddonPreferences(bpy.types.AddonPreferences):
    bl_idname = addon_name
    
    context_box = PointerProperty(type = ContextBoxProperties)
    debug = BoolProperty(default = False, name = "Debug", update = prop_changed)
    
    def draw(self, context):
        layout = self.layout
        
        col = layout.column(align = True)
        col.label("Context Box")
        col.prop(self.context_box, "font_size")
        col.prop(self.context_box, "line_height")
        col.prop(self.context_box, "width")
        col.prop(self.context_box, "padding")
        
        layout.prop(self, "debug")
      
def get_settings():
    return getPreferences()
        
def getPreferences():
    addon = bpy.context.user_preferences.addons.get(addon_name)
    return getattr(addon, "preferences", None)