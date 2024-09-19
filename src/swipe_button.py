class SwipeButton:
    button = ""
    swipe_right, swipe_left, swipe_up, swipe_down, click = [], [], [], [], []
    freeze, scroll, moved = False, False, False
    
    pressed = 0
    deltaX, deltaY = 0, 0
    delta = 0

    def __init__(self, button):
        self.button = button
