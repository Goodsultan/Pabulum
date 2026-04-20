import tkinter as tk
import pyautogui
import re
from utils.Enum import LIGHT_GRAY
from pynput.mouse import Listener
from PIL import ImageGrab
import os
import pyperclip


class Screenshot:
    def __init__(self, screenshot_name="screenshot.png", master=None):
        self.box = tk.Toplevel(background=LIGHT_GRAY, borderwidth=2, relief=tk.RIDGE)
        self.box.overrideredirect(True)
        self.box.attributes('-topmost', True)
        self.box.attributes('-alpha', 0.2)

        self.master = master

        self.screenshot_name = screenshot_name
        self.box.title(self.screenshot_name)

        self.initial_x, self.initial_y = pyautogui.position()

        self.minimum_size = 3

        self.box.geometry(f'%dx%d+%d+%d' % (self.minimum_size, self.minimum_size, self.initial_x, self.initial_y))

        self.mouse_listener = Listener(on_move=self.on_move, on_click=self.on_click)
        self.mouse_listener.start()

    def on_move(self, x, y):

        delta_x = x - self.initial_x
        delta_y = y - self.initial_y

        final_width = delta_x
        final_height = delta_y
        final_left = self.initial_x
        final_top = self.initial_y

        # Deal with negative coordinates
        if delta_x < self.minimum_size:
            final_width = self.initial_x - x
            final_left = x

        if delta_y < self.minimum_size:
            final_height = self.initial_y - y
            final_top = y

        # Ensure positive values
        final_width = abs(final_width)
        final_height = abs(final_height)
        final_left = abs(final_left)
        final_top = abs(final_top)

        self.box.geometry(f'%dx%d+%d+%d' % (final_width, final_height, final_left, final_top))

    @staticmethod
    def unpack_window_geometry(window):
        match = re.match(r'(\d+)x(\d+)\+(\d+)\+(\d+)', window.geometry())

        if match:
            width, height, x, y = map(int, match.groups())
            return width, height, x, y
        else:
            # Patch a bug, where match is None
            return 0, 0, 0, 0

    def on_click(self, x, y, button, pressed):
        self.box.attributes('-alpha', 0)

        width, height, x, y = self.unpack_window_geometry(self.box)

        # Patch a bug
        if x == 0 and y == 0 and width == 0 and height == 0:
            return

        x1, y1 = x, y
        x2, y2 = x + width, y + height

        screenshot = ImageGrab.grab(bbox=(x1, y1, x2, y2))

        relative_directory = "images"
        file_name = self.screenshot_name
        file_path = os.path.join(relative_directory, file_name)

        # Create the directory if it doesn't exist
        os.makedirs(relative_directory, exist_ok=True)

        screenshot.save(file_path)
        
        # Copy file_name for better experience
        pyperclip.copy(file_name)

        # Clean up
        self.box.destroy()
        self.mouse_listener.stop()

        # Update the master if there's one
        if self.master:
            self.master.update()
