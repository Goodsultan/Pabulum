from PIL import Image, ImageTk
from utils import Enum
import os


def resize(image_path: str, max_height=1000, min_height=0, max_width=700):
    try:
        # original_image_name = image_path[image_path.rindex('\\'):]
        if os.path.exists(image_path):
            original_image = Image.open(image_path)
        else:
            return ''
        # else:
        #     for auxiliary_images_directory in Enum.auxiliary_images_directories:
        #         new_path = auxiliary_images_directory + original_image_name
        #         if os.path.exists(new_path):
        #             original_image = Image.open(new_path)
        #             break
        #     else:
        #         return ''

        width, height = original_image.size

        # Calculate the aspect ratio to maintain proportions
        aspect_ratio = width / height

        # Calculate new dimensions based on the specified max_height and min_height
        new_height = min(height, max_height)
        new_height = max(new_height, min_height)

        new_width = int(new_height * aspect_ratio)
        new_width = min(new_width, max_width)

        # Resize the image
        resized_image = original_image.resize((new_width, new_height), Image.LANCZOS)

        # Convert the resized image to PhotoImage format
        photo_image = ImageTk.PhotoImage(resized_image)

        return photo_image
    except (IOError, FileNotFoundError):
        return ''
