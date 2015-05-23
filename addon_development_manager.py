import bpy 
import os
import sys
import zipfile
import importlib
import subprocess
import addon_utils
from bpy.props import *
from os import listdir
from os.path import isfile, isdir, join, dirname, basename
from collections import defaultdict
from bpy.app.handlers import persistent
from . text_block import TextBlock

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
    addon_name = StringProperty(name = "Addon Name", default = "my_addon", description = "Name of the currently selected addon")    
        
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
        row = layout.row(align = True)
        row.prop(setting, "addon_name", text = "Name")
        row.operator("code_autocomplete.find_existing_addon", icon = "EYEDROPPER", text = "")
        
        if not current_addon_exists():
            if not is_addon_name_valid():
                layout.operator("code_autocomplete.make_addon_name_valid", icon = "ERROR", text = "Correct Addon Name")
            else:
                row = layout.row()
                row.scale_y = 1.2
                row.operator_menu_enum("code_autocomplete.new_addon", "new_addon_type", icon = "NEW", text = "New Addon")
        else:
            row = layout.row()
            row.scale_y = 1.5
            row.operator("code_autocomplete.run_addon", icon = "OUTLINER_DATA_POSE", text = "Run Addon")
            layout.operator("code_autocomplete.export_addon", icon = "EXPORT", text = "Export as Zip")
        layout.operator("code_autocomplete.restart_blender", icon = "BLENDER")
        
        
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
        
        layout.operator("code_autocomplete.save_files", icon = "SAVE_COPY")
        self.draw_directory(layout, addon_path)
            
    def draw_directory(self, layout, directory):
        box = layout.box()
        if self.is_directory_visible(directory): icon = "DOWNARROW_HLT"
        else: icon = "RIGHTARROW"
        operator = box.operator("code_autocomplete.toogle_directory_visibility", text = os.path.split(directory[:-1])[-1], icon = icon, emboss = False)
        operator.directory = directory
        
        if self.is_directory_visible(directory):
            col = box.column(align = True)
            directory_names = get_directory_names(directory)
            for directory_name in directory_names:
                row = col.row()
                self.draw_directory(row, directory + directory_name + os.sep)
            
            file_names = get_file_names(directory)
            col = box.column(align = True) 
            for file_name in file_names:
                row = col.row()
                row.alignment = "LEFT"
                full_path = directory + file_name
                props = row.operator("code_autocomplete.open_file_menu", icon = "COLLAPSEMENU", text = "", emboss = True)
                props.path = full_path
                if full_path == get_current_filepath():
                    row.label("", icon = "RIGHTARROW_THIN")
                operator = row.operator("code_autocomplete.open_file", text = file_name, emboss = False)
                operator.path = full_path
            
            row = box.row(align = True)    
            operator = row.operator("code_autocomplete.new_file", icon = "PLUS", text = "File")
            operator.directory = directory
            operator = row.operator("code_autocomplete.new_directory", icon = "PLUS", text = "Directory")
            operator.directory = directory
                
    def is_directory_visible(self, directory):
        return directory_visibility[directory]                
 
ignore_names = ["__pycache__", ".git", ".gitignore"] 
def get_directory_names(directory):
    return [file_name for file_name in listdir(directory) if not isfile(join(directory, file_name)) and file_name not in ignore_names]         
def get_file_names(directory):
    return [file_name for file_name in listdir(directory) if isfile(join(directory, file_name)) and file_name not in ignore_names] 



class FindExistingAddon(bpy.types.Operator):
    bl_idname = "code_autocomplete.find_existing_addon"
    bl_label = "Find Existing Addon"
    bl_description = "Pick an existing addon"
    bl_options = {"REGISTER"}
    bl_property = "item"
    
    def get_items(self, context):
        items = []
        directories = get_directory_names(addons_path)
        for addon in directories:
            items.append((addon, addon, ""))
        return items
        
    item = bpy.props.EnumProperty(items = get_items)
        
    def invoke(self, context, event):
        context.window_manager.invoke_search_popup(self)
        return {"CANCELLED"}
        
    def execute(self, context):
        get_settings().addon_name = self.item
        make_directory_visible(get_current_addon_path()) 
        context.area.tag_redraw()
        return {"FINISHED"}
        
        
