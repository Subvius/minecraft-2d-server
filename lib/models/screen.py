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

    def get_show_inventory(self) -> bool:
        return self.show_inventory

    def toggle_pause(self):
        self.paused = not self.paused

    def change_screen(self, screen: str):
        self.screen = screen

    def set_mouse_pos(self, pos: tuple[int, int]):
        self.mouse_pos = pos

    def toggle_hold_button(self, button: str):
        self.hold_buttons.update({button: self.hold_buttons.get(button, False)})
