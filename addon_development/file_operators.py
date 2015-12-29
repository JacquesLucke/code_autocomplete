import bpy
import os
from bpy.props import *
from . utils import (get_directory_names,
                     current_addon_exists,
                     is_addon_name_valid,
                     get_current_addon_path,
                     get_addon_name,
                     correct_file_name,
                     get_settings,
                     addons_path,
                     new_file,
                     new_directory)

class NewFile(bpy.types.Operator):
    bl_idname = "code_autocomplete.new_file"
    bl_label = "New File"
    bl_description = "Create a new file in this directory"
    bl_options = {"REGISTER"}

    directory = StringProperty(name = "Directory", default = "")
    name = StringProperty(name = "File Name", default = "")
    content = StringProperty(name = "Content", default = "")

    @classmethod
    def poll(cls, context):
        return current_addon_exists()

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width = 400)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "name")

    def execute(self, context):
        if self.name != "":
            path = self.directory + self.name
            new_file(self.directory + self.name, self.content)
            bpy.ops.code_autocomplete.open_file(path = path)
            context.area.tag_redraw()
        return {"FINISHED"}


class NewDirectory(bpy.types.Operator):
    bl_idname = "code_autocomplete.new_directory"
    bl_label = "New Directory"
    bl_description = "Create a new subdirectory"
    bl_options = {"REGISTER"}

    directory = StringProperty(name = "Directory", default = "")
    name = StringProperty(name = "Directory Name", default = "")

    @classmethod
    def poll(cls, context):
        return current_addon_exists()

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width = 400)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "name")

    def execute(self, context):
        if self.name != "":
            new_directory(self.directory + self.name)
            new_file(os.path.join(self.directory + self.name, "__init__.py"))
            context.area.tag_redraw()
        return {"FINISHED"}


class FileMenuOpener(bpy.types.Operator):
    bl_idname = "code_autocomplete.open_file_menu"
    bl_label = "Open File Menu"

    path = StringProperty(name = "Path", default = "")

    def invoke(self, context, event):
        context.window_manager.popup_menu(self.drawMenu, title = "{} - File Menu".format(os.path.basename(self.path)))
        return {"FINISHED"}

    def drawMenu(fileProps, self, context):
        layout = self.layout
        layout.operator_context = "INVOKE_DEFAULT"

        props = layout.operator("code_autocomplete.rename_file", text = "Rename")
        props.path = fileProps.path

        props = layout.operator("code_autocomplete.open_file", text = "Open in Text Editor")
        props.path = fileProps.path

        props = layout.operator("code_autocomplete.open_external_file_browser", text = "Open External")
        props.directory = os.path.dirname(fileProps.path)

        layout.separator()

        props = layout.operator("code_autocomplete.delete_file", text = "Delete", icon = "ERROR")
        props.path = fileProps.path


class OpenFile(bpy.types.Operator):
    bl_idname = "code_autocomplete.open_file"
    bl_label = "Open File"
    bl_description = "Load the file into the text editor"
    bl_options = {"REGISTER"}

    path = StringProperty(name = "Path", default = "")

    def execute(self, context):
        text = None
        for text_block in bpy.data.texts:
            if text_block.filepath == self.path:
                text = text_block
                break
        if not text:
            text = bpy.data.texts.load(self.path, internal = False)

        context.space_data.text = text
        return {"FINISHED"}


class OpenExternalFileBrowser(bpy.types.Operator):
    bl_idname = "code_autocomplete.open_external_file_browser"
    bl_label = "Open External File Browser"
    bl_description = ""
    bl_options = {"REGISTER"}

    directory = StringProperty(name = "Directory", default = "")

    def execute(self, context):
        bpy.ops.wm.path_open(filepath = self.directory)
        return {"FINISHED"}


class RenameFile(bpy.types.Operator):
    bl_idname = "code_autocomplete.rename_file"
    bl_label = "Open External File Browser"
    bl_description = ""
    bl_options = {"REGISTER"}

    path = StringProperty(name = "Directory", default = "")
    new_name = StringProperty(name = "Directory", description = "New file name", default = "")

    def invoke(self, context, event):
        self.new_name = os.path.basename(self.path)
        return context.window_manager.invoke_props_dialog(self, width = 400)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "new_name")

    def execute(self, context):
        new_path = os.path.join(os.path.dirname(self.path), self.new_name)
        os.rename(self.path, new_path)
        self.correct_text_block_paths(self.path, new_path)
        context.area.tag_redraw()
        return {"FINISHED"}

    def correct_text_block_paths(self, old_path, new_path):
        for text in bpy.data.texts:
            if text.filepath == old_path:
                text.filepath = new_path


class DeleteFile(bpy.types.Operator):
    bl_idname = "code_autocomplete.delete_file"
    bl_label = "Delete File"
    bl_description = "Delete file on the hard drive"
    bl_options = {"REGISTER"}

    path = StringProperty(name = "Directory", default = "")

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):
        os.remove(self.path)
        context.area.tag_redraw()
        return {"FINISHED"}


class SaveFiles(bpy.types.Operator):
    bl_idname = "code_autocomplete.save_files"
    bl_label = "Save All Files"
    bl_description = "Save all files which correspond to a file on the hard drive"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        for text in bpy.data.texts:
            save_text_block(text)
        try: bpy.ops.text.resolve_conflict(resolution = "IGNORE")
        except: pass
        return {"FINISHED"}


def save_text_block(text_block):
    if not text_block: return
    if not os.path.exists(text_block.filepath): return

    file = open(text_block.filepath, mode = "w")
    file.write(text_block.as_string())
    file.close()
