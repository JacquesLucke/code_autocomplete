import bpy
from script_auto_complete.modal_handler import AutoCompletionManager
from script_auto_complete.text_editor_utils import *

class AutoCompleteSettingsPanel(bpy.types.Panel):
    bl_idname = "script_auto_complete.settings_panel"
    bl_label = "Auto Complete"
    bl_space_type = "TEXT_EDITOR"
    bl_region_type = "UI"
        
    def draw(self, context):
        layout = self.layout
        layout.operator("sript_autocomplete.start_auto_completion")
        

class StartAutoCompletion(bpy.types.Operator):
    bl_idname = "script_auto_complete.start_auto_completion"
    bl_label = "Start Auto Completion"
    
    def modal(self, context, event):
        event_used = False
        if active_text_block_exists():
            context.area.tag_redraw()
            event_used = self.modal_handler.update(event)
            
        if not event_used:
            if event.type in {'ESC'}:
                self.modal_handler.free()
                return { "FINISHED" }
            return { "PASS_THROUGH" }
        return { "RUNNING_MODAL" }

    def invoke(self, context, event):
        self.modal_handler = AutoCompletionManager()
        context.window_manager.modal_handler_add(self)
        return { "RUNNING_MODAL" }