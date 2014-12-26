import re
from script_auto_complete.text_operators import InsertTextOperator

def get_insert_template_operators(text_block):
    operators = []
    text_before = text_block.text_before_cursor
    for name, pattern, snippet in templates:
        if re.match(pattern, text_before) is not None:
            operators.append(InsertTextOperator(name, snippet))
    return operators
    
    
templates = []

templates.append(("New Panel", "class \w*\(.*Panel\):", '''
    bl_idname = "name"
    bl_label = "label"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "category"
    
    def draw(self, context):
        layout = self.layout
        '''))
        
templates.append(("New Operator", "class \w*\(.*Operator\):", '''
    bl_idname = "my.operator"
    bl_label = "label"
    bl_description = ""
    bl_options = {"REGISTER"}
    
    @classmethod
    def poll(cls, context):
        return True
    
    def execute(self, context):
        return {"FINISHED"}
        '''))
        
templates.append(("New Modal Operator", "class \w*\(.*Operator\):", '''
    bl_idname = "my.modal_operator"
    bl_label = "label"
    bl_description = ""
    bl_options = {"REGISTER"}
    
    @classmethod
    def poll(cls, context):
        return True
        
    def modal(self, context, event):
    
        if event.type == "LEFTMOUSE":
            return {"FINISHED"}
    
        if event.type in {"RIGHTMOUSE", "ESC"}:
            return {"CANCELLED"}
            
        return {"RUNNING_MODAL"}
    
    def invoke(self, context, event):
        context.window_manager.modal_handler_add(self)
        return {"RUNNING_MODAL"}
        '''))

templates.append(("New Modal Operator Draw", "class \w*\(.*Operator\):", '''
    bl_idname = "my.modal_operator"
    bl_label = "label"
    bl_description = ""
    bl_options = {"REGISTER"}
    
    @classmethod
    def poll(cls, context):
        return True
        
    def modal(self, context, event):
        context.area.tag_redraw()
        
        if event.type == "LEFTMOUSE":
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, "WINDOW")
            return {"FINISHED"}
            
        if event.type in {"RIGHTMOUSE", "ESC"}:
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, "WINDOW")
            return {"CANCELLED"}
            
        return {"RUNNING_MODAL"}
    
    def invoke(self, context, event):
        args = (self, context)
        self._handle = bpy.types.SpaceView3D.draw_handler_add(draw_callback_px, args, "WINDOW", "POST_PIXEL")
        context.window_manager.modal_handler_add(self)
        return {"RUNNING_MODAL"}
        
def draw_callback_px(self, context):
    pass
    '''))          
        
templates.append(("New Menu", "class \w*\(.*Menu\):", '''
    bl_idname = "view3D.custom_menu"
    bl_label = "Custom Menu"
    
    def draw(self, context):
        layout = self.layout
        '''))
        
templates.append(("New Pie Menu", "class \w*\(.*Menu\):", '''
    bl_idname = "view3D.custom_menu"
    bl_label = "Custom Menu"
    
    def draw(self, context):
        pie = self.layout.menu_pie()
        '''))        

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
    "blender": (2, 72, 0),
    "location": "View3D",
    "warning": "This is an unstable version",
    "wiki_url": "",
    "category": "Object" }
    '''))    
    
templates.append(("License Header", "'''", """
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
"""))