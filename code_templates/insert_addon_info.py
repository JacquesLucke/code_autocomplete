import bpy
from . base import InsertTemplateBase, insert_template

class InsertAddonInfo(bpy.types.Operator, InsertTemplateBase):
    bl_idname = "code_autocomplete.insert_addon_info"
    bl_label = "Insert Addon Info"
    bl_description = ""

    def execute(self, context):
        changes = { "BLENDER_VERSION" : str(bpy.app.version) }
        insert_template(addon_info_template, changes)
        return {"FINISHED"}

addon_info_template = '''bl_info = {
    "name": "My Addon Name",
    "description": "",
    "author": "Your Name",
    "version": (0, 0, 1),
    "blender": BLENDER_VERSION,
    "location": "View3D",
    "warning": "This addon is still in development.",
    "wiki_url": "",
    "category": "Object" }
    '''