class MakeAddonNameValid(bpy.types.Operator):
    bl_idname = "code_autocomplete.make_addon_name_valid"
    bl_label = "Make Name Valid"
    bl_description = "Make the addon name a valid module name"
    bl_options = {"REGISTER"}
    
    @classmethod
    def poll(cls, context):
        return not current_addon_exists() and not is_addon_name_valid()
    
    def execute(self, context):
        name = get_addon_name()
        get_settings().addon_name = correct_file_name(name, is_directory = True)
        return {"FINISHED"}     

        
new_addon_type_items = [
    ("BASIC", "Basic", ""),
    ("MULTIFILE", "Multi-File (recommended)", "") ]        

class CreateNewAddon(bpy.types.Operator):
    bl_idname = "code_autocomplete.new_addon"
    bl_label = "New Addon"
    bl_description = "Create a folder in the addon directory and setup a basic code base"
    bl_options = {"REGISTER"}
    
    new_addon_type = EnumProperty(default = "BASIC", items = new_addon_type_items)
    
    @classmethod
    def poll(cls, context):
        return not current_addon_exists() and is_addon_name_valid()
    
    def execute(self, context):
        self.create_addon_directory()
        self.generate_from_template()
        addon_path = get_current_addon_path()
        bpy.ops.code_autocomplete.open_file(path = addon_path + "__init__.py")
        make_directory_visible(addon_path)
        context.area.tag_redraw()
        return {"FINISHED"}
    
    def create_addon_directory(self):
        os.makedirs(get_current_addon_path())
            
    def generate_from_template(self):
        t = self.new_addon_type
        if t == "BASIC": 
            code = code = self.read_template_file("basic.txt")
            new_addon_file("__init__.py", code)
        
        if t == "MULTIFILE": 
            code = self.read_template_file("multifile.txt")
            new_addon_file("__init__.py", code)
            code = self.read_template_file("developer_utils.txt")
            new_addon_file("developer_utils.py", code)
    
    def read_template_file(self, path):
        path = join(dirname(__file__), "addon_templates", path)
        file = open(path)
        text = file.read()
        file.close()
        return text

            
class NewFile(bpy.types.Operator):
    bl_idname = "code_autocomplete.new_file"
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
            path = self.directory + self.name
            new_file(self.directory + self.name)
            bpy.ops.code_autocomplete.open_file(path = path)
            context.area.tag_redraw()
        return {"FINISHED"}
    
    
class NewDirectory(bpy.types.Operator):
    bl_idname = "code_autocomplete.new_directory"
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
            new_file(join(self.directory + self.name, "__init__.py"))
            context.area.tag_redraw()
        return {"FINISHED"}    
    
  
def new_addon_file(path, default = ""):
    new_file(get_current_addon_path() + path, default) 
       
def new_file(path, default = ""):
    dirname = os.path.dirname(path)
    new_directory(dirname)
    if not os.path.exists(path):
        file = open(path, "a")
        file.write(default)
        file.close()
        
def new_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)       
      
    
class ToogleDirectoryVisibility(bpy.types.Operator):
    bl_idname = "code_autocomplete.toogle_directory_visibility"
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
        
        
class FileMenuOpener(bpy.types.Operator):
    bl_idname = "code_autocomplete.open_file_menu"
    bl_label = "Open File Menu"
    
    path = StringProperty(name = "Path", default = "")
    
    def invoke(self, context, event):
        context.window_manager.popup_menu(self.drawMenu, title = "{} - File Menu".format(basename(self.path)))
        return {"FINISHED"}
    
    def drawMenu(fileProps, self, context):
        layout = self.layout
        layout.operator_context = "INVOKE_DEFAULT"
        props = layout.operator("code_autocomplete.rename_file", text = "Rename")        
        props.path = fileProps.path
        props = layout.operator("code_autocomplete.open_file", text = "Open in Text Editor")        
        props.path = fileProps.path
        props = layout.operator("code_autocomplete.open_external_file_browser", text = "Open External")        
        props.directory = dirname(fileProps.path)
        layout.separator()
        props = layout.operator("code_autocomplete.delete_file", text = "Delete", icon = "ERROR")        
        props.path = fileProps.path
            
            
