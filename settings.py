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
    lines = IntProperty(default = 8, name = "Lines", min = 1, update = prop_changed)
    
class DescriptionBoxProperties(bpy.types.PropertyGroup):
    font_size = IntProperty(default = 80, name = "Font Size", min = 10, update = prop_changed)
    line_height = IntProperty(default = 23, name = "Line Height", min = 5, update = prop_changed)
    padding = IntProperty(default = 5, name = "Padding", min = 0, update = prop_changed)

class FakeModuleProperties(bpy.types.PropertyGroup):
    docstring_width = IntProperty(default = 70, name = "Docstring Width", min = 10)
    use_quote_marks = BoolProperty(default = False, name = "Use Quote Marks", description = "Create quote marks for each possible item for a enum property")

class AddonPreferences(bpy.types.AddonPreferences):
    bl_idname = addon_name
    
    context_box = PointerProperty(type = ContextBoxProperties)
    description_box = PointerProperty(type = DescriptionBoxProperties)
    fake_module = PointerProperty(type = FakeModuleProperties)
    debug = BoolProperty(default = False, name = "Debug", update = prop_changed)
    
    def draw(self, context):
        layout = self.layout
        
        row = layout.row()
        col = row.column(align = True)
        col.label("Context Box")
        col.prop(self.context_box, "font_size")
        col.prop(self.context_box, "line_height")
        col.prop(self.context_box, "width")
        col.prop(self.context_box, "padding")
        col.prop(self.context_box, "lines")
        
        col = row.column(align = True)
        col.label("Description Box")
        col.prop(self.description_box, "font_size")
        col.prop(self.description_box, "line_height")
        col.prop(self.description_box, "padding")
        
        col = layout.column(align = True)
        col.label("Fake Module")
        col.prop(self.fake_module, "docstring_width")
        col.prop(self.fake_module, "use_quote_marks")
        layout.prop(self, "debug")
      
def get_settings():
    return getPreferences()
        
def getPreferences():
    addon = bpy.context.user_preferences.addons.get(addon_name)
    return getattr(addon, "preferences", None)