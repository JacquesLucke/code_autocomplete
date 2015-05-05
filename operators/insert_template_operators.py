import re
from .. text_operators import InsertTextOperator

def get_insert_template_operators(text_block):
    operators = []
    text_before = text_block.text_before_cursor
    for name, pattern, snippet in templates:
        if re.match(pattern, text_before) is not None:
            operators.append(InsertTextOperator(name, snippet))
    return operators
    
    
templates = []   

templates.append(("Register", "def register\(\):", '''
    bpy.utils.register_module(__name__)

def unregister():
    bpy.utils.unregister_module(__name__)
    
if __name__ == "__main__":
    register()
    '''))
    
templates.append(("Addon Info", "bl_info.*=.*", ''' {
    "name": "My Addon Name",
    "description": "Single Line Explanation",
    "author": "Your Name",
    "version": (0, 0, 1),
    "blender": (2, 74, 0),
    "location": "View3D",
    "warning": "This addon is still in development.",
    "wiki_url": "",
    "category": "Object" }
    '''))    
    
templates.append(("License Header", "'''", """
Copyright (C) 2015 YOUR NAME
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
"""))

templates.append(("Invoke Function", "\s*def invoke\(", """self, context, event):
        
        return {"FINISHED"}"""))
        
templates.append(("Modal Function", "\s*def modal\(", """self, context, event):
        
        return {"RUNNING_MODAL"}"""))        