class OpenFile(bpy.types.Operator):
    bl_idname = "code_autocomplete.open_file"
    bl_label = "Open File"
    bl_description = "Load the file into the text editor"
    bl_options = {"REGISTER"}
    
    path = StringProperty(name = "Path", default = "")
        
    def execute(self, context):
        text = None
        for text_block in bpy.data.texts:
            if text_block.filepath == self.path:
                text = text_block
                break
        if not text:
            text = bpy.data.texts.load(self.path, internal = False)
        
        context.space_data.text = text
        return {"FINISHED"}
    
    
class OpenExternalFileBrowser(bpy.types.Operator):
    bl_idname = "code_autocomplete.open_external_file_browser"
    bl_label = "Open External File Browser"
    bl_description = ""
    bl_options = {"REGISTER"}
    
    directory = StringProperty(name = "Directory", default = "")
    
    def execute(self, context):
        bpy.ops.wm.path_open(filepath = self.directory)
        return {"FINISHED"}
        
        
class RenameFile(bpy.types.Operator):
    bl_idname = "code_autocomplete.rename_file"
    bl_label = "Open External File Browser"
    bl_description = ""
    bl_options = {"REGISTER"}
    
    path = StringProperty(name = "Directory", default = "")
    new_name = StringProperty(name = "Directory", description = "New file name", default = "")
    
    def invoke(self, context, event):
        self.new_name = basename(self.path)
        return context.window_manager.invoke_props_dialog(self, width = 400)
    
    def draw(self, context):
        layout = self.layout
        layout.prop(self, "new_name")
    
    def execute(self, context):
        new_path = join(dirname(self.path), self.new_name)
        os.rename(self.path, new_path)
        self.correct_text_block_paths(self.path, new_path)
        context.area.tag_redraw()
        return {"FINISHED"}     

    def correct_text_block_paths(self, old_path, new_path):
        for text in bpy.data.texts:
            if text.filepath == old_path:
                text.filepath = new_path
                
                
class DeleteFile(bpy.types.Operator):
    bl_idname = "code_autocomplete.delete_file"
    bl_label = "Delete File"
    bl_description = "Delete file on the hard drive"
    bl_options = {"REGISTER"}
    
    path = StringProperty(name = "Directory", default = "")
    
    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)
    
    def execute(self, context):
        os.remove(self.path)
        context.area.tag_redraw()
        return {"FINISHED"}  
    
    
class SaveFiles(bpy.types.Operator):
    bl_idname = "code_autocomplete.save_files"
    bl_label = "Save All Files"
    bl_description = "Save all files which correspond to a file on the hard drive"
    bl_options = {"REGISTER"}
    
    @classmethod
    def poll(cls, context):
        return True
    
    def execute(self, context):
        for text in bpy.data.texts:
            save_text_block(text)
        try: bpy.ops.text.resolve_conflict(resolution = "IGNORE")
        except: pass
        return {"FINISHED"}
        
        
class ConvertAddonIndentation(bpy.types.Operator):
    bl_idname = "code_autocomplete.convert_addon_indentation"
    bl_label = "Convert Addon Indentation"
    bl_description = ""
    bl_options = {"REGISTER"}
    
    old_indentation = StringProperty(default = "\t")
    new_indentation = StringProperty(default = "    ")
    
    @classmethod
    def poll(cls, context):
        return current_addon_exists()
        
    def execute(self, context):
        paths = self.get_addon_files()
        for path in paths:
            bpy.ops.code_autocomplete.convert_file_indentation(
                path = path, 
                old_indentation = self.old_indentation, 
                new_indentation = self.new_indentation)
        return {"FINISHED"}
        
    def get_addon_files(self):
        paths = []
        for root, dirs, files in os.walk(get_current_addon_path()):
            for file in files:
                if file.endswith(".py"):
                    paths.append(join(root, file))
        return paths
            
                    
class ExportAddon(bpy.types.Operator):
    bl_idname = "code_autocomplete.export_addon"
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
        subdirectory_name = get_addon_name() + os.sep
        source_path = get_current_addon_path()
        output_path = self.filepath
        if not output_path.lower().endswith(".zip"):
            output_path += ".zip"
        zip_directory(source_path, output_path, additional_path = subdirectory_name)
        return {"FINISHED"}
   
            
