import bpy
import os

addons_path = bpy.utils.user_resource("SCRIPTS", "addons")

def get_current_filepath():
    try: return bpy.context.space_data.text.filepath
    except: return ""

def current_addon_exists():
    return os.path.exists(get_current_addon_path()) and get_settings().addon_name != ""

def get_current_addon_path():
    return os.path.join(addons_path, get_addon_name()) + os.sep

def is_addon_name_valid():
    name = get_addon_name()
    return name == correct_file_name(name, is_directory = True) and name != ""

def get_addon_name():
    return get_settings().addon_name

def get_settings():
    return bpy.context.scene.addon_development


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



def get_directory_names(directory):
    return [name for path, name in get_directory_content(directory) if not os.path.isfile(path)]
def get_file_names(directory):
    return [name for path, name in get_directory_content(directory) if os.path.isfile(path)]

ignore_names = ["__pycache__", ".git"]
def get_directory_content(directory):
    return [(os.path.join(directory, name), name) for name in os.listdir(directory) if name not in ignore_names]
