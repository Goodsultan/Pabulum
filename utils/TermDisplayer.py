import tkinter as tk
from tkinter import ttk
import re
import pyautogui
import os

from utils import Enum
from utils.Set import Set
from utils import ImageFuncs


class TermDisplayer:
    def __init__(self, view, master):
        self.view = view
        self.master = master
        self.current_term = None

        self.model = self.view.mediator.model

        # Frame for canvas and Scrollbars
        self.main_frame = tk.Frame(self.master)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Create Canvas
        self.canvas = tk.Canvas(
            self.main_frame,
            background=Enum.LIGHT_GRAY,
            width=Enum.WINDOW_WIDTH,
            height=Enum.WINDOW_HEIGHT
        )
        self.canvas.bind("<Configure>", self.on_canvas_configure)

        self.frame_container = tk.Frame(self.canvas, background=Enum.LIGHT_GRAY)
        self.frame_container.pack(anchor=tk.CENTER, expand=True)

        self.canvas.create_window((0, 0), window=self.frame_container, anchor="nw")

        # Scrollbars
        self.y_scrollbar = tk.Scrollbar(self.main_frame, command=self.on_y_scroll)
        self.y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, anchor=tk.E)
        self.canvas.configure(yscrollcommand=self.y_scrollbar.set)

        self.x_scrollbar = tk.Scrollbar(self.main_frame, orient=tk.HORIZONTAL, command=self.on_x_scroll)
        self.x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X, anchor=tk.S)
        self.canvas.configure(xscrollcommand=self.x_scrollbar.set)

        self.canvas.pack(fill=tk.BOTH, expand=True)

        # A way to scroll without using the bars
        self.frame_container.bind_all('<B1-Motion>', self.on_canvas_drag)

        self.on_canvas_configure(None)

    def on_y_scroll(self, *args):
        self.canvas.yview(*args)

    def on_x_scroll(self, *args):
        self.canvas.xview(*args)

    @staticmethod
    def unpack_geometry(geometry):
        match = re.match(r'(\d+)x(\d+)\+(\d+)\+(\d+)', geometry)
        width, height, x, y = map(int, match.groups())
        return width, height, x, y

    def on_canvas_drag(self, event):
        width, height, x, y = self.unpack_geometry(self.view.root.geometry())

        current_x, current_y = pyautogui.position()

        # Subtractions for ease at reaching the left and top
        percentage_x = max(0.0, min(1.0, (current_x - x) / width) - 0.3)
        percentage_y = max(0.0, min(1.0, (current_y - y) / height) - 0.5)

        self.canvas.xview_moveto(percentage_x)
        self.canvas.yview_moveto(percentage_y)

    def on_canvas_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def clear(self):
        for child in self.frame_container.winfo_children():
            child.pack_forget()
            child.destroy()

        self.current_term = None

    def display_term(self, term: dict):
        self.clear()

        term_items = term.items()

        self.current_term = term

        for attribute, value in term_items:
            # Skip blacklisted term attributes
            if attribute in self.model.settings[Enum.Settings.Blacklisted_Term_Attributes]:
                continue

            frame = tk.Frame(self.frame_container, background=Enum.LIGHT_GRAY)

            # A way to scroll without using the bars
            frame.bind('<B1-Motion>', self.on_canvas_drag)

            # Make sure multi-line displays neatly
            if type(value) == str and '\n' in value:
                text = f'{attribute}:\n{value}'
            else:
                text = f'{attribute}: {value}'

            # Normalize, because one \n, may become two of them
            text = self.model.normalize_text(text)

            # Special case, where the attribute is None, we want to display an empty string
            if value is None:
                text = f'{attribute}:'

            label = ttk.Button(
                frame,
                command=lambda attr=attribute: self.on_term_attribute_reenter(attr),
                text=text
                # justify=tk.LEFT,
            )
            label.bind('<B1-Motion>', self.on_canvas_drag)

            # Enable a way to view attribute's image
            if attribute in (Enum.TermAttribute.Subject_Image.value, Enum.TermAttribute.Predicate_Image.value) and value:
                try:
                    image_path = os.path.join(self.model.get_images_path(), value)

                    image = ImageFuncs.resize(image_path, **self.model.get_image_requirements())

                    label.image = image
                    label.configure(image=image, compound='top')
                except Exception as e:
                    print(f"An error occurred: {e}")

            label.pack(anchor=tk.NW, expand=True)

            frame.pack(
                expand=False,
                side=tk.TOP,
                fill=tk.Y,
                anchor=tk.W,
            )

        self.on_canvas_configure(None)

    def on_term_attribute_reenter(self, attribute: str):
        Set.reenter(self.current_term, attribute)
        self.view.mediator.controller.update()