class RunAddon(bpy.types.Operator):
    bl_idname = "code_autocomplete.run_addon"
    bl_label = "Run Addon"
    bl_description = "Unregister, reload and register it again."
    bl_options = {"REGISTER"}
    
    @classmethod
    def poll(cls, context):
        return current_addon_exists()
    
    def execute(self, context):
        bpy.ops.code_autocomplete.save_files()
        
        addon_name = get_addon_name()
        module = sys.modules.get(addon_name)
        if module:  
            addon_utils.disable(addon_name)
            importlib.reload(module)
        addon_utils.enable(addon_name)
        return {"FINISHED"}        


class RestartBlender(bpy.types.Operator):
    bl_idname = "code_autocomplete.restart_blender"
    bl_label = "Restart Blender"
    bl_description = "Close and open a new Blender instance to test the Addon on the startup file. (Currently only supported for windows)"
    bl_options = {"REGISTER"}
    
    @classmethod
    def poll(cls, context):
        return sys.platform == "win32"
    
    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)
    
    def execute(self, context):
        bpy.ops.code_autocomplete.save_files()
        save_status()
        start_another_blender_instance()
        bpy.ops.wm.quit_blender()
        return {"FINISHED"}         
        

restart_data_path = join(dirname(__file__), "restart_data.txt")   

id_addon_name = "ADDON_NAME: "
id_current_path = "CURRENT_PATH: "  
id_visiblie_path = "VISIBLE_PATH: "
def save_status():
    file = open(restart_data_path, "w")
    file.write(id_addon_name + get_addon_name() + "\n")
    text_block = bpy.context.space_data.text
    if text_block:
        file.write(id_current_path + text_block.filepath + "\n")
    for path, is_open in directory_visibility.items():
        if is_open:
            file.write(id_visiblie_path + path + "\n")
            
    file.close()
 
@persistent 
def open_status(scene):
    if os.path.exists(restart_data_path):
        file = open(restart_data_path)
        lines = file.readlines()
        file.close()
        os.remove(restart_data_path)
        parse_startup_file_lines(lines)
        
def parse_startup_file_lines(lines):        
    for line in lines:
        if line.startswith(id_addon_name):
            get_settings().addon_name = line[len(id_addon_name):].strip()
        if line.startswith(id_current_path):
            path = line[len(id_current_path):].strip()
            text_block = bpy.data.texts.load(path, internal = False)
            for screen in bpy.data.screens:
                for area in screen.areas:
                    for space in area.spaces:
                        if space.type == "TEXT_EDITOR":
                            space.text = text_block
        if line.startswith(id_visiblie_path):
            path = line[len(id_visiblie_path):].strip()
            make_directory_visible(path)   

def make_directory_visible(path):
    global directory_visibility
    directory_visibility[path] = True   
    
def get_current_filepath():
    try: return bpy.context.space_data.text.filepath
    except: return ""
    
def current_addon_exists():
    return os.path.exists(get_current_addon_path()) and get_settings().addon_name != ""
    
def get_current_addon_path():
    return join(addons_path, get_addon_name()) + os.sep

def is_addon_name_valid():
    name = get_addon_name()
    return name == correct_file_name(name, is_directory = True) and name != ""
    
def get_addon_name():
    return get_settings().addon_name

def get_settings():
    return bpy.context.scene.addon_development

def save_text_block(text_block):
    if not text_block: return
    if not os.path.exists(text_block.filepath): return

    file = open(text_block.filepath, mode = "w")
    file.write(text_block.as_string())
    file.close()
    
def zip_directory(source_path, output_path, additional_path = ""):
    try:
        parent_folder = dirname(source_path)
        content = os.walk(source_path)  
        zip_file = zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED)
        for root, folders, files in content:
            for data in folders + files:
                absolute_path = join(root, data)
                relative_path = additional_path + absolute_path[len(parent_folder+os.sep):]
                zip_file.write(absolute_path, relative_path)
        zip_file.close()
    except: print("Could not zip the directory")
    
def start_another_blender_instance():
    open_file(bpy.app.binary_path) 
 
# only works for windows currently   
def open_file(path):
    if sys.platform == "win32":
        os.startfile(path)
    else:
        opener = "open" if sys.platform == "darwin" else "xdg-open"
        subprocess.call([opener, path])


    
    
bpy.app.handlers.load_post.append(open_status)  
