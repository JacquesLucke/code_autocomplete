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



bl_info = {
    "name":        "Code Autocomplete",
    "description": "Improve the scripting experience in Blenders text editor.",
    "author":      "Jacques Lucke",
    "version":     (1, 5, 1),
    "blender":     (2, 7, 4),
    "location":    "Text Editor",
    "category":    "Development"
    }
    
    
    
# load and reload submodules
##################################    
    
from . import developer_utils
modules = developer_utils.setup_addon_modules(__path__, __name__, "bpy" in locals())



# properties
################################## 

import bpy
        
class AddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__
    
    line_amount = bpy.props.IntProperty(default = 8, min = 1, max = 20, name = "Lines", description = "Amount of lines shown in the context box")
    
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
    kmi = km.keymap_items.new("code_autocomplete.select_whole_string", type = "Y", value = "PRESS", ctrl = True)
    kmi = km.keymap_items.new("code_autocomplete.switch_lines", type = "R", value = "PRESS", ctrl = True)
    kmi = km.keymap_items.new("wm.call_menu", type = "SPACE", value = "PRESS", ctrl = True)
    kmi.properties.name = "code_autocomplete.insert_template_menu"
    kmi = km.keymap_items.new("wm.call_menu", type = "TAB", value = "PRESS", ctrl = True)
    kmi.properties.name = "code_autocomplete.select_text_block"
    addon_keymaps.append(km)
    
def unregister_keymaps():
    wm = bpy.context.window_manager
    for km in addon_keymaps:
        for kmi in km.keymap_items:
            km.keymap_items.remove(kmi)
        wm.keyconfigs.addon.keymaps.remove(km)
    addon_keymaps.clear()
 
from . addon_development_manager import AddonDevelopmentSceneProperties 
from . quick_operators import register_menus, unregister_menus
    
def register():
    bpy.utils.register_module(__name__)
    register_keymaps()
    register_menus()
    bpy.types.Scene.addon_development = bpy.props.PointerProperty(name = "Addon Development", type = AddonDevelopmentSceneProperties)
    
    print("Registered Code Autocomplete with {} modules.".format(len(modules)))

def unregister():
    bpy.utils.unregister_module(__name__)
    unregister_keymaps()
    unregister_menus()
    
    print("Unregistered Code Autocomplete")
