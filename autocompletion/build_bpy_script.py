import bpy
import inspect

class BuildScript(bpy.types.Operator):
    bl_idname = "code_autocomplete.build_script"
    bl_label = "Build Script"
    bl_description = ""
    
    def execute(self, context):
        text = bpy.data.texts.get("bpy_script.py")
        if not text:
            text = bpy.data.texts.new("bpy_script.py")
        text.from_string(build_bpy_script())
        return { "FINISHED" }

def build_bpy_script():
    bpy_types = [type for type in inspect.getmembers(bpy.types) if "." not in type[0]]
    
    import_lines = ["import mathutils"]
    script = "\n\n".join(import_lines + [build_type_script(*bpy_type) for bpy_type in bpy_types])
    
    return script
    
def build_type_script(name, type):
    lines = []
    lines.append("class " + name + ":")
    lines.append("    def __init__(self):")
    for property in type.bl_rna.properties:
        lines.append("        self." + property.identifier + " = " + get_property_declaration(property))
    lines.append("        pass")
    for function in type.bl_rna.functions:
        lines.append("    def " + function.identifier + "({}):".format(get_function_parameter_list(function)))
        lines.append("        return " + get_function_return_list(function))
    if type.bl_rna.description.startswith("Collection"):
        element_type = "Object()"
        lines.append("""
    def get(self, key):
        return {}
    def __getitem__(self, key):
        return {}
    def __iter__(self):
        yield {}
    def __get__(self, key):
        return {}""".format(element_type, element_type, element_type, element_type))
    return "\n".join(lines)
    
def get_property_declaration(property):
    if property.type == "BOOLEAN": return "True"
    if property.type == "INT": return "0"
    if property.type == "STRING": return "''"
    if property.type == "COLLECTION":
        if property.srna is None: return "[{}()]".format(property.fixed_type.identifier)
        else: return property.srna.identifier + "()"
    if property.type == "FLOAT":
        if property.array_length <= 1: return "float()"
        if property.array_length == 2: return "mathutils.Vector()"
        if property.array_length == 3: return "mathutils.Vector()"
        if property.array_length == 16: return "mathutils.Matrix()"
    if property.type == "POINTER":
        return property.fixed_type.identifier + "()"
    return "''"
    
    
def get_function_parameter_list(function):
    parameters = ["self"] + [parameter.identifier for parameter in function.parameters if not parameter.is_output]
    return ", ".join(parameters)
    
def get_function_return_list(function):
    returns = [parameter for parameter in function.parameters if parameter.is_output]
    return ", ".join([get_property_declaration(parameter) for parameter in returns])
        