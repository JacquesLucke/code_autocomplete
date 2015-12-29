import bpy
from mathutils import Vector

def get_mouse_region_position(event):
    return Vector((event.mouse_region_x, event.mouse_region_y))

def is_event(event, type, value = "PRESS", shift = False, ctrl = False, alt = False):
    if event.type in ("LEFT_SHIFT", "RIGHT_SHIFT"): shift = True
    if event.type in ("LEFT_CTRL", "RIGHT_CTRL"): ctrl = True
    if event.type in ("LEFT_ALT", "RIGHT_ALT"): alt = True
    if shift == "ANY": shift = event.shift
    if ctrl == "ANY": ctrl = event.ctrl
    if alt == "ANY": alt = event.alt

    return event.type == type and \
           event.value == value and \
           event.shift == shift and \
           event.ctrl == ctrl and \
           event.alt == alt

def is_event_in_list(event, types, value = "PRESS", shift = False, ctrl = False, alt = False):
    if not event.type in types: return
    return is_event(event, event.type, value, shift, ctrl, alt)

def is_mouse_click(event):
    return is_event_in_list(event, ("LEFTMOUSE", "RIGHTMOUSE"))

def get_area_under_event(event):
    for area in bpy.context.screen.areas:
        if is_event_over_area(event, area): return area
    return None

def is_event_over_area(event, area):
    for region in area.regions:
        if is_event_over_region(event, region): return True
    return False

def is_event_over_region(event, region):
    return region.x <= event.mouse_x <= region.x + region.width and \
           region.y <= event.mouse_y <= region.y + region.height
