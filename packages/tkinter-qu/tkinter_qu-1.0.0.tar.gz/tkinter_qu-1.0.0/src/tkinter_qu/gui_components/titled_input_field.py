from tkinter_qu.gui_components.dimensions import Dimensions
from tkinter_qu.gui_components.grid_items import GridItems, GridType
from tkinter_qu.gui_components.input_field import InputField
from tkinter_qu.base.colors import *


class TitledInputField(Dimensions):
    """An input field that is titled"""

    grid = None
    title_field = None
    input_field = None
    error_message_function = None

    def __init__(self, window_type, font, input_field_default_text, title_field_text, title_field_background_color=black,
                 title_field_text_color=white, input_field_background_color=white, input_field_text_color=black,
                 error_message_function=lambda text: None, input_field_is_editable=True):

        """Initializes the object"""

        self.title_field = InputField(window_type, font, title_field_text, is_editable=False,
                                      background_color=title_field_background_color, text_color=title_field_text_color)
        self.input_field = InputField(window_type, font, input_field_default_text, is_editable=input_field_is_editable,
                                      background_color=input_field_background_color, text_color=input_field_text_color)

        self.error_message_function = error_message_function
        self.grid_items = GridItems([self.title_field, self.input_field], GridType.VERTICAL)

    def set_text(self, text):
        """Sets the text of the InputField to the value provided if the InputField is editable"""

        self.input_field.set_text(text)

    def set_title(self, title):
        """Sets the title of the title InputField"""

        self.title_field.set_text(title)

    def get_text(self):
        return self.input_field.get_text()

    def get_error_message(self):
        """
            Returns:
                str: the error message if the data is invalid"""

        return self.error_message_function(self.get_text())

    def set_command(self, command):
        self.input_field.set_command(command)

    @property
    def is_editable(self):
        return self.input_field.is_editable

    def focus_force(self):
        self.input_field.focus_force()

    def number_set_dimensions(self, left_edge, top_edge, length, height):
        """Places all the items at that location in a grid format"""

        self.grid_items.number_set_dimensions(left_edge, top_edge, length, height)

