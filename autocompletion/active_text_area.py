import bpy
from . event_utils import is_event, get_area_under_event

class ActiveTextArea:
    def __init__(self):
        self.x, self.y, self.width, self.height = 0, 0, 0, 0

    def set_area(self, area):
        if not area: return
        self.x = area.x
        self.y = area.y
        self.width = area.width
        self.height = area.height

    def get_text(self):
        area = self.get()
        if area:
            space = area.spaces[0]
            return getattr(space, "text", None)

    def get(self):
        area = self.get_nearest_text_area()
        if getattr(area, "type", "") == "TEXT_EDITOR": return area

    def update(self, event):
        if is_event(event, "LEFTMOUSE", "PRESS"):
            area = get_area_under_event(event)
            self.settings_from_area(area)
        else:
            nearest_area = self.get_nearest_text_area()
            self.settings_from_area(nearest_area)

    def settings_from_area(self, area):
        if not area: return
        self.x = area.x
        self.y = area.y
        self.width = area.width
        self.height = area.height

    def get_nearest_text_area(self):
        differences = [(area, self.get_area_difference(area)) for area in bpy.context.screen.areas if area.type == "TEXT_EDITOR"] + [(bpy.context.area, 10000)]
        return min(differences, key = lambda x: x[1])[0]

    def get_area_difference(self, area):
        difference = 0
        difference += abs(area.x - self.x)
        difference += abs(area.y - self.y)
        difference += abs(area.width - self.width)
        difference += abs(area.height - self.height)
        return difference
