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
        
    def get_inset_rectangle(self, border):
        return Rectangle(self.left + border, self.top - border, self.width - 2*border, self.height - 2*border)