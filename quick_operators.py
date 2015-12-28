import bpy
import os
import re
from bpy.props import *
from . text_block import TextBlock

class SolveWhitespaceInconsistency(bpy.types.Operator):
    bl_idname = "code_autocomplete.correct_whitespaces"
    bl_label = "Correct Whitespaces"
    bl_description = "Convert whitespaces to spaces or tabs depending on what is set for this text block"

    def execute(self, context):
        if context.edit_text.use_tabs_as_spaces:
            bpy.ops.text.convert_whitespace(type = "SPACES")
        else:
            bpy.ops.text.convert_whitespace(type = "TABS")
        return { "FINISHED" }

class SelectWholeString(bpy.types.Operator):
    bl_idname = "code_autocomplete.select_whole_string"
    bl_label = "Select Whole String"
    bl_description = ""
    bl_options = {"REGISTER"}

    def execute(self, context):
        text_block = TextBlock.get_active()
        if not text_block: return {"CANCELLED"}

        line_text = text_block.current_line
        character_index = text_block.current_character_index

        string_letter = text_block.get_string_definition_type(line_text, character_index)
        if string_letter is None: return {"CANCELLED"}
        start, end = text_block.get_range_surrounded_by_letter(line_text, string_letter, character_index)
        if start != end:
            text_block.set_selection_in_line(start, end)

        return {"FINISHED"}


class ConvertFileIndentation(bpy.types.Operator):
    bl_idname = "code_autocomplete.convert_file_indentation"
    bl_label = "Convert File Indentation"
    bl_description = ""
    bl_options = {"REGISTER"}

    path = StringProperty()
    old_indentation = StringProperty(default = "\t")
    new_indentation = StringProperty(default = "    ")

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        if not os.path.exists(self.path): return {"CANCELLED"}

        old = self.old_indentation
        new = self.new_indentation

        file = open(self.path, "r")
        lines = file.readlines()
        file.close()

        new_lines = []
        for line in lines:
            new_line = ""
            while line.startswith(old):
                new_line += new
                line = line[len(old):]
            new_line += line.rstrip()
            new_lines.append(new_line)

        file = open(self.path, "w")
        file.write("\n".join(new_lines))
        file.close()
        return {"FINISHED"}


class SelectTextBlockMenu(bpy.types.Menu):
    bl_idname = "code_autocomplete_select_text_block"
    bl_label = "Select Text Block"

    def draw(self, context):
        layout = self.layout

        if len(bpy.data.texts) == 0:
            layout.label("There are no texts in this file", icon = "INFO")
        else:
            for text in bpy.data.texts:
                operator = layout.operator("code_autocomplete.open_text_block", text = text.name)
                operator.name = text.name

class OpenTextBlock(bpy.types.Operator):
    bl_idname = "code_autocomplete.open_text_block"
    bl_label = "Open Text Block"
    bl_description = ""
    bl_options = {"REGISTER"}

    name = StringProperty()

    @classmethod
    def poll(cls, context):
        return hasattr(context.space_data, "text")

    def execute(self, context):
        context.space_data.text = bpy.data.texts[self.name]
        return {"FINISHED"}


def right_click_menu_extension(self, context):
    layout = self.layout
    layout.separator()
    layout.operator("text.comment")
    layout.operator("text.uncomment")

    text_block = TextBlock.get_active()
    if text_block:
        line = text_block.current_line
        match = re.match("def (\w+)\(\):", line)
        if match:
            function_name = match.group(1)
            operator = layout.operator("code_autocomplete.execute_function")
            operator.filepath = text_block.filepath
            operator.function_name = function_name


def format_menu_extension(self, context):
    text_block = TextBlock.get_active()
    if text_block:
        layout = self.layout
        layout.operator("code_autocomplete.build_script")
        layout.operator("code_autocomplete.correct_whitespaces")
        props = layout.operator("code_autocomplete.convert_addon_indentation")
        if text_block.use_tabs_as_spaces:
            props.old_indentation = "\t"
            props.new_indentation = "    "
        else:
            props.old_indentation = "    "
            props.new_indentation = "\t"



def register_menus():
    bpy.types.TEXT_MT_toolbox.append(right_click_menu_extension)
    bpy.types.TEXT_MT_format.append(format_menu_extension)

def unregister_menus():
    bpy.types.TEXT_MT_toolbox.remove(right_click_menu_extension)
    bpy.types.TEXT_MT_format.remove(format_menu_extension)
