import bpy
import re
from mathutils import Vector
from . exception import BlockEvent
from . suggestions import complete
from .. settings import get_preferences
from .. graphics.text_box import TextBox
from .. graphics.utils import getDpiFactor
from .. graphics.list_box import ListItem, ListBox
from . event_utils import (is_event, is_event_in_list,
                           is_mouse_click, get_mouse_region_position,
                           is_event_over_area)

move_index_commands = {
    "DOWN_ARROW" : 1,
    "UP_ARROW" : -1,
    "PAGE_DOWN" : 4,
    "PAGE_UP" : -4,
    "END" : 10000,
    "HOME" : -10000 }

def is_event_changing_the_text(event):
    if len(event.unicode) > 0: return True
    if is_event_in_list(event, ["BACK_SPACE", "RET", "DEL"], "PRESS"): return True
    return False

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

        if is_event_changing_the_text(event):
            self.reload_completions = True

        if self.completions_amount > 0:
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

        if self.completions_amount == 0: return
        if self.is_hidden: return
        insert_with_keyboard()
        insert_with_mouse()

    def insert_completion(self, text_block, completion):
        completion.insert(text_block)
        if completion.finished_statement: self.hide()
        self.active_index = 0

    def update_visibility(self, event, text_block):
        if is_mouse_click(event):
            return self.hide()

        if is_event(event, "ESC", shift = True):
            return self.show()

        # open after removing after . or ' or "
        if is_event_in_list(event, ["BACK_SPACE", "DEL"], "PRESS"):
            line = text_block.text_before_cursor
            if len(line) > 0:
                if line[-1] in "\"\'.":
                    return self.show()

        if is_event_in_list(event, ["BACK_SPACE", "DEL", "ESC", "RET", "LEFT_ARROW", "RIGHT_ARROW"], "PRESS"):
            return self.hide()

        char = event.unicode.lower()
        if len(char) > 0 and not event.alt:
            if char in "abcdefghijklmnopqrstuvwxyz0123456789_({[\\/=@.":
                return self.show()
            if char in ":":
                return self.hide()

            # open with string declaration start and close with its end
            line = text_block.text_before_cursor
            if char in "\"":
                if line.count("\"") % 2 == 0: return self.show()
                else: return self.hide()
            if char in '\'':
                if line.count('\'') % 2 == 0: return self.show()
                else: return self.hide()

        # open with space in import statement and after comma
        if is_event(event, "SPACE"):
            line = text_block.text_before_cursor
            if re.search("(import|from)\s*\.?\s*$", line) or re.search("(,|=)\s*$", line):
                return self.show()
            else:
                return self.hide()

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
        self.active_index += amount
        self.correct_selection_indices()

    def update_completions(self, text_block):
        self.completions = complete(text_block)
        self.correct_selection_indices()

    def correct_selection_indices(self):
        index = self.active_index
        if index < 0:
            index = 0
        if index >= self.completions_amount:
            index = self.completions_amount - 1
        if index < self.top_index:
            self.top_index = index
        if index > self.bottom_index:
            self.top_index = index - self.draw_max + 1
        if self.completions_amount < self.draw_max:
            self.top_index = 0
        self.active_index = index


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
            item.offset = 10 * getDpiFactor() if c.type.endswith("PARAMETER") else 0
            items.append(item)
        return items

    @property
    def completions_amount(self):
        return len(self.completions)

    @property
    def bottom_index(self):
        return self.top_index + self.draw_max - 1


class ContextUI:
    def __init__(self):
        self.context_box = ListBox()
        self.description_box = TextBox()

    def update_settings(self):
        settings = get_preferences()

        s = settings.context_box
        self.context_box.font_size = s.font_size
        self.context_box.line_height = s.line_height * getDpiFactor()
        self.context_box.width = s.width * getDpiFactor()
        self.context_box.padding = s.padding * getDpiFactor()

        s = settings.description_box
        self.description_box.font_size = s.font_size
        self.description_box.line_height = s.line_height * getDpiFactor()
        self.description_box.padding = s.padding * getDpiFactor()

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
