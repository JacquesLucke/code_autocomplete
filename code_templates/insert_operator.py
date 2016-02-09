import bpy
from bpy.props import *
from . base import InsertClassTemplateBase, insert_template
from .. utils.variable_name_conversion import (get_valid_variable_name,
                                               get_lower_case_with_underscores,
                                               get_separated_capitalized_words)

operator_type_items = [
    ("NORMAL", "Normal", ""),
    ("MODAL", "Modal", ""),
    ("MODAL_DRAW", "Modal Draw", "") ]

class InsertOperator(bpy.types.Operator, InsertClassTemplateBase):
    bl_idname = "code_autocomplete.insert_operator"
    bl_label = "Insert Operator"
    bl_description = ""

    operator_type = EnumProperty(items = operator_type_items, default = "NORMAL")

    def execute(self, context):
        if self.operator_type == "NORMAL": code = operator_template
        if self.operator_type == "MODAL": code = modal_operator_template
        if self.operator_type == "MODAL_DRAW": code = modal_operator_draw_template
        changes = {
            "CLASS_NAME" : get_valid_variable_name(self.class_name),
            "ID_NAME" : "my_operator." + get_lower_case_with_underscores(self.class_name),
            "LABEL" : get_separated_capitalized_words(self.class_name) }
        insert_template(code, changes)
        return {"FINISHED"}

operator_template = '''class CLASS_NAME(bpy.types.Operator):
    bl_idname = "ID_NAME"
    bl_label = "LABEL"
    bl_description = ""
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        return {"FINISHED"}
        '''

modal_operator_template = '''class CLASS_NAME(bpy.types.Operator):
    bl_idname = "ID_NAME"
    bl_label = "LABEL"
    bl_description = ""
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return True

    def invoke(self, context, event):
        context.window_manager.modal_handler_add(self)
        return {"RUNNING_MODAL"}

    def modal(self, context, event):

        if event.type == "LEFTMOUSE":
            return {"FINISHED"}

        if event.type in {"RIGHTMOUSE", "ESC"}:
            return {"CANCELLED"}

        return {"RUNNING_MODAL"}
        '''

modal_operator_draw_template = '''class CLASS_NAME(bpy.types.Operator):
    bl_idname = "ID_NAME"
    bl_label = "LABEL"
    bl_description = ""
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return True

    def invoke(self, context, event):
        args = ()
        self.draw_handler = bpy.types.SpaceView3D.draw_handler_add(self.draw_callback_px, args, "WINDOW", "POST_PIXEL")
        context.window_manager.modal_handler_add(self)
        return {"RUNNING_MODAL"}

    def modal(self, context, event):
        context.area.tag_redraw()

        if event.type == "LEFTMOUSE":
            return self.finish()

        if event.type in {"RIGHTMOUSE", "ESC"}:
            return self.finish()

        return {"RUNNING_MODAL"}

    def finish(self):
        bpy.types.SpaceView3D.draw_handler_remove(self.draw_handler, "WINDOW")
        return {"FINISHED"}

    def draw_callback_px(self):
        pass
    '''
