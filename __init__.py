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
    "version":     (1,0, 0),
    "blender":     (2, 7, 4),
    "location":    "Text Editor",
    "category":    "Development"
    }
    
# import all modules in same/subdirectories
###########################################
currentPath = os.path.dirname(__file__)
module_name = "script_auto_complete"
sys.modules[module_name] = sys.modules[__name__]

def getAllImportFiles():
    def get_path(base):
        b, t = os.path.split(base)
        if __name__ == t:
            return [module_name]
        else:
            return get_path(b) + [t]

    for root, dirs, files in os.walk(currentPath):
        path = ".".join(get_path(root))
        for f in filter(lambda f:f.endswith(".py"), files):
            name = f[:-3]
            if not name == "__init__":
                yield path + "." + name

auto_complete_modules = []

for name in getAllImportFiles():
    mod = importlib.import_module(name)
    auto_complete_modules.append(mod)

reload_event = "bpy" in locals()

import bpy

#  Reload
#  makes F8 reload actually reload the code

if reload_event:
    for module in auto_complete_modules:
        importlib.reload(module)
        
        
class AddonPreferences(bpy.types.AddonPreferences):
    bl_idname = module_name
    
    line_amount = bpy.props.IntProperty(default = 8, min = 1, max = 20, name = "Lines")
    
    def draw(self, context):
        layout = self.layout
        row = layout.row(align = False)
        row.prop(self, "line_amount")
               
    
# register
##################################

def register():
    try: bpy.utils.register_module(module_name)
    except: pass
    print("Loaded Script Auto Completion with {} modules".format(len(auto_complete_modules)))

def unregister():
    try: bpy.utils.unregister_module(module_name)
    except: pass
        
if __name__ == "__main__":
    register()
