import datetime
import json

import pygame
from lib.functions.drawing import draw_text
from lib.models.action_bar import ActionBar


class Screen:
    def __init__(self):
        self.mouse_pos = (0, 0)
        self.hold_buttons = {
            "left": False,
            "right": False
        }
        self.screen = 'lobby'  # | game
        self.location = None  # | house | some castle area etc.
        self.paused = False
        self.show_inventory = False
        self.show_players = False
        self.show_dialog = self.show_rep = self.show_tasks = False
        self.dialog_action = '0'
        self.dialog = {}
        self.current_dialog = {}
        self.dialog_interlocutor = "mira"
        self.high_lighted_choice = None
        self.dialog_rects: list[pygame.Rect] = list()
        """Rects for choices"""

        self.phase_index, self.stage = self.get_phase()
        self.story_data, self.phase = self.get_story()
        self.timer_start = None
        self.wait_for_dialog_end = False
        self.story_world_pos = (0, 0)

        self.action_bar: ActionBar = None

    def get_story(self):
        with open("lib/storage/story.json", "r", encoding="utf-8") as f:
            data = json.load(f)

        return data, data.get(f"phase{self.phase_index}", None)

    def render_action_bar(self, surface: pygame.Surface, player):
        if self.action_bar is not None:
            self.action_bar.render(surface, player)

    def set_action_bar(self, text: str, duration: int, position: str = "bottom"):
        self.action_bar = ActionBar(text, duration, position)
        self.action_bar.show()

    def remove_action_bar(self):
        self.action_bar = None

    @staticmethod
    def get_phase():
        with open("lib/storage/phase_details.json", "r", encoding="utf-8") as f:
            data = json.load(f)

        return data.get("phase", 1), data.get("phase_stage", 0)

    def update_phase(self):
        with open("lib/storage/phase_details.json", "w", encoding="utf-8") as f:
            json.dump({
                "phase": self.phase_index,
                "phase_stage": self.stage
            }, f)

    @staticmethod
    def edit_characters(key, field, value):
        with open("lib/storage/story_characters.json", "r", encoding="utf-8") as f:
            data: dict = json.load(f)

        data[key][field] = value

        with open("lib/storage/story_characters.json", "w") as f:
            json.dump(data, f)

    def next_stage(self, actions):
        self.stage += 1
        if self.stage >= len(actions):
            self.stage = 0
            self.phase_index += 1
            self.story_data, self.phase = self.get_story()
        self.update_phase()

    def story(self, player, npcs: list):
        if self.screen == "abyss" and self.phase is not None:
            current_stage = self.phase
            actions = current_stage.get("actions", [{}])

            current_action = actions[self.stage]
            now = datetime.datetime.now()
            if current_action.get("title", None) is not None:
                title = current_action.get("title")
                if title.get("show", False):
                    text = title.get("text")
                    surf = pygame.display.get_surface()
                    surf.fill("black")
                    draw_text(text, centerx=surf.get_width() // 2, centery=surf.get_height() // 2, color="white",
                              scolor="#404040", shadow=(1.0, 1.0), player=player,
                              pos=(surf.get_width() // 2, surf.get_height() // 2), surf=surf)

                    if self.timer_start is None:
                        self.timer_start = now
                    elif now - self.timer_start >= datetime.timedelta(seconds=title.get("time")):
                        self.next_stage(actions)
                        self.timer_start = None
            elif current_action.get("edit", None) is not None and not self.wait_for_dialog_end:
                edit = current_action.get("edit")
                key = edit.get("key")
                field = edit.get("field")
                value = edit.get("value")
                self.edit_characters(key, field, value)
                if field == "interact" and type(value) == dict and value.get("can", False):
                    self.wait_for_dialog_end = True
                else:
                    self.next_stage(actions)
                    return key, field, value
            elif current_action.get("wait", None) is not None:
                wait = current_action.get("wait")
                if self.timer_start is None:
                    self.timer_start = now
                elif now - self.timer_start >= datetime.timedelta(seconds=wait.get("time")):
                    self.next_stage(actions)
                    self.timer_start = None
            elif current_action.get("wait_for", None) is not None:
                wait_for = current_action.get("wait_for")
                key = wait_for.get("key")
                field = wait_for.get("field")
                event = wait_for.get("event")
                if event.get("type") == "equal-to":
                    for npc in npcs:
                        if npc.name.lower() == key.lower():
                            fields = []
                            for el in event.get("fields"):
                                fields.append(eval(f"npc.{el}"))
                            if fields == eval(f"npc.{field}") or (field == "destination" and npc.destination is None):
                                self.next_stage(actions)
        return None, None, None

    def add_dialog_rect(self, rect: pygame.Rect):
        self.dialog_rects.append(rect)

    def reset_dialog_rects(self):
        self.dialog_rects = list()

    def get_show_inventory(self) -> bool:
        return self.show_inventory

    def set_story_world_pos(self, pos):
        self.story_world_pos = pos

    def start_dialog(self):
        self.show_dialog = True
        self.paused = True
        self.dialog_action = '0'
        with open("lib/storage/story_characters.json", "r", encoding="utf-8") as f:
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

    def call_toggle_pause(self):
        if not self.show_tasks and not self.show_rep and not self.show_dialog:
            self.paused = False
        else:
            self.paused = True

    def call_close_window(self):
        if self.show_dialog:
            self.close_dialog()
        elif self.show_rep:
            self.show_rep = False
        elif self.show_tasks:
            self.show_tasks = False

        self.call_toggle_pause()

    def toggle_rep(self):
        self.show_rep = not self.show_rep
        self.call_toggle_pause()

    def toggle_tasks(self):
        self.show_tasks = not self.show_tasks
        self.call_toggle_pause()

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

    def set_hold_button(self, button: str, pressed: bool, player):
        self.hold_buttons.update({button: pressed})

        if button == "left" and pressed:
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
                        if self.dialog_interlocutor != "greeter":
                            self.wait_for_dialog_end = False
                            self.next_stage(self.phase.get("actions", [{}]))
                        self.close_dialog()
                        if answer.get("action", None) is not None:
                            action = answer.get("action")
                            details = answer.get("details", {})

                            if action == "teleport":
                                dimension = details.get("dimension", self.screen)
                                player.set_coord(*list(map(int, details.get("coord", "0-0").split("-"))))
                                if dimension != self.screen:
                                    self.screen = dimension
                                    if dimension == "abyss" and self.dialog_interlocutor == 'greeter':
                                        player.set_coord(*self.story_world_pos)

                    else:
                        self.dialog_action = f"{int(self.dialog_action.split('-')[0]) + 1}"
                        self.current_dialog = self.dialog[int(self.dialog_action)]
                        self.reset_dialog_rects()
            elif self.show_rep:
                tasks_rect = pygame.Rect(421, 108, 41, 23)
                if tasks_rect.collidepoint(*self.mouse_pos):
                    self.toggle_rep()
                    self.toggle_tasks()
            elif self.show_tasks:
                rep_rect = pygame.Rect(360, 108, 41, 23)
                if rep_rect.collidepoint(*self.mouse_pos):
                    self.toggle_tasks()
                    self.toggle_rep()
