import bpy
from .. graphics.rectangle import Rectangle
from . exception import BlockEvent
from . event_utils import is_event, get_area_under_event
from bgl import *


class AutocompleteHandler:
    def __init__(self):
        self.active_text_area = ActiveTextArea(bpy.context.area)
        
    def update(self, event):
        self.active_text_area.update(event)
        if is_event(event, "D"):
            raise BlockEvent()
        
    def draw(self):
        area = bpy.context.area
        if area == self.active_text_area.get():
            Rectangle(20, 50, 400, 100).draw()
    
    
class ActiveTextArea:
    def __init__(self, area):
        self.x = area.x
        self.y = area.y
        self.width = area.width
        self.height = area.height

    def get(self):
        return self.get_nearest_text_area()
        
    def update(self, event):
        if is_event(event, "LEFTMOUSE", "PRESS"):
            area = get_area_under_event(event)
            self.settings_from_area(area)
        else:
            nearest_area = self.get_nearest_text_area()
            self.settings_from_area(nearest_area)
        
    def settings_from_area(self, area):
        self.x = area.x
        self.y = area.y
        self.width = area.width
        self.height = area.height
        
    def get_nearest_text_area(self):
        differences = [(area, self.get_area_difference(area)) for area in bpy.context.screen.areas if area.type == "TEXT_EDITOR"]
        return min(differences, key = lambda x: x[1])[0]
            
    def get_area_difference(self, area):
        difference = 0
        difference += abs(area.x - self.x)
        difference += abs(area.y - self.y)
        difference += abs(area.width - self.width)
        difference += abs(area.height - self.height)
        return difference
        