import bpy
from .. import settings
from . exception import BlockEvent
from . autocomplete_handler import AutocompleteHandler


class Autocomplete(bpy.types.Panel):
    bl_idname = "autocomplete"
    bl_label = "Autocomplete"
    bl_space_type = "TEXT_EDITOR"
    bl_region_type = "UI"
    
    def draw(self, context):
        layout = self.layout
        layout.operator("code_autocomplete.start_modal_operator")
        

class StartModalOperator(bpy.types.Operator):
    bl_idname = "code_autocomplete.start_modal_operator"
    bl_label = "Start Modal Operator"
    bl_description = ""
    bl_options = {"REGISTER"}
    
    def execute(self, context):
        bpy.ops.code_autocomplete.modal_operator("INVOKE_DEFAULT")
        return {"FINISHED"}


class ModalOperator(bpy.types.Operator):
    bl_idname = "code_autocomplete.modal_operator"
    bl_label = "Modal Operator"
    bl_description = ""
    bl_options = {"REGISTER"}
    
    @classmethod
    def poll(cls, context):
        return True
        
    def invoke(self, context, event):
        args = (self, context)
        self._handle = bpy.types.SpaceTextEditor.draw_handler_add(self.draw_callback_px, args, "WINDOW", "POST_PIXEL")
        context.window_manager.modal_handler_add(self)
        
        self.handlers = [AutocompleteHandler()]
        
        return {"RUNNING_MODAL"}
        
    def modal(self, context, event):
        for area in context.screen.areas:
            if area.type == "TEXT_EDITOR":
                area.tag_redraw()
        
        if event.type == "ESC":
            return self.finish()
            
        try:
            for handler in self.handlers:
                handler.update(event)
        except BlockEvent:
            if settings.debug: print("Event blocked: {} - {}".format(event.type, event.value))
            return {"RUNNING_MODAL"}
            
        return {"PASS_THROUGH"}
        
    def finish(self):
        bpy.types.SpaceTextEditor.draw_handler_remove(self._handle, "WINDOW")
        return {"FINISHED"}
    
    def draw_callback_px(tmp, self, context):
        for handler in self.handlers:
            handler.draw()