import bpy
from script_auto_complete.modal_handler import ModalHandler
from script_auto_complete.text_editor_utils import *
from script_auto_complete.documentation import get_documentation

class AutoCompleteSettingsPanel(bpy.types.Panel):
    bl_idname = "script_auto_complete.settings_panel"
    bl_label = "Auto Complete"
    bl_space_type = "TEXT_EDITOR"
    bl_region_type = "UI"
        
    def draw(self, context):
        layout = self.layout
        layout.operator("script_auto_complete.start_auto_completion")
        if get_documentation().is_build:
            layout.operator("script_auto_complete.rebuild_documentation")
        

class StartAutoCompletion(bpy.types.Operator):
    bl_idname = "script_auto_complete.start_auto_completion"
    bl_label = "Start Auto Completion"
    
    def modal(self, context, event):
        block_event = False
        if active_text_block_exists():
            context.area.tag_redraw()
            block_event = self.modal_handler.update(event)
            
        if not block_event:
            if event.type in {'ESC'}:
                self.modal_handler.free()
                return { "FINISHED" }
            return { "PASS_THROUGH" }
        return { "RUNNING_MODAL" }

    def invoke(self, context, event):
        get_documentation().build_if_necessary()
        self.modal_handler = ModalHandler()
        context.window_manager.modal_handler_add(self)
        return { "RUNNING_MODAL" }
        
        
class RebuildDocumentation(bpy.types.Operator):
    bl_idname = "script_auto_complete.rebuild_documentation"
    bl_label = "Rebuild Documentation"
    
    @classmethod
    def poll(cls, context):
        return get_documentation().is_build
    
    def execute(self, context):
        get_documentation().build()
        return { "FINISHED" }
        
