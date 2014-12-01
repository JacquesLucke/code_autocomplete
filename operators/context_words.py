def get_before_after_pairs():
    return pairs

pairs = {}
pairs["bpy"] = ("context", "data", "ops", "types", "utils", "path", "app", "props")
pairs["types"] = ("Panel", "Operator", "Menu")
pairs["context"] = ("active_object", "selected_objects", "scene", "world", "mesh", "material")
pairs["props"] = ("BoolProperty", "BoolVectorProperty", "CollectionProperty", "EnumProperty", "FloatProperty", "FloatVectorProperty", "IntProperty", "IntVectorProperty", "PointerProperty", "RemoveProperty", "StringProperty")

layout = ("row", "column", "box", "split", "prop", "prop_search", "prop_enum", "prop_menu_enum", "operator", "operator_enum", "operator_menu_enum", "label", "menu", "separator")
layout_element = layout + ("scale_x", "scale_y")
pairs["layout"] = layout
pairs["row"] = layout_element
pairs["col"] = layout_element
pairs["box"] = layout_element