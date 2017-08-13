import bpy
import os
import sys
import shutil
import inspect
import textwrap
from ... settings import get_preferences
from . rna_utils import get_readable_property_type

fake_package_name = "_bpy_fake"
top_directory = os.path.join(os.path.dirname(__file__), "dynamic")
directory = os.path.join(top_directory, fake_package_name)
private_path = os.path.join(directory, "__private__")

sys.path.append(top_directory)

docstring_width = 70
use_quote_marks = False


class GenerateFakeBPY(bpy.types.Operator):
    bl_idname = "code_autocomplete.regenerate_fake_bpy"
    bl_label = "Generate Fake BPY"
    bl_description = "Regenerate the fake bpy module that the jedi autocompletion needs"
    bl_options = {"REGISTER"}

    def execute(self, context):
        regenerate_fake_bpy()
        return {"FINISHED"}

def fake_bpy_module_exists():
    return os.path.exists(private_path)

def regenerate_fake_bpy():
    remove_old_fake()
    generate_fake_bpy()

def remove_old_fake():
    if os.path.exists(directory):
        shutil.rmtree(directory, ignore_errors = True)

def generate_fake_bpy():
    try: os.makedirs(directory)
    except: pass
    create_init()
    create_private_subdirectory()

def create_init():
    path = os.path.join(directory, "__init__.py")
    file = open(path, "w+", encoding='utf-8')
    file.write(init_content)
    file.close()

init_content = '''
from . __private__.context import Context as context
from . __private__.blenddata import BlendData as data
'''

def create_private_subdirectory():
    os.makedirs(private_path)
    open(os.path.join(private_path, "__init__.py"), "a").close()
    write_code_file("__init__", "")
    write_code_file("bpy_struct", bpy_struct_content)
    generate_code_files()


collection_types = {}
def generate_code_files(create_all = False):
    types_to_generate = {"Context", "Panel"}
    generated_types = set()

    while len(types_to_generate) > 0:
        name = types_to_generate.pop()
        generated_types.add(name)
        type = getattr(bpy.types, name)
        code, dependencies = get_code_and_dependencies(name, type)
        write_code_file(name, code)
        types_to_generate.update([d for d in dependencies if d not in generated_types])

        if len(types_to_generate) == 0 and create_all:
            bpy_types = [(name, type) for name, type in inspect.getmembers(bpy.types) if "." not in name]
            for name, type in bpy_types:
                if name not in generated_types:
                    types_to_generate.add(name)


def get_code_and_dependencies(name, type):
    dependencies = get_dependencies(name, type)

    lines = []
    lines.extend(get_import_code_lines(dependencies))
    lines.append("class {}({}):".format(name, "" if name == "Context" else "bpy_struct"))
    lines.extend(get_property_code_lines(type))
    lines.extend(get_function_code_lines(name, type))

    return "\n".join(lines), dependencies

def get_import_code_lines(dependencies):
    return ["from . {} import {}".format(d.lower(), d) for d in dependencies] + ["from . bpy_struct import bpy_struct", "import mathutils", ""]

def get_property_code_lines(type):
    lines = []
    for property in get_type_properties(type):
        lines.extend(get_property_definition_code_lines(property))
    return lines

def get_property_definition_code_lines(property):
    lines = []
    lines.append("    @property")
    lines.append("    def {}(self):".format(property.identifier))
    lines.extend(get_property_docstring_lines(property, docstring_width))
    lines.append("        return {}".format(get_property_declaration(property)))
    return lines

def get_function_code_lines(name, type):
    lines = []
    for function in type.bl_rna.functions:
        lines.append("    def {}({}):".format(function.identifier, get_function_parameter_list(function)))
        lines.extend(get_function_docstring_lines(function, docstring_width))
        lines.append("        return {}".format(get_function_return_list(function)))

    global collection_types
    if name in collection_types:
        subtype = collection_types[name]
        lines.append("    def get(key): return {}()".format(subtype))
        lines.append("    def __getitem__(key): return {}()".format(subtype))
        lines.append("    def __iter__(key): yield {}()".format(subtype))

    return lines

def get_property_docstring_lines(property, width = 70, indent = 8):
    lines = get_property_description_lines(property, width)
    lines.extend(get_enum_item_lines(property, width))
    return make_docstring_from_lines(lines, indent)

