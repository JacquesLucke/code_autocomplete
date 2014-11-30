def get_before_after_pairs():
    return pairs

pairs = {}
pairs["bpy"] = ("context", "data", "ops", "types", "utils", "path", "app", "props")
pairs["data"] = ("actions", "armatures", "brushes", "cameras", "curves", "filepath", "fonts", "grease_pencil", "groups", "images", "is_dirty", "is_saved", "lamps", "lattices", 
    "libraries", "linestyles", "masks", "materials", "meshes", "metaballs", "movieclips", "node_groups", "objects", "particles", "scenes", "screens", "scripts", "shape_keys",
    "sounds", "speakers", "texts", "textures", "use_autopack", "window_manager", "worlds")
pairs["types"] = ("Panel", "Operator", "Menu")
pairs["context"] = ("active_object", "selected_objects", "scene", "world", "mesh", "material")

layout = ("row", "column", "box", "split", "prop", "prop_search", "prop_enum", "prop_menu_enum", "operator", "operator_enum", "operator_menu_enum", "label", "menu", "separator")
layout_element = layout + ("scale_x", "scale_y")
pairs["layout"] = layout
pairs["row"] = layout_element
pairs["col"] = layout_element
pairs["box"] = layout_element