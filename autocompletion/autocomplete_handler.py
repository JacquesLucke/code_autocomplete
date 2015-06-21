import bpy
from .. graphics.rectangle import Rectangle
from . exception import BlockEvent
from . event_utils import is_event
from . suggestions import complete
import time

completions = []

class AutocompleteHandler:
    def __init__(self):
        pass
        
    def update(self, event, text_block):
        global completions
        text = text_block.text_before_cursor
        
        if event.value == "RELEASE" and event.type not in ("MOUSEMOVE", "INBETWEEN_MOUSEMOVE"):
            changed = False
            if len(text) > 0:
                c = text[-1]
                if c.isalpha() or c in "._" or text.endswith("import "):
                    start = time.clock()
                    completions = complete(text_block)
                    end = time.clock()
                    print("Time: {}\t\tCode: {}".format(end - start, text))
                    changed = True
                    
            if not changed:
                completions = []
        
    def draw(self, text_block):
        Rectangle(20, 50, 400, 100).draw()
        
        
class Autocomplete(bpy.types.Panel):
    bl_idname = "test"
    bl_label = "Completions"
    bl_space_type = "TEXT_EDITOR"
    bl_region_type = "UI"
    
    def draw(self, context):
        layout = self.layout
        global completions
        for i, c in enumerate(completions):
            if i > 10: break
            layout.label(c.name)
    
    

        