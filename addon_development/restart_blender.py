import os
import bpy
import sys
from bpy.app.handlers import persistent
from . utils import get_addon_name, get_settings
from . panels import directory_visibility

class RestartBlender(bpy.types.Operator):
    bl_idname = "code_autocomplete.restart_blender"
    bl_label = "Restart Blender"
    bl_description = "Close and open a new Blender instance to test the Addon on the startup file. (Currently only supported for windows)"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return sys.platform == "win32"

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):
        bpy.ops.code_autocomplete.save_files()
        save_status()
        start_another_blender_instance()
        bpy.ops.wm.quit_blender()
        return {"FINISHED"}


# Save current settings to reload them in the new instance
##########################################################

restart_data_path = os.path.join(os.path.dirname(__file__), "restart_data.txt")

id_addon_name = "ADDON_NAME: "
id_current_path = "CURRENT_PATH: "
id_visiblie_path = "VISIBLE_PATH: "

def save_status():
    file = open(restart_data_path, "w")
    file.write(id_addon_name + get_addon_name() + "\n")
    text_block = bpy.context.space_data.text
    if text_block:
        file.write(id_current_path + text_block.filepath + "\n")
    for path, is_open in directory_visibility.items():
        if is_open:
            file.write(id_visiblie_path + path + "\n")

    file.close()

@persistent
def open_status(scene):
    if os.path.exists(restart_data_path):
        file = open(restart_data_path)
        lines = file.readlines()
        file.close()
        os.remove(restart_data_path)
        parse_startup_file_lines(lines)

bpy.app.handlers.load_post.append(open_status)

def parse_startup_file_lines(lines):
    for line in lines:
        if line.startswith(id_addon_name):
            get_settings().addon_name = line[len(id_addon_name):].strip()
        if line.startswith(id_current_path):
            path = line[len(id_current_path):].strip()
            if os.path.exists(path):
                text_block = bpy.data.texts.load(path, internal = False)
                for screen in bpy.data.screens:
                    for area in screen.areas:
                        for space in area.spaces:
                            if space.type == "TEXT_EDITOR":
                                space.text = text_block
        if line.startswith(id_visiblie_path):
            path = line[len(id_visiblie_path):].strip()
            bpy.ops.code_autocomplete.set_directory_visibility(directory = path, visibility = True)



# Restart Blender
##########################

def start_another_blender_instance():
    open_file(bpy.app.binary_path)

# only works for windows currently
def open_file(path):
    if sys.platform == "win32":
        os.startfile(path)
    else:
        opener = "open" if sys.platform == "darwin" else "xdg-open"
        subprocess.call([opener, path])
