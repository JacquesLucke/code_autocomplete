import bpy
import os
from collections import defaultdict
from bpy.props import *
from . utils import (get_settings,
                     get_current_addon_path,
                     current_addon_exists,
                     is_addon_name_valid,
                     get_directory_names,
                     get_file_names,
                     get_current_filepath,
                     get_addon_name)

class AddonDeveloperPanel(bpy.types.Panel):
    bl_idname = "addon_developer_panel"
    bl_label = "Addon Development"
    bl_space_type = "TEXT_EDITOR"
    bl_region_type = "UI"

    def draw(self, context):
        layout = self.layout
        setting = get_settings()
        row = layout.row(align = True)
        row.prop(setting, "addon_name", text = "Name")
        row.operator("code_autocomplete.find_existing_addon", icon = "EYEDROPPER", text = "")

        if not current_addon_exists():
            if not is_addon_name_valid():
                if get_addon_name() == "":
                    layout.label("Insert the name of your addon", icon = "INFO")
                else:
                    layout.operator("code_autocomplete.make_addon_name_valid", icon = "ERROR", text = "Correct Addon Name")
            else:
                row = layout.row()
                row.scale_y = 1.2
                row.operator_menu_enum("code_autocomplete.new_addon", "new_addon_type", icon = "NEW", text = "New Addon")
        else:
            row = layout.row()
            row.scale_y = 1.5
            row.operator("code_autocomplete.run_addon", icon = "OUTLINER_DATA_POSE", text = "Run Addon")
            layout.operator("code_autocomplete.export_addon", icon = "EXPORT", text = "Export as Zip")
        layout.operator("code_autocomplete.restart_blender", icon = "BLENDER")


directory_visibility = defaultdict(bool)

class AddonFilesPanel(bpy.types.Panel):
    bl_idname = "addon_files_panel"
    bl_label = "Addon Files"
    bl_space_type = "TEXT_EDITOR"
    bl_region_type = "UI"

    @classmethod
    def poll(cls, context):
        return current_addon_exists()

    def draw(self, context):
        layout = self.layout
        addon_path = get_current_addon_path()

        layout.operator("code_autocomplete.save_files", icon = "SAVE_COPY")
        self.draw_directory(layout, addon_path)

    def draw_directory(self, layout, directory):
        is_visible = self.is_directory_visible(directory)
        box = layout.box()

        row = box.row(align = True)

        icon = "DOWNARROW_HLT" if is_visible else "RIGHTARROW"
        props = row.operator("code_autocomplete.set_directory_visibility", text = os.path.split(directory[:-1])[-1], icon = icon, emboss = False)
        props.directory = directory
        props.visibility = not is_visible

        subrow = row.row(align = True)
        subrow.active = False
        props = subrow.operator("code_autocomplete.open_external_file_browser", text = "", icon = "FILESEL", emboss = False)
        props.directory = directory

        if is_visible:
            col = box.column(align = True)
            directory_names = get_directory_names(directory)
            for directory_name in directory_names:
                row = col.row()
                self.draw_directory(row, directory + directory_name + os.sep)

            file_names = get_file_names(directory)
            col = box.column(align = True)
            for file_name in file_names:
                row = col.row()
                row.alignment = "LEFT"
                full_path = directory + file_name
                props = row.operator("code_autocomplete.open_file_menu", icon = "COLLAPSEMENU", text = "", emboss = True)
                props.path = full_path
                if full_path == get_current_filepath():
                    row.label("", icon = "RIGHTARROW_THIN")
                operator = row.operator("code_autocomplete.open_file", text = file_name, emboss = False)
                operator.path = full_path

            row = box.row(align = True)
            operator = row.operator("code_autocomplete.new_file", icon = "PLUS", text = "File")
            operator.directory = directory
            operator = row.operator("code_autocomplete.new_directory", icon = "PLUS", text = "Directory")
            operator.directory = directory

    def is_directory_visible(self, directory):
        return directory_visibility[directory]

class SetDirectoryVisibility(bpy.types.Operator):
    bl_idname = "code_autocomplete.set_directory_visibility"
    bl_label = "Toogle Directory Visibility"
    bl_description = ""
    bl_options = {"REGISTER"}

    directory = StringProperty(name = "Directory", default = "")
    visibility = BoolProperty(name = "Visibility", default = True)

    def execute(self, context):
        global directory_visibility
        directory_visibility[self.directory] = self.visibility
        return {"FINISHED"}
