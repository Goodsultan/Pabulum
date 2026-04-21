import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk, ImageDraw
import pyperclip
import copy
import os

from utils import Enum


class HarvestWidget:
    def __init__(self, view):
        self.view = view
        self.master = view.root

        self.root = ttk.Frame(master=self.master)

        # For displaying the name of the image on the top left
        self.label_displaying_image_name = tk.Label(self.root, compound='top', justify=tk.LEFT, pady=0)
        self.label_displaying_image_name.pack(expand=False, side=tk.TOP, anchor=tk.NW)

        # Define frame for displaying image given index
        self.image_displayer = tk.Canvas(self.root, height=0)
        self.image_displayer.pack(expand=True, anchor=tk.CENTER)
        self.edited_image = None
        self.edited_photo_image = None
        # For recording changes before applying
        self.draft_image = None

        # Let user draw rectangles
        self.rect_start = None
        self.rect_end = None
        self.to_fill = Enum.CRIMSON

        self.image_displayer.bind("<ButtonPress-1>", self.on_canvas_click)
        self.image_displayer.bind("<B1-Motion>", self.on_canvas_drag)
        self.image_displayer.bind("<ButtonRelease-1>", self.on_canvas_release)

        # Define menu
        self.menu = tk.Menu(self.master)

        self.commands = []
        for command in Enum.ImagesCommand:
            self.commands.append(command)

            self.menu.add_command(
                label=command.value,
                command=lambda cmd=command: self.on_menu_command(command=cmd)
            )

    def on_canvas_click(self, event):
        if self.edited_image:
            self.rect_start = (event.x, event.y)

    def on_canvas_drag(self, event):
        if self.rect_start:
            self.rect_end = (event.x, event.y)

            self.draw_rectangle()

    def on_canvas_release(self, event):
        self.rect_start = None
        self.rect_end = None

        if self.draft_image:
            image = self.draft_image
            self.edited_image = image
            self.edited_photo_image = self.set_image(image)

            self.draft_image = None

    def draw_rectangle(self):
        if self.rect_start and self.rect_end:
            image = copy.deepcopy(self.edited_image)
            draw = ImageDraw.Draw(image)

            x1, y1 = self.rect_start
            x2, y2 = self.rect_end

            # Normalize
            if x1 > x2:
                x1, x2 = x2, x1
            if y1 > y2:
                y1, y2 = y2, y1

            draw.rectangle((x1, y1, x2, y2), outline=Enum.CRIMSON, fill=self.to_fill)

            self.draft_image = image
            self.set_image(image)

    def on_menu_command(self, command):
        self.view.mediator.controller.on_menu_command(command)

    def update(self):
        model = self.view.mediator.model

        image_files = model.get_image_files()

        # Set image given index
        current_index = model.Services['images']['current_index']

        image_file = None

        if current_index in range(0, len(image_files)):
            image_file = image_files[current_index]

        if image_file:
            # image_path = fr"{Enum.IMAGES_DIRECTORY}\{image_file}"
            image_path = os.path.join(model.get_images_path(), image_file)
            image = Image.open(image_path)

            self.edited_image = image
            self.edited_photo_image = self.set_image(image)

            # Check if tab is Services and Images before copying
            if self.view.current_tab_name == self.view.Tab.Services.name:
                services = self.view.tabs[self.view.Tab.Services.name]

                if services.current_tab_name == Enum.Service.Images.name:
                    pyperclip.copy(image_file)

            # Display its name
            self.label_displaying_image_name.configure(text=f'''image_file: {image_file}\ncurrent_index/len(image_files): {current_index + 1}/{len(image_files)}''')
        else:
            self.edited_image = None
            self.edited_photo_image = None
            self.image_displayer.delete('all')

            # Display no name
            self.label_displaying_image_name.configure(text=f'''image_file: None\ncurrent_index/len(image_files): {current_index + 1}/{len(image_files)}''')

    def set_image(self, image):
        self.image_displayer.delete('all')

        photo_image = ImageTk.PhotoImage(image)

        # Keep to avoid garbage collection
        self.image_displayer.photo_image = photo_image

        self.image_displayer.config(width=image.width, height=image.height)
        self.image_displayer.create_image(0, 0, anchor=tk.NW, image=self.image_displayer.photo_image)

        return photo_image


class Images:
    HarvestWidget = HarvestWidget


