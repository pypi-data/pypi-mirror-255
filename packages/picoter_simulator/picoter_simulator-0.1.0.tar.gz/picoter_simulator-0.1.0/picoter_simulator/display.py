import pygame
import thorpy as tp


class Display:
    def __init__(self, width, height):
        self._tpbuttons = []

        self.width = width
        self.height = height
        # A scale is calculated, so that the window isn't tiny if a low resolution
        # display is being used
        targetsize = (960, 540)
        scale = (targetsize[0] / width, targetsize[1] / height)
        # we don't want to strech anything, but the content should fit on the
        # screen, so we use the smaller scale (horizontal / vertical)
        self._scale = round(min(scale), 0)

        pygame.init()
        self._init_screen()

    def _change_scale(self, **params):
        self._scale += params["by"]

        self._init_screen()
        self._update_positioning()

    def _init_screen(self):
        self._scaled_width = self.width * self._scale
        self._scaled_height = self.height * self._scale

        self._screen = pygame.display.set_mode(
            (self._scaled_width, self._scaled_height)
        )
        tp.init(self._screen)  # bind screen to gui elements

    def _update_ui(self):
        self._scale_inc_button = tp.Button("Scale +")
        self._scale_inc_button.at_unclick_params = {"by": 1}
        self._scale_inc_button.at_unclick = self._change_scale
        self._scale_dec_button = tp.Button("Scale -")
        self._scale_dec_button.at_unclick_params = {"by": -1}
        self._scale_dec_button.at_unclick = self._change_scale

        self._group = tp.Group([self._scale_inc_button, self._scale_dec_button])

        for b in self._buttons:
            tpbtn = tp.Button(b._text)
            tpbtn._at_click = b._set_pressed
            tpbtn._at_click_params = {"pressed": True}
            tpbtn.at_unclick = b._set_pressed
            tpbtn.at_unclick_params = {"pressed": False}
            self._tpbuttons.append(tpbtn)
            self._group.add_child(tpbtn)

    def _update_positioning(self):
        self._scale_inc_button.set_bottomright(
            self._scaled_width - 10, self._scaled_height - 10
        )
        self._scale_dec_button.set_bottomright(
            self._scaled_width - 110, self._scaled_height - 10
        )

        for i, b in enumerate(self._tpbuttons):
            b.set_bottomleft(100 * i, self._scaled_height - 10)

    def _start(self, buttons, mainfunc):
        self._buttons = buttons
        self._update_ui()
        self._update_positioning()

        # For the sake of brevity, the main loop is replaced here by a shorter but blackbox-like method
        tp.call_before_gui(mainfunc)
        self._group.get_updater().launch()
        pygame.quit()

    def fill(self, color):
        self._screen.fill(color)

    def drawRect(self, color, x, y, w, h):
        pygame.draw.rect(self._screen, color, ((x, y), (w, h)))