def get_function_docstring_lines(function, width = 70, indent = 8):
    lines = get_function_description_lines(function, width)
    parameter_lines = get_parameter_lines(function, width)
    lines.extend(parameter_lines)
    return make_docstring_from_lines(lines, indent)

def get_parameter_lines(function, width):
    lines = []
    params = [p for p in function.parameters if not p.is_output]
    if len(params) > 0:
        lines.append("")
        lines.append("Parameter:")
        lines.extend(get_parameter_list_lines(params, width))
    returns = [p for p in function.parameters if p.is_output]
    if len(returns) > 0:
        lines.append("")
        lines.append("Returns:")
        lines.extend(get_parameter_list_lines(returns, width))
    return lines

def get_parameter_list_lines(params, width):
    lines = []
    for param in params:
        lines.append("{}:".format(param.identifier))
        description_lines = get_property_description_lines(param, width)
        amount = len(description_lines)
        if amount == 0: lines[-1] += " <no description available>"
        elif amount == 1: lines[-1] += " " + description_lines[0]
        else:
            indent_lines(description_lines, 2)
            lines.extend(description_lines)
    indent_lines(lines, 2)
    return lines

def get_property_description_lines(property, width):
    type = "({})".format(get_readable_property_type(property))
    if property.description in (None, ""): return [type]
    return textwrap.wrap(type + " " + property.description, width)

def get_function_description_lines(function, width):
    if function.description in (None, ""): return []
    return textwrap.wrap(function.description, width)

def get_enum_item_lines(property, width):
    if getattr(property, "enum_items", None) is None: return []
    items = property.enum_items
    if len(items) == 0: return []
    quote_mark = "'" if use_quote_marks else ""
    item_string = "["+ ", ".join(quote_mark + item.identifier + quote_mark for item in items) +"]"
    return [""] + textwrap.wrap(item_string, width)

def make_docstring_from_lines(lines, indent = 8):
    if len(lines) == 0: return []
    lines[0] = "'''" + lines[0]
    lines[-1] += "'''"
    indent_lines(lines, indent)
    return lines

def indent_lines(lines, indent = 4):
    spaces = " " * indent
    for i in range(len(lines)):
        lines[i] = spaces + lines[i]

def get_dependencies(name, type):
    def find_property_dependency(property):
        if property.type == "POINTER":
            dependencies.add(property.fixed_type.identifier)
        if property.type == "COLLECTION":
            if property.srna is None: dependencies.add(property.fixed_type.identifier)
            else: dependencies.add(property.srna.identifier)

    dependencies = set()
    if name in collection_types:
        dependencies.add(collection_types[name])
    for property in get_type_properties(type):
        find_property_dependency(property)
    for function in type.bl_rna.functions:
        for parameter in function.parameters:
            find_property_dependency(parameter)
    return dependencies

def get_type_properties(type):
    fakes = []
    if type.bl_rna.identifier == "Context":
        fakes = fake_context_properties
    return list(type.bl_rna.properties) + fakes

def get_function_parameter_list(function):
    parameters = ["self"] + [parameter.identifier for parameter in function.parameters if not parameter.is_output]
    return ", ".join(parameters)

def get_function_return_list(function):
    returns = [parameter for parameter in function.parameters if parameter.is_output]
    return ", ".join([get_property_declaration(parameter) for parameter in returns])

def get_property_declaration(property):
    global collection_types
    if property.type == "BOOLEAN": return "bool()"
    if property.type == "INT": return "int()"
    if property.type in ("STRING", "ENUM"): return "str()"
    if property.type == "COLLECTION":
        if property.srna is None: return "({}(),)".format(property.fixed_type.identifier)
        else:
            collection_types[property.srna.identifier] = property.fixed_type.identifier
            return property.srna.identifier + "()"
    if property.type == "FLOAT":
        if property.array_length <= 1: return "float()"
        if property.array_length in (2, 3): return "mathutils.Vector()"
        if property.array_length == 16: return "mathutils.Matrix()"
    if property.type == "POINTER":
        return property.fixed_type.identifier + "()"
    return "''"

def write_code_file(name, code):
    path = os.path.join(private_path, name.lower() + ".py")
    file = open(path, "w+", encoding='utf-8')
    file.write(code)
    file.close()




