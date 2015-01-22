import bpy, inspect, re
from collections import defaultdict

class Documentation:
    def __init__(self):
        self.is_build = False
        self.reset()
        
    def build_if_necessary(self):
        if not self.is_build:
            self.build()
    
    def build(self):
        self.reset()
        all_bpy_types = inspect.getmembers(bpy.types)
        self.build_type_documentation(all_bpy_types)
        self.build_attribute_documentation(all_bpy_types)
        self.build_operator_documentation()
        self.add_custom_properties() 
        self.find_registered_menu_names()
        self.load_modules()
        self.categorize_data()
        self.is_build = True
        
    def reset(self):
        self.types = defaultdict(TypeDocumentation)
        self.functions = []
        self.functions_by_name = defaultdict(list)
        self.functions_by_owner = defaultdict(list)
        self.properties = []
        self.properties_by_name = defaultdict(list)
        self.properties_by_owner = defaultdict(list)
        self.operators = []
        self.operators_by_container = defaultdict(list)
        self.operators_by_full_name = {}
        self.menu_names = []
        self.is_build = False
        
    def build_type_documentation(self, bpy_types):
        for type in bpy_types:
            type_doc = self.get_documentation_of_type(type[1].bl_rna)
            self.types[type_doc.name] = type_doc
        
    def get_documentation_of_type(self, type):
        type_doc = TypeDocumentation(type.identifier)
        type_doc.description = type.description
        return type_doc
            
        
    def build_attribute_documentation(self, bpy_types):
        for type in bpy_types:
            self.build_attribute_lists_of_type(type[1])
              
    def build_attribute_lists_of_type(self, type):
        identifier = type.bl_rna.identifier
        
        for function in type.bl_rna.functions:
            function_doc = self.get_documentation_of_function(function, identifier)
            self.functions.append(function_doc)
            
        for property in type.bl_rna.properties:
            property_doc = self.get_documentation_of_property(property, identifier)
            self.properties.append(property_doc)
            
    def get_documentation_of_function(self, function, owner):
        function_doc = FunctionDocumentation(function.identifier)
        function_doc.description = function.description
        function_doc.owner = owner
        function_doc.inputs, function_doc.outputs = self.get_function_parameters(function)
        return function_doc
    
    def get_function_parameters(self, function):
        inputs = []
        outputs = []
        for parameter in function.parameters:
            parameter_doc = self.get_documentation_of_property(parameter, function.identifier)
            if parameter.is_output: outputs.append(parameter_doc)
            else: inputs.append(parameter_doc)
        return inputs, outputs
         
         
    def build_operator_documentation(self):
        container_names = dir(bpy.ops)
        for container_name in container_names:
            self.build_docs_for_container_name(container_name)
            
    def build_docs_for_container_name(self, container_name):
        container = getattr(bpy.ops, container_name)
        operator_names = dir(container)
        for operator_name in operator_names:
            self.build_doc_for_operator_name(container_name, container, operator_name)
            
    def build_doc_for_operator_name(self, container_name, container, operator_name):
        operator = getattr(container, operator_name)
        operator_rna = operator.get_rna().bl_rna
        inputs = self.get_operator_inputs(operator_rna)
        operator_doc = OperatorDocumentation(container_name, operator_name, operator_rna.description, inputs)
        self.operators.append(operator_doc)
        
    def get_operator_inputs(self, operator_rna):
        inputs = []
        for property in operator_rna.properties:
            if property.identifier != "rna_type":
                inputs.append(self.get_documentation_of_property(property, None))
        return inputs
            
    def get_documentation_of_property(self, property, owner):
        property_doc = PropertyDocumentation(property.identifier)
        property_doc.type = self.get_property_type(property)
        if property_doc.type == "Enum":
            property_doc.enum_items = self.get_enum_items(property)
        property_doc.description = property.description
        property_doc.is_readonly = property.is_readonly
        property_doc.owner = owner
        return property_doc
        
    def get_property_type(self, property):
        type = property.type
        
        if type == "POINTER":
            return property.fixed_type.identifier
        
        if type == "COLLECTION":
            srna = getattr(property, "srna", None)
            if srna is None: return "bpy_prop_collection"
            else: return srna.identifier
        
        if type in ["FLOAT", "INT", "STRING", "BOOLEAN"]:
            array_length = getattr(property, "array_length", 0)
            type_name = self.convert_to_nicer_type(type)
            if array_length <= 1: return type_name
            elif array_length <= 3: return type_name + " Vector " + str(array_length)
            else: return type_name + " Array " + str(array_length)
        
        if type == "ENUM":
            return "Enum"
        
        return None
    
    def get_enum_items(self, enum_property):
        items = []
        for item in enum_property.enum_items:
            items.append(item.identifier)
        return items
    
    def convert_to_nicer_type(self, type):
        if type == "INT": return "Integer"
        if type == "FLOAT": return "Float"
        if type == "BOOLEAN": return "Boolean"
        if type == "STRING": return "String"
        
    def load_modules(self):
        for name in ["bgl", "blf", "re", "bmesh", "mathutils", "random"]:
            self.load_module(name)

    def load_module(self, module_name):
        names = self.get_attribute_names_in_module(module_name)
        for name in names:
            self.properties.append(PropertyDocumentation(name, type = "", owner = module_name))
        self.properties.append(PropertyDocumentation(module_name, type = module_name, owner = None))
        
    def get_attribute_names_in_module(self, module_name):
        code = "import " + module_name + "\n"
        code += "names = dir(" + module_name + ")"
        names = []
        try:
            dic = {}
            exec(code, dic)
            names = [name for name in dic["names"] if not name.startswith("_")]
        except: pass
        return names
    
    # have to do this manually, because these properties aren't available everywhere
    def add_custom_properties(self):
        props = self.properties
        
        props.append(PropertyDocumentation("data", type = "BlendData", is_readonly = True, owner = None))
        props.append(PropertyDocumentation("kmi", type = "KeyMapItem", owner = None))
        props.append(PropertyDocumentation("context", type = "Context", is_readonly = True, owner = None))
        
        context_prop_data = [
            ("visible_objects", "Object Sequence"),
            ("visible_bases", "ObjectBase Sequence"),
            ("selectable_objects", "Object Sequence"),
            ("selectable_bases", "ObjectBase Sequence"),
            ("selected_objects", "Object Sequence"),
            ("selected_editable_objects", "Object Sequence"),
            ("selected_editable_bases", "ObjectBase Sequence"),
            ("visible_bones", "EditBone Sequence"),
            ("editable_bones", "EditBone Sequence"),
            ("selected_bones", "EditBone Sequence"),
            ("selected_editable_bones", "EditBone Sequence"),
            ("visible_pose_bones", "PoseBone Sequence"),
            ("selected_pose_bones", "PoseBone Sequence"),
            ("active_bone", "EditBone"),
            ("active_pose_bone", "PoseBone"),
            ("active_base", "ObjectBase"),
            ("active_object", "Object"),
            ("object", "Object"),
            ("edit_object", "Object"),
            ("sculpt_object", "Object"),
            ("vertex_paint_object", "Object"),
            ("weight_paint_object", "Object"),
            ("image_paint_object", "Object"),
            ("particle_edit_object", "Object"),
            ("sequences", "Sequence Sequence"),
            ("selected_sequences", "Sequence Sequence"),
            ("selected_editable_sequences", "Sequence Sequence"),
            ("gpencil_data", "GreasePencil"),
            ("gpencil_data_owner", "ID"),
            ("visible_gpencil_layers", "GPencilLayer Sequence"),
            ("editable_gpencil_layers", "GPencilLayer Sequence"),
            ("editable_gpencil_strokes", "GPencilStroke Sequence"),
            ("active_gpencil_layer", "GPencilLayer Sequence"),
            ("active_gpencil_frame", "GPencilLayer Sequence"),
            ("active_operator", "Operator"),
            ("texture_slot", "MaterialTextureSlot"),
            ("world", "World"),
            ("mesh", "Mesh"),
            ("armature", "Armature"),
            ("lattice", "Lattice"),
            ("curve", "Curve"),
            ("meta_ball", "MetaBall"),
            ("lamp", "Lamp"),
            ("speaker", "Speaker"),
            ("camera", "Camera"),
            ("material", "Material"),
            ("material_slot", "MaterialSlot"),
            ("texture", "Texture"),
            ("texture_user", "ID"),
            ("texture_user_property", "Property"),
            ("bone", "Bone"),
            ("edit_bone", "EditBone"),
            ("pose_bone", "Posebone"),
            ("particle_system", "ParticleSystem"),
            ("particle_system_editable", "ParticleSystem"),
            ("particle_settings", "ParticleSettings"),
            ("cloth", "ClothModifier"),
            ("soft_body", "SoftBodyModifier"),
            ("fluid", "FluidSimulationModifier"),
            ("smoke", "SmokeModifier"),
            ("collision", "CollisionModifier"),
            ("brush", "Brush"),
            ("dynamic_paint", "DynamicPaintModifier"),
            ("line_style", "FreestyleLineStyle"),
            ("edit_image", "Image"),
            ("edit_mask", "Mask"),
            ("selected_nodes", "Node Sequence"),
            ("active_node", "Node"),
            ("edit_text", "Text"),
            ("edit_movie_clip", "MovieClip"),
            ("edit_mask", "Mask") ]
            
        for prop_name, prop_type in context_prop_data:
            props.append(PropertyDocumentation(prop_name, type = prop_type, owner = "Context", is_readonly = True))
        
        space_subclass_names = [subclass.__name__ for subclass in bpy.types.Space.__subclasses__()]
        for space_name in space_subclass_names:
            props.append(PropertyDocumentation("space", type = space_name))
            props.append(PropertyDocumentation("space_data", type = space_name))
        
        props.append(PropertyDocumentation("event", type = "Event", is_readonly = True))
        for element in ("row", "col", "box", "subrow", "subcol", "subbox", "pie"):
            props.append(PropertyDocumentation(element, type = "UILayout"))
            
    def find_registered_menu_names(self):
        classes = bpy.types.Menu.__subclasses__()
        for cl in classes:
            self.menu_names.append(self.get_name_of_menu_class(cl))
            
    def get_name_of_menu_class(self, menu_class):
        text = str(menu_class)
        match = re.search("\.(?!.*\.)(\w*)", text)
        return match.group(1)
    
    def categorize_data(self):
        for property in self.properties:
            self.properties_by_name[property.name].append(property)
            self.properties_by_owner[property.owner].append(property)
            
        for functions in self.functions:
            self.functions_by_name[functions.name].append(functions)
            self.functions_by_owner[functions.owner].append(functions)
            
        for operator in self.operators:
            self.operators_by_container[operator.container_name].append(operator)
            self.operators_by_full_name[operator.container_name + "." + operator.name] = operator
            
    # attribute methods
    def get_possible_subattributes_of_property(self, property_name):
        attributes = []
        attributes.extend(self.get_possible_subproperties_of_property(property_name))
        attributes.extend(self.get_possible_subfunctions_of_property(property_name))
        return attributes
        
    def get_best_matching_subattributes_of_path(self, path):
        types = self.get_best_matching_types_of_path(path)
        attributes = []
        for type in types:
            attributes.extend(self.get_attributes_of_type(type))
        return attributes
        
    def get_best_matching_types_of_path(self, path):
        attributes = self.get_best_matching_attributes_of_path(path)
        return list(set([attribute.type for attribute in attributes]))
    
    # "context.active_object.modifiers" -> Object.modifiers (instead of SequenceModifiers, etc.)    
    def get_best_matching_attributes_of_path(self, path):
        attribute_names = path.split(".")
        best_attributes = set(self.get_properties_by_name(attribute_names[-1]))
        for i in range(len(attribute_names)):
            first_name = attribute_names[i]
            attributes_behind = attribute_names[i+1:]
            attributes = set()
            for attribute in self.get_attributes_by_name(first_name):
                attributes.update(self.get_matching_attributes_for_child(attribute, attributes_behind))
            if len(attributes) > 0:
                best_attributes = attributes
                break
        return list(best_attributes)
    # this is recursive        
    def get_matching_attributes_for_child(self, attribute, attribute_names_behind):
        if len(attribute_names_behind) == 0:
            return [attribute]
        else:
            if isinstance(attribute, FunctionDocumentation): return []
            attributes = []
            property = attribute
            type = property.type
            first_name = attribute_names_behind[0]
            attributes_behind = attribute_names_behind[1:]
            for attr in self.get_attributes_of_type(type):
                if attr.name == first_name:
                    attributes.extend(self.get_matching_attributes_for_child(attr, attributes_behind))
            return attributes
        
    def get_attributes_by_name(self, attribute_name):
        return self.get_properties_by_name(attribute_name) + self.get_functions_by_name(attribute_name)
    
    def get_attributes_of_type(self, attribute_name):
        return self.get_properties_of_type(attribute_name) + self.get_functions_of_type(attribute_name)
    
    # property methods
    def get_possible_subproperty_names_of_property(self, property_name):
        return list(set([property.name for property in self.get_subproperties_of_property(property_name)]))   
            
    def get_possible_subproperties_of_property(self, property_name):
        properties = []
        for type in self.get_possible_type_names_for_property(property_name):
            properties.extend(self.get_properties_of_type(type))
        return properties
            
    def get_types_with_property(self, property_name):
        return [property.owner for property in self.properties_by_name[property_name]]    

    def get_property_names_of_type(self, type_name):
        return [property.name for property in self.get_properties_of_type(type_name)]
    
    def get_properties_of_type(self, type_name):
        return self.properties_by_owner[type_name]
    
    def get_type_description(self, type_name):
        return self.types[type_name].description
    
    def get_possible_type_names_for_property(self, property_name):
        return list(set([property.type for property in self.get_properties_by_name(property_name)]))
    
    def get_descriptions_for_property(self, property_name):
        return list(set(property.description for property in self.get_properties_by_name(property_name)))
    
    def get_properties_by_name(self, property_name):
        return self.properties_by_name[property_name]
        
    # function methods    
    def get_possible_subfunctions_of_property(self, property_name):
        functions = []
        for type in self.get_possible_type_names_for_property(property_name):
            functions.extend(self.get_functions_of_type(type))
        return functions
        
    def get_function_names_of_type(self, type_name):
        return [function.name for function in self.get_functions_of_type(type_name)]
    
    def get_functions_of_type(self, type_name):
        return self.functions_by_owner[type_name]
        
    def get_functions_by_name(self, function_name):
        return self.functions_by_name[function_name]
        
    # operator methods
    def get_operator_container_names(self):
        return [container_name for container_name in self.operators_by_container.keys()]
        
    def get_operator_names_in_container(self, container_name):
        return [operator.name for operator in self.get_operators_in_container(container_name)]
        
    def get_operators_in_container(self, container_name):
        return self.operators_by_container[container_name]
        
    def get_operator_by_full_name(self, full_name):
        if "bpy.ops." in full_name:
            full_name = full_name[8:]
        return self.operators_by_full_name.get(full_name, None)
        
    # menu methods
    def get_menu_names(self):
        if len(self.menu_names) == 0:
            self.find_registered_menu_names()
        return self.menu_names
              
        
