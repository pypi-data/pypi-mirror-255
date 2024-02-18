class Button:
    def __init__(self, text):
        self._pressed = False
        self._text = text

    def _set_pressed(self, pressed):
        self._pressed = pressed

    def pressed(self):
        return self._pressed
