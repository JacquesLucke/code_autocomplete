import bpy
import jedi
import time
from .. text_block import TextBlock

class CompletionsPanel(bpy.types.Panel):
    bl_idname = "completions_panel"
    bl_label = "Completions Panel"
    bl_space_type = "TEXT_EDITOR"
    bl_region_type = "UI"
    bl_category = "category"
    
    def draw(self, context):
        layout = self.layout
        
        text = TextBlock.get_active()
        if not text: return
        
        word = text.current_word
        if len(word) == 0 and not "import" in text.current_line and not text.current_line.endswith("."): return
        
        start = time.clock()
    
        source = text.text
        line = text.current_line_index + 1
        character = text.current_character_index
        
        script = jedi.Script(source, line, character)
        completions = script.completions()
        
        end = time.clock()
        layout.label(str(end-start))
        layout.label(str(len(completions)))
        
        for i, c in enumerate(completions):
            if i > 20: break
            col = layout.column(align = True)
            col.label(c.name)