class PropertyDocumentation:
    def __init__(self, name = "", description = "", type = None, owner = None, is_readonly = False, enum_items = []):
        self.name = name
        self.description = description
        self.type = type
        self.owner = owner
        self.is_readonly = is_readonly
        self.enum_items = enum_items
        
    def __repr__(self):
        if self.owner is None: return self.name
        return self.owner + "." + self.name
        
        
class FunctionDocumentation:
    type = "Function"
    def __init__(self, name = "", description = "", owner = None, inputs = [], outputs = []):
        self.name = name
        self.description = description
        self.owner = owner
        self.inputs = inputs
        self.outputs = outputs
        
    def get_input_names(self):
        return [input.name for input in self.inputs]
    def get_output_names(self):
        return [output.name for output in self.outputs]
   
    def __repr__(self):
        output_names = ", ".join(self.get_output_names())
        if output_names != "": output_names = " -> " + output_names
        function_string = self.name + "(" + ", ".join(self.get_input_names()) + ")" + output_names
        if self.owner is None: return function_string
        else: return self.owner + "." + function_string
        
        
class TypeDocumentation:
    def __init__(self, name = "", description = ""):
        self.name = name
        self.description = description 

    def __repr__(self):
        return self.name
        
class OperatorDocumentation:
    def __init__(self, container_name = "", name = "", description = "", inputs = []):
        self.container_name = container_name
        self.name = name
        self.description = description
        self.inputs = inputs
        
    def get_input_names(self):
        return [input.name for input in self.inputs]
        
    def __repr__(self):
        return self.container_name + "." + self.name
        
class WordDescription:
    def __init__(self, word, description):
        self.word = word
        self.description = description        
        
        
documentation = Documentation()
def get_documentation():
    global documentation
    return documentation