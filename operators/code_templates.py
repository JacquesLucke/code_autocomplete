def get_templates():
    return templates
    
    
    
templates = {}

templates["New Panel"] = ("Panel):", '''
    bl_idname = "name"
    bl_label = "label"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "category"
    
    def draw(self, context):
        layout = self.layout
        ''')
        
templates["New Operator"] = ("Operator):", '''
    bl_idname = "my.operator"
    bl_label = "label"
    bl_description = ""
    
    @classmethod
    def poll(cls, context):
        return True
    
    def execute(self, context):
        return {"FINISHED"}
        ''')

templates["Register"] = ("register():", '''
    bpy.utils.register_module(__name__)

def unregister():
    bpy.utils.unregister_module(__name__)
    
if __name__ == "__main__":
    register()
    ''')
    
templates["Addon Info"] = ("bl_info =", ''' {
    "name": "My Addon Name",
    "description": "Single Line Explanation",
    "author": "Your Name",
    "version": (0, 0, 1),
    "blender": (2, 72, 0),
    "location": "View3D",
    "warning": "This is an unstable version",
    "wiki_url": "",
    "category": "Object" }
    ''')