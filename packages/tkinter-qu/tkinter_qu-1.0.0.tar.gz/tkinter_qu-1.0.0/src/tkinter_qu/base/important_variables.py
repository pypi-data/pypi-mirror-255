"""This file holds all the important variables that are within the program"""

from tkinter import Tk
from tkinter_qu.base.colors import *

BACKGROUND_COLOR = dark_gray

# Window
SCREEN_LENGTH = 1100
SCREEN_HEIGHT = 650
WINDOW = Tk()
WINDOW.configure(bg=BACKGROUND_COLOR)
WINDOW.title()
WINDOW.geometry(f'{SCREEN_LENGTH}x{SCREEN_HEIGHT}')
all_key_bindings = []
key_binding_to_function = {}
input_is_allowed = True

FONT_NAME = "Arial"
MINISCULE_FONT = [FONT_NAME, 5]
TINY_FONT = [FONT_NAME, 7]
SMALL_FONT = [FONT_NAME, 8]
NORMAL_FONT = [FONT_NAME, 10]
LARGE_FONT = [FONT_NAME, 15]