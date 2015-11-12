import bpy
import re
from mathutils import Vector
from .. graphics.list_box import ListItem, ListBox
from .. graphics.text_box import TextBox
from . exception import BlockEvent
from . event_utils import is_event, is_event_in_list, is_mouse_click, get_mouse_region_position, is_event_over_area
from . suggestions import complete
from .. settings import get_preferences
import time

move_index_commands = {
    "DOWN_ARROW" : 1,
    "UP_ARROW" : -1,
    "PAGE_DOWN" : 4,
    "PAGE_UP" : -4,
    "END" : 10000,
    "HOME" : -10000 }

text_changing_types = ["BACK_SPACE", "SPACE", "COMMA", "RET", "DEL",
    "SEMI_COLON", "MINUS", "RIGHT_BRACKET", "LEFT_BRACKET", "SLASH"]

statement_chars = "abcdefghijklmnopqrstuvwxyz0123456789_."

hide_types = ["BACK_SPACE", "DEL", "ESC", "RET"]


class AutocompleteHandler:
    def __init__(self):
        self.context_ui = ContextUI()
        self.completions = []
        self.draw_max = 8
        self.top_index = 0
        self.active_index = 0
        self.reload_completions = False
        self.hide()

    def update(self, event, text_block, area):
        if not is_event_over_area(event, area): return
        self.update_settings()
        self.check_event_for_insertion(event, text_block)
        self.update_visibility(event, text_block)
        if self.is_hidden: return

        char = event.unicode.lower()
        if char == "": char = "empty"
        if is_event_in_list(event, text_changing_types, "PRESS") or char in statement_chars:
            self.reload_completions = True

        if len(self.completions) > 0:
            self.move_active_index(event)

    def update_settings(self):
        self.draw_max = get_preferences().context_box.lines

    def check_event_for_insertion(self, event, text_block):
        def insert_with_keyboard():
            if is_event_in_list(event, ("TAB", "RET")):
                self.insert_completion(text_block, self.completions[self.active_index])
                raise BlockEvent()

        def insert_with_mouse():
            if not is_event(event, "LEFTMOUSE"): return
            item = self.context_ui.get_item_under_event(event)
            if item:
                self.insert_completion(text_block, item.data)
                raise BlockEvent()

        if len(self.completions) == 0: return
        if self.is_hidden: return
        insert_with_keyboard()
        insert_with_mouse()

    def insert_completion(self, text_block, completion):
        completion.insert(text_block)
        self.hide()
        self.active_index = 0

    def update_visibility(self, event, text_block):
        char = event.unicode.lower()
        if char == "": char = "empty"
        if self.is_hidden:
            if char in statement_chars: self.show()
            if char == "(": self.show()
            if is_event(event, "ESC", shift = True): self.show()
        else:
            if is_event_in_list(event, hide_types, "PRESS"): self.hide()
            if not (char in statement_chars or char == "empty"): self.hide()

        text = text_block.text_before_cursor
        if is_event(event, "SPACE"):
            if re.search("(import|from)\s*\.?\s*$", text): self.show()
            else: self.hide()

        if is_mouse_click(event): self.hide()

    def show(self):
        if self.is_hidden:
            self.is_hidden = False
            self.reload_completions = True

    def hide(self):
        self.is_hidden = True

    def move_active_index(self, event):
        def move_with_keyboard():
            for key, amount in move_index_commands.items():
                if is_event(event, key):
                    self.change_active_index(amount)
                    raise BlockEvent()
        def move_with_mouse():
            if not self.context_ui.event_over_context_box(event): return
            if is_event(event, "WHEELUPMOUSE"):
                self.change_active_index(-1)
                raise BlockEvent()
            if is_event(event, "WHEELDOWNMOUSE"):
                self.change_active_index(1)
                raise BlockEvent()
        move_with_keyboard()
        move_with_mouse()

    def change_active_index(self, amount):
        index = self.active_index + amount
        index = min(max(index, 0), len(self.completions) - 1)
        if index < self.top_index:
            self.top_index = index
        if index > self.top_index + self.draw_max - 1:
            self.top_index = index - self.draw_max + 1
        if len(self.completions) < self.draw_max:
            self.top_index = 0
        self.active_index = index

    def update_completions(self, text_block):
        self.completions = complete(text_block)
        self.change_active_index(0)

    def draw(self, text_block):
        if self.is_hidden: return

        if self.reload_completions:
            self.update_completions(text_block)
            self.reload_completions = False

        items = self.get_display_items()
        self.context_ui.update_settings()
        self.context_ui.insert_items(items)
        self.context_ui.draw(text_block)

    def get_display_items(self):
        items = []
        for i, c in enumerate(self.completions):
            if not self.top_index <= i < self.top_index + self.draw_max: continue
            item = ListItem(c.name)
            item.active = self.active_index == i
            item.data = c
            item.offset = 10 if c.type == "PARAMETER" else 0
            items.append(item)
        return items


class ContextUI:
    def __init__(self):
        self.context_box = ListBox()
        self.description_box = TextBox()

    def update_settings(self):
        settings = get_preferences()

        s = settings.context_box
        self.context_box.font_size = s.font_size
        self.context_box.line_height = s.line_height
        self.context_box.width = s.width
        self.context_box.padding = s.padding

        s = settings.description_box
        self.description_box.font_size = s.font_size
        self.description_box.line_height = s.line_height
        self.description_box.padding = s.padding

    def insert_items(self, items):
        self.context_box.items = items
        active_item = self.get_active_item()
        if active_item: self.description_box.text = active_item.data.description
        else: self.description_box.text = ""

    def get_active_item(self):
        for item in self.context_box.items:
            if item.active: return item

    def draw(self, text_block):
        cursor = text_block.current_cursor_region_location
        self.context_box.position = cursor.copy()
        self.description_box.position = cursor + Vector((self.context_box.width + 10, 0))

        if len(self.context_box.items) > 0:
            self.context_box.draw()
            if len(self.description_box.text) > 0:
                self.description_box.draw()

    def event_over_context_box(self, event):
        point = get_mouse_region_position(event)
        return self.context_box.contains(point)

    def get_item_under_event(self, event):
        point = get_mouse_region_position(event)
        return self.context_box.get_item_under_point(point)
