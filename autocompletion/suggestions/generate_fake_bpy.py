import bpy
import os
import sys
import shutil

fake_package_name = "_bpy_fake"
top_directory = os.path.join(os.path.dirname(__file__), "dynamic")
directory = os.path.join(top_directory, fake_package_name)
private_path = os.path.join(directory, "__private__")

sys.path.append(top_directory) 

class GenerateFakeBPY(bpy.types.Operator):
    bl_idname = "code_autocomplete.generate_fake_bpy"
    bl_label = "Generate Fake BPY"
    bl_description = ""
    bl_options = {"REGISTER"}
    
    def execute(self, context):
        regenerate_fake_bpy()
        return {"FINISHED"}
        
def regenerate_fake_bpy():
    remove_old_fake()
    generate_fake_bpy()
        
def remove_old_fake():
    if os.path.exists(directory):
        shutil.rmtree(directory, ignore_errors = True)
        
def generate_fake_bpy():
    os.makedirs(directory)
    create_init()
    create_private_subdirectory()
    
def create_init():
    path = os.path.join(directory, "__init__.py")
    file = open(path, "w+")
    file.write(init_content)
    file.close()    
    
init_content = '''
from . __private__.context import Context as context
data = "Test"
'''    

def create_private_subdirectory():
    os.makedirs(private_path)
    open(os.path.join(private_path, "__init__.py"), "a").close()
    create_context_file()
    
def create_context_file():
    path = os.path.join(private_path, "context.py")
    file = open(path, "w+")
    file.write(context_content)
    file.close()
    
context_content = '''
class Context:
    area = Area()
    blend_data = BlendData()
    mode = "EDIT_MESH"
    region = Region()
    region_data = RegionView3D()
    scene = Scene()
    screen = Screen()
    space_data = Space()
    tool_settings = ToolSettings()
    user_preferences = UserPreferences()
    window = Window()
    window_manager = WindowManager()
'''    