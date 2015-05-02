'''
Copyright (C) 2014 Jacques Lucke
mail@jlucke.com

Created by Jacques Lucke

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

 
import importlib, sys, os
from fnmatch import fnmatch

bl_info = {
    "name":        "Code Autocomplete",
    "description": "Improve the scripting experience in Blenders text editor.",
    "author":      "Jacques Lucke",
    "version":     (1, 5, 0),
    "blender":     (2, 7, 4),
    "location":    "Text Editor",
    "category":    "Development"
    }

import bpy
from . import quick_operators
from . import ui
from . addon_development_manager import AddonDevelopmentSceneProperties
        
class AddonPreferences(bpy.types.AddonPreferences):
    bl_idname = "script_auto_complete"
    
    line_amount = bpy.props.IntProperty(default = 8, min = 1, max = 20, name = "Lines")
    
    def draw(self, context):
        layout = self.layout
        row = layout.row(align = False)
        row.prop(self, "line_amount")
        
               
    
# register
##################################

addon_keymaps = []
def register_keymaps():
    global addon_keymaps
    wm = bpy.context.window_manager
    km = wm.keyconfigs.addon.keymaps.new(name = "Text", space_type = "TEXT_EDITOR")
    kmi = km.keymap_items.new("script_auto_complete.select_whole_string", type = "Y", value = "PRESS", ctrl = True)
    kmi = km.keymap_items.new("script_auto_complete.switch_lines", type = "R", value = "PRESS", ctrl = True)
    addon_keymaps.append(km)
    
def unregister_keymaps():
    global addon_keymaps
    wm = bpy.context.window_manager
    for km in addon_keymaps:
        wm.keyconfigs.addon.keymaps.remove(km)
    addon_keymaps.clear()
    

def register():
    bpy.utils.register_module(__name__)
    
    register_keymaps()
    bpy.types.Scene.addon_development = bpy.props.PointerProperty(name = "Addon Development", type = AddonDevelopmentSceneProperties)

def unregister():
    unregister_keymaps()
    bpy.utils.unregister_module(__name__)
        
if __name__ == "__main__":
    register()
