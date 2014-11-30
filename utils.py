def clamp(value, min_value, max_value):
    return min(max(value, min_value), max_value)

class Rectangle:
    # (x, y) is the top left corner
    def __init__(self, x, y, width, height):
        self.left = x
        self.right = x + width
        self.top = y
        self.bottom = y - height
        
    def move_down(self, amount):
        self.top -= amount
        self.bottom -= amount
        
    @property
    def width(self):
        return self.right - self.left
    @property
    def height(self):
        return self.top - self.bottom
        
    @property
    def center(self):
        return [(self.left+self.right) / 2, (self.top+self.bottom) / 2]
        
    def contains(self, x, y):
        return self.left <= x <= self.right and self.top >= y >= self.bottom
        
    def get_inset_rectangle(self, border):
        return Rectangle(self.left + border, self.top - border, self.width - 2*border, self.height - 2*border)