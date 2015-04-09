import bpy 
import os
import zipfile
from bpy.props import *
from os import listdir
from os.path import isfile, isdir, join, dirname
from collections import defaultdict

is_setting = False

# directory name handlers
def set_directory_name_handler(self, value):
    global is_setting
    if not is_setting:
        is_setting = True
        self["directory_name_internal"] = correct_file_name(value, is_directory = True)
        is_setting = False
def get_directory_name_handler(self):
    try: return self["directory_name_internal"]   
    except: return "" 

# file name handlers
def set_file_name_handler(self, value):
    global is_setting
    if not is_setting:
        is_setting = True
        self["file_name_internal"] = correct_file_name(value, is_directory = False)
        is_setting = False
def get_file_name_handler(self):
    try: return self["file_name_internal"]
    except: return ""

class AddonDevelopmentSceneProperties(bpy.types.PropertyGroup):
    addon_name = StringProperty(name = "Addon Name", default = "my_addon", set = set_directory_name_handler, get = get_directory_name_handler)    
        
def correct_file_name(name, is_directory = False):
    new_name = ""
    for char in name:
        if char.isupper():
            new_name += char.lower()
        elif char.islower() or char == "_":
            new_name += char
        elif char == " ":
            new_name += "_"  
        elif char.isdigit() and len(new_name) > 0:
            new_name += char
        elif not is_directory and char == "." and new_name.count(".") == 0:
            new_name += char
    return new_name     
        


addons_path = bpy.utils.user_resource("SCRIPTS", "addons") 
directory_visibility = defaultdict(bool)

class AddonDeveloperPanel(bpy.types.Panel):
    bl_idname = "addon_developer_panel"
    bl_label = "Addon Development"
    bl_space_type = "TEXT_EDITOR"
    bl_region_type = "UI"
    
    def draw(self, context):
        layout = self.layout
        setting = get_settings()
        layout.prop(setting, "addon_name", text = "Name")
        layout.operator("script_auto_complete.new_addon", icon = "NEW")
        
        layout.operator("script_auto_complete.export_addon", icon = "EXPORT")
        
        
class AddonFilesPanel(bpy.types.Panel):
    bl_idname = "addon_files_panel"
    bl_label = "Addon Files"
    bl_space_type = "TEXT_EDITOR"
    bl_region_type = "UI"
    
    @classmethod
    def poll(cls, context):
        return current_addon_exists()
    
    def draw(self, context):
        layout = self.layout
        addon_path = get_current_addon_path()
        
        layout.operator("script_auto_complete.save_files", icon = "SAVE_COPY")
        self.draw_directory(layout, addon_path)
            
    def draw_directory(self, layout, directory):
        box = layout.box()
        if self.is_directory_visible(directory): icon = "DOWNARROW_HLT"
        else: icon = "RIGHTARROW"
        operator = box.operator("script_auto_complete.toogle_directory_visibility", text = directory[:-1].split("\\")[-1], icon = icon, emboss = False)
        operator.directory = directory
        
        if self.is_directory_visible(directory):
            directory_names = get_directory_names(directory)
            for directory_name in directory_names:
                self.draw_directory(box, directory + directory_name + "\\")
            
            col = box.column(align = True)    
            file_names = get_file_names(directory)
            for file_name in file_names:
                row = col.row()
                operator = row.operator("script_auto_complete.open_file", text = "", emboss = True, icon = "FILE")
                operator.path = directory + file_name
                row.label(file_name)
            
            row = box.row(align = True)    
            operator = row.operator("script_auto_complete.new_file", icon = "PLUS", text = "File")
            operator.directory = directory
            operator = row.operator("script_auto_complete.new_directory", icon = "PLUS", text = "Directory")
            operator.directory = directory
                
    def is_directory_visible(self, directory):
        return directory_visibility[directory]                
 
ignore_names = ["__pycache__", ".git", ".gitignore"] 
def get_directory_names(directory):
    return [file_name for file_name in listdir(directory) if not isfile(join(directory, file_name)) and file_name not in ignore_names]         
def get_file_names(directory):
    return [file_name for file_name in listdir(directory) if isfile(join(directory, file_name)) and file_name not in ignore_names]     

class CreateNewAddon(bpy.types.Operator):
    bl_idname = "script_auto_complete.new_addon"
    bl_label = "New Addon"
    bl_description = "Create a folder in the addon directory and setup a basic code base"
    bl_options = {"REGISTER"}
    
    @classmethod
    def poll(cls, context):
        return True
    
    def execute(self, context):
        self.create_addon_directory()
        self.create_init_file()
        return {"FINISHED"}
    
    def create_addon_directory(self):
        if not current_addon_exists():
            os.makedirs(get_current_addon_path())
            
    def create_init_file(self):
        new_addon_file("__init__.py")
        

            
