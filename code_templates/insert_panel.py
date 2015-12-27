import bpy
from . base import InsertClassTemplateBase, insert_template
from .. utils.variable_name_conversion import (get_valid_variable_name,
                                               get_lower_case_with_underscores,
                                               get_separated_capitalized_words)

class InsertPanel(bpy.types.Operator, InsertClassTemplateBase):
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

panel_template = '''class CLASS_NAME(bpy.types.Panel):
    bl_idname = "ID_NAME"
    bl_label = "LABEL"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "category"

    def draw(self, context):
        layout = self.layout
        '''
