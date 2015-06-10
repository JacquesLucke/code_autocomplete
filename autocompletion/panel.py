import bpy
import jedi
import time
from .. text_block import TextBlock


class PrintCompletions(bpy.types.Operator):
    bl_idname = "code_autocomplete.print_completions"
    bl_label = "Print Completions"
    bl_description = ""
    
    def execute(self, context):
        text = TextBlock.get_active()
        if not text: { "FINISHED" }
        
        print(("#"*80+"\n")*2)
        
        source = text.text
        line = text.current_line_index + 1
        character = text.current_character_index
        
        start = time.clock()
        script = jedi.Script(source, line, character, text.filepath)
        completions = script.completions()
        print("Total Time: {}".format(time.clock() - start))
        print("Amount: {}".format(len(completions)))
        
        for i, c in enumerate(completions):
            print("{}".format(c.name))
            print("    Type: {}".format(c.type))
        
        return { "FINISHED" }

class CompletionsPanel(bpy.types.Panel):
    bl_idname = "completions_panel"
    bl_label = "Completions Panel"
    bl_space_type = "TEXT_EDITOR"
    bl_region_type = "UI"
    bl_category = "category"
    
    def draw(self, context):
        layout = self.layout
        layout.operator("code_autocomplete.print_completions")
        