class NewFile(bpy.types.Operator):
    bl_idname = "script_auto_complete.new_file"
    bl_label = "New File"
    bl_description = "Create a new file in this directory"
    bl_options = {"REGISTER"}
    
    directory = StringProperty(name = "Directory", default = "")
    name = StringProperty(name = "File Name", default = "", set = set_file_name_handler, get = get_file_name_handler)
    
    @classmethod
    def poll(cls, context):
        return current_addon_exists()
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width = 400)
    
    def draw(self, context):
        layout = self.layout
        layout.prop(self, "name")
    
    def execute(self, context):
        if self.name != "":
            new_file(self.directory + self.name)
        return {"FINISHED"}
    
    
class NewDirectory(bpy.types.Operator):
    bl_idname = "script_auto_complete.new_directory"
    bl_label = "New Directory"
    bl_description = "Create a new subdirectory"
    bl_options = {"REGISTER"}
    
    directory = StringProperty(name = "Directory", default = "")
    name = StringProperty(name = "Directory Name", default = "", set = set_directory_name_handler, get = get_directory_name_handler)
    
    @classmethod
    def poll(cls, context):
        return current_addon_exists()
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width = 400)
    
    def draw(self, context):
        layout = self.layout
        layout.prop(self, "name")
    
    def execute(self, context):
        if self.name != "":
            new_directory(self.directory + self.name)
        return {"FINISHED"}    
    
  
def new_addon_file(path):
    new_file(get_current_addon_path() + path) 
       
def new_file(path):
    dirname = os.path.dirname(path)
    new_directory(dirname)
    if not os.path.exists(path):
        open(path, "a").close()
        
def new_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)       
      
    
class ToogleDirectoryVisibility(bpy.types.Operator):
    bl_idname = "script_auto_complete.toogle_directory_visibility"
    bl_label = "Toogle Directory Visibility"
    bl_description = ""
    bl_options = {"REGISTER"}
    
    directory = StringProperty(name = "Directory", default = "")
    
    @classmethod
    def poll(cls, context):
        return True
    
    def execute(self, context):
        global directory_visibility
        directory_visibility[self.directory] = not directory_visibility[self.directory]
        return {"FINISHED"}
            
            
class OpenFile(bpy.types.Operator):
    bl_idname = "script_auto_complete.open_file"
    bl_label = "label"
    bl_description = "Opens the file in the text editor (hold ctrl to copy the path)"
    bl_options = {"REGISTER"}
    
    path = StringProperty(name = "Path", default = "")
    
    @classmethod
    def poll(cls, context):
        return True
    
    def invoke(self, context, event):
        if event.ctrl:
            context.window_manager.clipboard = dirname(self.path)
        else:
            text = None
            for text_block in bpy.data.texts:
                if text_block.filepath == self.path:
                    text = text_block
                    break
            if not text:
                text = bpy.data.texts.load(self.path, internal = False)
            context.space_data.text = text
        return {"FINISHED"}
    
    
class SaveFiles(bpy.types.Operator):
    bl_idname = "script_auto_complete.save_files"
    bl_label = "Save All Files"
    bl_description = "Save all files which correspond to a file on the hard drive"
    bl_options = {"REGISTER"}
    
    @classmethod
    def poll(cls, context):
        return True
    
    def execute(self, context):
        for text in bpy.data.texts:
            save_text_block(text)
        return {"FINISHED"}
            
                    
class ExportAddon(bpy.types.Operator):
    bl_idname = "script_auto_complete.export_addon"
    bl_label = "Export Addon"
    bl_description = "Save a .zip file of the addon"
    bl_options = {"REGISTER"}
    
    filepath = StringProperty(subtype = "FILE_PATH")
    
    @classmethod
    def poll(cls, context):
        return current_addon_exists()
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}
    
    def execute(self, context):
        source_path = get_current_addon_path()
        output_path = self.filepath
        zip_directory(source_path, output_path)
        return {"FINISHED"}
            
   
    
def current_addon_exists():
    return os.path.exists(get_current_addon_path()) and get_settings().addon_name != ""
    
def get_current_addon_path():
    return "{}\\{}\\".format(addons_path, get_settings().addon_name)  

def get_settings():
    return bpy.context.scene.addon_development

def save_text_block(text_block):
    if not text_block: return
    if text_block.filepath == "": return

    file = open(text_block.filepath, mode = "w")
    file.write(text_block.as_string())
    file.close()
    
def zip_directory(source_path, output_path):
    try:
        parent_folder = dirname(source_path)
        content = os.walk(source_path)  
        zip_file = zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED)
        for root, folders, files in content:
            for data in folders + files:
                absolute_path = join(root, data)
                relative_path = absolute_path[len(parent_folder+"\\"):]
                zip_file.write(absolute_path, relative_path)
        zip_file.close()
    except: print("Could not zip the directory")
    
def start_another_blender_instance():
    os.startfile(bpy.app.binary_path)            