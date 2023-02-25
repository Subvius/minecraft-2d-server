import datetime

import pygame
from lib.functions.drawing import draw_text


class ActionBar:
    def __init__(self, text: str, duration: int, position: str = "bottom"):
        """
        Showing text (above health bar. Can be adjusted)

        :param text: Text to display
        :param duration: Duration of showing action bar. In seconds
        :param position: Relative position on the screen. Default - bottom
        """

        self.text = text
        self.duration = duration
        self.position = position
        self.hidden = True
        self.start_time = None

    def show(self):
        self.hidden = False
        self.start_time = datetime.datetime.now()

    def hide(self):
        self.hidden = True
        self.start_time = None

    def check_time(self):
        if (datetime.datetime.now() - self.start_time).seconds >= self.duration:
            self.hide()

    def render(self, surface: pygame.Surface, player):
        if not self.hidden:
            if self.position == "bottom":
                draw_text(self.text, (surface.get_width() // 2, surface.get_height() - 70), surface, player,
                          centerx=surface.get_width() // 2, width=300, scolor="black", shadow=(1.0, 1.0))

            elif self.position == "top":
                draw_text(self.text, (surface.get_width() // 2, 70), surface, player,
                          centerx=surface.get_width() // 2, width=300, scolor="black", shadow=(0, 1.0))

            self.check_time()
