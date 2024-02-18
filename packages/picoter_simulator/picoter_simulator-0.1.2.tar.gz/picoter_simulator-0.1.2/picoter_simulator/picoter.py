from threading import Thread


class Picoter:
    def __init__(self, display, buttons):
        self.display = display
        self.buttons = buttons

    def start(self, mainfunc):
        Thread(target=mainfunc).run()
        self.display._start(self.buttons, mainfunc)
