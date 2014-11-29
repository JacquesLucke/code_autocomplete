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