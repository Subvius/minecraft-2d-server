import json

import pygame


class Screen:
    def __init__(self):
        self.mouse_pos = (0, 0)
        self.hold_buttons = {
            "left": False,
            "right": False
        }
        self.screen = 'lobby'  # | game
        self.paused = False
        self.show_inventory = False
        self.show_players = False
        self.show_dialog = False
        self.dialog_action = '0'
        self.dialog = {}
        self.current_dialog = {}
        self.dialog_interlocutor = "mira"
        self.high_lighted_choice = None
        self.dialog_rects: list[pygame.Rect] = list()
        """Rects for choices"""

    def add_dialog_rect(self, rect: pygame.Rect):
        self.dialog_rects.append(rect)

    def reset_dialog_rects(self):
        self.dialog_rects = list()

    def get_show_inventory(self) -> bool:
        return self.show_inventory

    def start_dialog(self):
        self.show_dialog = True
        self.paused = True
        self.dialog_action = '0'
        with open("lib/storage/story_characters.json", "r") as f:
            data = json.load(f)

        self.dialog = data[self.dialog_interlocutor]["interact"]['actions']
        self.current_dialog = data[self.dialog_interlocutor]["interact"]['actions'][0]

    def close_dialog(self):
        self.show_dialog = False
        self.paused = False
        self.dialog_action = "0"
        self.current_dialog = {}
        self.reset_dialog_rects()

    def toggle_pause(self):
        self.paused = not self.paused

    def change_screen(self, screen: str):
        self.screen = screen

    def set_mouse_pos(self, pos: tuple[int, int]):
        self.mouse_pos = pos

        if self.show_dialog:
            picked = None
            for index, r in enumerate(self.dialog_rects):
                if r.collidepoint(*self.mouse_pos):
                    picked = index
                    break
            self.high_lighted_choice = picked

    def set_hold_button(self, button: str, value: bool):
        self.hold_buttons.update({button: value})

        if button == "left" and value:
            if self.show_dialog:
                picked = None
                for index, r in enumerate(self.dialog_rects):
                    if r.collidepoint(*self.mouse_pos):
                        picked = index
                        break
                if picked is not None:
                    answer = self.current_dialog['choices'][f"{picked + 1}"]
                    if answer.get('next', None) is not None:
                        self.dialog_action += f'-{picked}'
                        self.current_dialog = answer["next"]
                        self.reset_dialog_rects()
                    elif self.current_dialog.get("end", False):
                        self.close_dialog()
                    else:
                        self.dialog_action = f"{int(self.dialog_action.split('-')[0]) + 1}"
                        self.current_dialog = self.dialog[int(self.dialog_action)]
                        self.reset_dialog_rects()
