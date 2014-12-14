import bpy, re
from script_auto_complete.text_operators import *
from script_auto_complete.text_editor_utils import *

def get_insert_template_operators():
    operators = []
    text_before = get_text_before()
    for name, (before, text) in templates.items():
        if re.match(before, text_before) is not None:
            operators.append(InsertTextOperator(name, text))
    return operators
    
    
templates = {}

templates["New Panel"] = ("class \w*\(.*Panel\):", '''
    bl_idname = "name"
    bl_label = "label"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "category"
    
    def draw(self, context):
        layout = self.layout
        ''')
        
templates["New Operator"] = ("class \w*\(.*Operator\):", '''
    bl_idname = "my.operator"
    bl_label = "label"
    bl_description = ""
    
    @classmethod
    def poll(cls, context):
        return True
    
    def execute(self, context):
        return {"FINISHED"}
        ''')

templates["Register"] = ("def register\(\):", '''
    bpy.utils.register_module(__name__)

def unregister():
    bpy.utils.unregister_module(__name__)
    
if __name__ == "__main__":
    register()
    ''')
    
templates["Addon Info"] = ("bl_info.*=.*", ''' {
    "name": "My Addon Name",
    "description": "Single Line Explanation",
    "author": "Your Name",
    "version": (0, 0, 1),
    "blender": (2, 72, 0),
    "location": "View3D",
    "warning": "This is an unstable version",
    "wiki_url": "",
    "category": "Object" }
    ''')    
    
templates["License Header"] = "'''", """
Copyright (C) 2014 YOUR NAME
YOUR@MAIL.com

Created by YOUR NAME

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
"""    