bpy_struct_content = '''
from . fcurve import FCurve

class bpy_struct:
    id_data = ID()
    def as_pointer():
        return int()
    def driver_add(path, index):
        return FCurve()
    def driver_remove(path, index):
        return bool()
    def keyframe_delete(data_path, index, frame, group):
        return bool()
    def keyframe_insert(data_path, index, frame, group):
        return bool()
    def path_from_id(property):
        return str()
    def path_resolve(path, coerce):
        return
    def property_unsert(property):
        return
'''

class FakeProp:
    def __init__(self, identifier):
        self.identifier = identifier
    def __getattr__(self, name):
        if name == "type": return ""
        if name == "array_length": return 0
        if name == "srna": return None
        if name == "fixed_type": return None

class FakePointer(FakeProp):
    def __init__(self, name, fixed_identifier):
        self.identifier = name
        self.type = "POINTER"
        self.fixed_type = FakeProp(fixed_identifier)

class FakeSequence(FakeProp):
    def __init__(self, name, fixed_identifier):
        self.identifier = name
        self.type = "COLLECTION"
        self.fixed_type = FakeProp(fixed_identifier)

FP = FakePointer
FS = FakeSequence

fake_context_properties = [
    FP("active_bone", "EditBone"),
    FP("active_pose_bone", "PoseBone"),
    FP("active_base", "ObjectBase"),
    FP("active_object", "Object"),
    FP("object", "Object"),
    FP("edit_object", "Object"),
    FP("sculpt_object", "Object"),
    FP("vertex_paint_object", "Object"),
    FP("weight_paint_object", "Object"),
    FP("image_paint_object", "Object"),
    FP("particle_edit_object", "Object"),
    FP("gpencil_data", "GreasePencil"),
    FP("gpencil_data_owner", "ID"),
    FP("active_operator", "Operator"),
    FP("texture_slot", "MaterialTextureSlot"),
    FP("world", "World"),
    FP("mesh", "Mesh"),
    FP("armature", "Armature"),
    FP("lattice", "Lattice"),
    FP("curve", "Curve"),
    FP("meta_ball", "MetaBall"),
    FP("lamp", "Lamp"),
    FP("speaker", "Speaker"),
    FP("camera", "Camera"),
    FP("material", "Material"),
    FP("material_slot", "MaterialSlot"),
    FP("texture", "Texture"),
    FP("texture_user", "ID"),
    FP("texture_user_property", "Property"),
    FP("bone", "Bone"),
    FP("particle_system", "ParticleSystem"),
    FP("particle_system_editable", "ParticleSystem"),
    FP("particle_settings", "ParticleSettings"),
    FP("cloth", "ClothModifier"),
    FP("soft_body", "SoftBodyModifier"),
    FP("fluid", "FluidSimulationModifier"),
    FP("smoke", "SmokeModifier"),
    FP("collision", "CollisionModifier"),
    FP("brush", "Brush"),
    FP("dynamic_paint", "DynamicPaintModifier"),
    FP("line_style", "FreestyleLineStyle"),
    FP("edit_image", "Image"),
    FP("edit_mask", "Mask"),
    FP("active_node", "Node"),
    FP("edit_text", "Text"),
    FP("edit_movieclip", "MovieClip"),
    FS("visible_objects", "Object"),
    FS("visible_bases", "ObjectBase"),
    FS("selectable_objects", "Object"),
    FS("selectable_bases", "ObjectBase"),
    FS("selected_objects", "Object"),
    FS("selected_bases", "ObjectBase"),
    FS("selected_editable_objects", "Object"),
    FS("selected_editable_bases", "ObjectBase"),
    FS("visible_bones", "EditBone"),
    FS("editable_bones", "EditBone"),
    FS("selected_bones", "EditBone"),
    FS("selected_editable_bones", "EditBone"),
    FS("visible_pose_bones", "PoseBone"),
    FS("selected_pose_bones", "PoseBone"),
    FS("sequences", "Sequence"),
    FS("selected_sequences", "Sequence"),
    FS("selected_editable_sequences", "Sequence"),
    FS("visible_gpencil_layers", "GPencilLayer"),
    FS("editable_gpencil_layers", "GPencilLayer"),
    FS("editable_gpencil_strokes", "GPencilStroke"),
    FS("active_gpencil_layer", "GPencilLayer"),
    FS("active_gpencil_frame", "GPencilLayer"),
    FS("selected_nodes", "Node") ]
