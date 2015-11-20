import bpy
from .. settings import get_preferences
from .. text_block import TextBlock
from . exception import BlockEvent
from . autocomplete_handler import AutocompleteHandler
from . event_utils import is_event
from . active_text_area import ActiveTextArea

is_running = False
active_text_area = ActiveTextArea()

class Autocomplete(bpy.types.Panel):
    bl_idname = "autocomplete"
    bl_label = "Autocomplete"
    bl_space_type = "TEXT_EDITOR"
    bl_region_type = "UI"

    def draw(self, context):
        layout = self.layout
        if is_running:
            layout.operator("code_autocomplete.stop_modal_operator")
        else:
            layout.operator("code_autocomplete.start_modal_operator")
        layout.operator("code_autocomplete.regenerate_fake_bpy", "Build bpy Module")

        providers = get_preferences().completion_providers
        layout.prop(providers, "use_jedi_completion")
        layout.prop(providers, "use_word_completion")
        layout.prop(providers, "use_operator_completion")


class StartModalOperator(bpy.types.Operator):
    bl_idname = "code_autocomplete.start_modal_operator"
    bl_label = "Start Modal Operator"
    bl_description = ""
    bl_options = {"REGISTER"}

    def execute(self, context):
        bpy.ops.code_autocomplete.modal_text_operator("INVOKE_DEFAULT")
        active_text_area.set_area(context.area)
        global is_running
        is_running = True
        return {"FINISHED"}


class StopModalOperator(bpy.types.Operator):
    bl_idname = "code_autocomplete.stop_modal_operator"
    bl_label = "Stop Modal Operator"
    bl_description = ""
    bl_options = {"REGISTER"}

    def execute(self, context):
        global is_running
        is_running = False
        return {"FINISHED"}


class ModalTextOperator(bpy.types.Operator):
    bl_idname = "code_autocomplete.modal_text_operator"
    bl_label = "Modal Text Operator"
    bl_description = ""
    bl_options = {"REGISTER"}

    def invoke(self, context, event):
        args = (self, context)
        self._handle = bpy.types.SpaceTextEditor.draw_handler_add(self.draw_callback_px, args, "WINDOW", "POST_PIXEL")
        context.window_manager.modal_handler_add(self)
        self.handlers = [AutocompleteHandler()]
        return {"RUNNING_MODAL"}

    def modal(self, context, event):
        self.redraw_text_editors()
        active_text_area.update(event)

        if not is_running or event.type == "F8":
            return self.finish()

        return self.update_handlers(event)

    def redraw_text_editors(self):
        for area in bpy.context.screen.areas:
            if area.type == "TEXT_EDITOR":
                area.tag_redraw()

    def update_handlers(self, event):
        text_block = self.get_text_block()
        area = active_text_area.get()
        if not text_block: return {"PASS_THROUGH"}

        try:
            for handler in self.handlers:
                handler.update(event, text_block, area)
            return {"PASS_THROUGH"}
        except BlockEvent:
            if get_preferences().debug: print("Event blocked: {} - {}".format(event.type, event.value))
            return {"RUNNING_MODAL"}

    def finish(self):
        bpy.types.SpaceTextEditor.draw_handler_remove(self._handle, "WINDOW")
        if get_preferences().debug: print("Finished modal text operator")
        return {"FINISHED"}

    def draw_callback_px(tmp, self, context):
        if context.area == active_text_area.get():
            text_block = self.get_text_block()
            if not text_block: return

            for handler in self.handlers:
                handler.draw(text_block)

    def get_text_block(self):
        text = active_text_area.get_text()
        area = active_text_area.get()
        if text:
            text_block = TextBlock(text)
            text_block.set_context(area = area, space = area.spaces[0])
            return text_block
