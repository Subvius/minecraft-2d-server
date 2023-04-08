import datetime
from copy import deepcopy

import pygame
from pygame.locals import *
from lib.functions.drawing import draw_text


class Notification:
    def __init__(self, text: str, duration: int, window_size, position: str = "left", animation: str = "slide",
                 notification_type: str = "info", on_click=None):
        """
        Notification class. Displaying messages on the screen..

        :param text: Notification text
        :param duration: Duration of notification display. Provide -1 for infinite display
        :param position: Position on the screen. Default - left
        :param animation: Animation of notification popup. Default - slide
        :param notification_type: Type of the notification. Info | Warning | Danger
        """

        self.notification_type = notification_type
        self._colors = ["#272726", "#e9d75f", "#e8817c", ]
        self._types = ["info", "warning", "danger"]
        self.border_color = self._colors[self._types.index(self.notification_type.lower())]
        self.text = text
        self.on_click = on_click
        self.duration = duration
        self.is_disappearing = duration != -1
        self.position = position
        self.animation = animation
        self.show = False
        self.show_start = None
        self.window_size = window_size

        self.rect = pygame.Rect(self.window_size[0] - 310 - 10, 10, 310, 85)
        self.rect_before = deepcopy(self.rect)

    def toggle_visibility(self):
        self.show = not self.show
        self.show_start = datetime.datetime.now() if self.show else None
        self.rect = self.rect_before if self.show else self.rect

    def set_custom_color(self, color: any):
        self.border_color = color

    def show_window(self):
        self.show = True
        self.show_start = datetime.datetime.now()
        self.rect = pygame.Rect(self.window_size[0] - 310 - 10, 10, 310, 85)

    def _check_time(self):
        if self.is_disappearing:
            if (datetime.datetime.now() - self.show_start).seconds >= self.duration:
                if self.rect.x > self.window_size[0]:
                    self.toggle_visibility()
                else:
                    self.rect.x += 10

    def set_text(self, text: str):
        """
        Set's text for the notification
        :param text: New text to display
        :return: None
        """

        self.text = text

    def set_type(self, type: str):
        if type.lower() in self._types:
            self.border_color = self._colors[self._types.index(self.notification_type.lower())]
        else:
            self.border_color = self._colors[0]

    def on_event(self, events: list[pygame.event.Event]):
        for event in events:
            if event.type == MOUSEBUTTONDOWN:
                pos = event.pos
                if self.rect.collidepoint(*pos):
                    if self.on_click is not None:
                        self.on_click()

    def draw(self, surface: pygame.Surface, player):
        """
        Drawing notification on the given surface...

        :param surface: Surface to draw notification on
        :param player: Current player.
        :return: None
        """
        if self.show:
            pygame.draw.rect(surface, "#090707", self.rect, border_radius=8)
            pygame.draw.rect(surface, self.border_color, self.rect, width=2, border_radius=8)

            draw_text(self.text, (self.rect.topleft[0] + 10, 0), surface, player,
                      centery=self.rect.centery, width=self.rect.width - 20, fontsize=20)

            self._check_time()
