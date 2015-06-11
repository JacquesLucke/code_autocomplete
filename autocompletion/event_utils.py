import bpy

def is_event(event, type, value = "PRESS", shift = False, ctrl = False, alt = False):
    if event.type in ("LEFT_SHIFT", "RIGHT_SHIFT"): shift = True
    if event.type in ("LEFT_CTRL", "RIGHT_CTRL"): ctrl = True
    if event.type in ("LEFT_ALT", "RIGHT_ALT"): alt = True
    
    return event.type == type and \
           event.value == value and \
           event.shift == shift and \
           event.ctrl == ctrl and \
           event.alt == alt
           
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