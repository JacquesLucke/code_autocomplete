import bpy
from bpy.props import *
from . name_utils import *
from . text_block import TextBlock

class InsertTemplateMenu(bpy.types.Menu):
    bl_idname = "text_editor.insert_template_menu"
    bl_label = "Insert Template"
    
    def draw(self, context):
        layout = self.layout
        layout.operator_context = "INVOKE_DEFAULT"
        layout.operator("code_autocomplete.insert_panel", text = "New Panel")
        layout.operator_menu_enum("code_autocomplete.insert_menu", "menu_type", text = "Menu")
        

class InsertTemplateBase:
    bl_options = {"REGISTER"}
    
    class_name = StringProperty(name = "Class Name", default = "")
    
    @classmethod
    def poll(cls, context):
        return TextBlock.get_active()
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, 300, 200)
    
    def draw(self, context):
        layout = self.layout
        layout.prop(self, "class_name", text = "Name")
        
        

class InsertPanel(bpy.types.Operator, InsertTemplateBase):
    bl_idname = "code_autocomplete.insert_panel"
    bl_label = "Insert Panel"
    bl_description = ""
    
    def execute(self, context):
        changes = {
            "CLASS_NAME" : get_valid_variable_name(self.class_name),
            "ID_NAME" : get_lower_case_with_underscores(self.class_name),
            "LABEL" : get_separated_capitalized_words(self.class_name) }
        insert_template(panel_template, changes)
        return {"FINISHED"}  
        

menu_type_items = [
    ("NORMAL", "Normal", ""),
    ("PIE", "Pie", "") ]        
class InsertMenu(bpy.types.Operator, InsertTemplateBase):
    bl_idname = "code_autocomplete.insert_menu"
    bl_label = "Insert Menu"
    bl_description = ""
    
    menu_type = EnumProperty(items = menu_type_items, default = "NORMAL")
    
    def execute(self, context):
        if self.menu_type == "NORMAL": code = menu_template
        if self.menu_type == "PIE": code = pie_menu_template
        changes = {
            "CLASS_NAME" : get_valid_variable_name(self.class_name),
            "ID_NAME" : "view3d." + get_lower_case_with_underscores(self.class_name),
            "LABEL" : get_separated_capitalized_words(self.class_name) }
        insert_template(code, changes)
        return {"FINISHED"} 
        
        
        
def insert_template(code, changes = {}):
    for old, new in changes.items():
        code = code.replace(old, new)
    text_block = TextBlock.get_active()
    if text_block:
        text_block.insert(code)
        
        
        
panel_template = '''class CLASS_NAME(bpy.types.Panel):
    bl_idname = "ID_NAME"
    bl_label = "LABEL"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "category"
    
    def draw(self, context):
        layout = self.layout
        '''         
        

menu_template = '''class CLASS_NAME(bpy.types.Menu):
    bl_idname = "ID_NAME"
    bl_label = "LABEL"
    
    def draw(self, context):
        layout = self.layout
        '''   

pie_menu_template = '''class CLASS_NAME(bpy.types.Menu):
    bl_idname = "ID_NAME"
    bl_label = "LABEL"
    
    def draw(self, context):
        pie = self.layout.menu_pie()
        '''       