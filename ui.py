import bpy
from script_auto_complete.modal_handler import AutoCompletionManager

class AutoCompleteSettingsPanel(bpy.types.Panel):
    bl_idname = "sript_autocomplete.settings_panel"
    bl_label = "Autocomplete"
    bl_space_type = "TEXT_EDITOR"
    bl_region_type = "UI"
        
    def draw(self, context):
        layout = self.layout
        layout.operator("sript_autocomplete.start_auto_completion")
        

class StartAutocompletion(bpy.types.Operator):
    bl_idname = "sript_autocomplete.start_auto_completion"
    bl_label = "Start Auto Completion"
    
    def modal(self, context, event):
        context.area.tag_redraw()
        self.modal_handler.update(event)

        if event.type in {'ESC'}:
            self.modal_handler.free()
            return { "FINISHED" }
        return { "PASS_THROUGH" }
        #return { "RUNNING_MODAL" }

    def invoke(self, context, event):
        self.modal_handler = AutoCompletionManager()
        context.window_manager.modal_handler_add(self)
        return { "RUNNING_MODAL" }