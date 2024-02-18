import tkinter
from tkinter_qu.gui_components.component import Component
from tkinter_qu.base.important_variables import *
from tkinter_qu.base import important_variables


class InputField(tkinter.Text, Component):
    """ Extends tkinter's class Entry. It adds the functionality of more easily setting the text, adding default text, and
        only allowing editing when the InputField is editable"""

    is_selected = False
    count2 = 0
    belongs_to = None
    is_editable = True
    command = None
    string_variable = None
    previous_text = ""
    error_message_function = None

    most_recent_key_press = None
    most_recent_key_press_was_valid = True
    count = 0
    previous_validation_text = ""
    window_type = None
    font = None
    name = ""
    text_color = None
    background_color = None

    def __init__(self, window_type, font, default_text, is_editable=True, text_color=black, background_color=white,
                 error_message_function=lambda text: None, name=""):

        """Initializes the object"""

        self.error_message_function = error_message_function
        self.window_type = window_type
        self.font = font
        self.text_color = text_color
        self.background_color = background_color
        self.name = name

        super().__init__(window_type, font=font, fg=text_color, bg=background_color)

        self.set_text(default_text) # Puts this text at the start of the Input Field (Default Text)

        self.is_editable = is_editable

        self.bind("<Key>", self.on_key_press)
        self.bind("<<Modified>>", self.validate)

    def set_text(self, text):
        """Sets the text of the InputField to the value provided if the InputField is editable"""

        self.previous_text = str(text)
        self.delete("1.0", tkinter.END)
        self.insert(tkinter.END, text)

    def get_text(self):
        return self.get("1.0", tkinter.END).rstrip("\n")

    def set_is_selected(self, is_selected):
        self.is_selected = is_selected

    def get_is_selected(self):
        """
            Returns:
                bool: if the input field is selected"""

        return self.is_selected

    def set_command(self, command):
        """Sets the function that is called when the input field is clicked"""

        self.bind("<1>", lambda event: self.call_command())
        self.command = command

    def call_command(self):
        """Calls the command 'self.command'"""

        self.command(self)

    def focus_force(self) -> None:
        """ Adds functionality to tkinter's build in focus_force() method; it not only moves the mouse to the InputField,
            but it also selects all the text in the InputField"""

        super().focus_force()
        super().tag_add("sel", "1.0", tkinter.END)

    def stop_focusing(self):
        """Forces the Text to stop focusing"""

        super().tag_remove("sel", "1.0", tkinter.END)

    def validate(self, *args):
        """ Validates the input, so if the user put the application into vim normal mode, characters are not typed into
            the InputField."""

        # Prevents this function from being called endlessly
        if self.previous_validation_text != self.get_text():
            self.edit_modified(False)

        self.previous_validation_text = self.get_text()

        #  If the text_is_valid we accept the incoming change otherwise we do not
        if self.most_recent_key_press_was_valid:
            self.previous_text = self.get_text()

        else:
            self.set_text(self.previous_text)
            self.count += 1

    def on_key_press(self, event):
        """Runs what should happen when a key is pressed"""

        self.want_error_validation = False
        self.most_recent_key_press = event.keysym
        self.most_recent_key_press_was_valid = important_variables.input_is_allowed

        if self.focus_get():
            self.edit_modified(False)

        # There are key bindings that should not trigger the InputField getting text in it. For instance, if one keyboard
        # shortcut was 'd' then typing 'd' should only do the shortcut, not put text in the InputField
        key_press_was_a_key_binding = important_variables.all_key_bindings.__contains__(self.most_recent_key_press)

        if self.most_recent_key_press == "BackSpace" or self.most_recent_key_press == "Delete":
            self.most_recent_key_press_was_valid = self.is_editable

        elif important_variables.input_is_allowed:
            self.most_recent_key_press_was_valid = True

        else:
            self.most_recent_key_press_was_valid = not key_press_was_a_key_binding and self.is_editable

        # Finally if no input is valid, then it will make it false
        if not important_variables.input_is_allowed:
            self.most_recent_key_press_was_valid = False

    def get_error_message(self):
        """
            Returns:
                str: the error message if the data is invalid"""

        # For some unknown reason this just does not work
        return self.error_message_function(self.get_text())

    def get_copy(self):
        """
            Returns:
                InputField: a copy of this input field"""

        return_value = InputField(self.window_type, self.font, default_text=self.previous_text,
                                  is_editable=self.is_editable ,text_color=self.text_color, background_color=self.background_color,
                                  name=self.name, error_message_function=self.error_message_function)

        return_value.previous_text = self.previous_text
        return_value.most_recent_key_press_was_valid = False

        return return_value

    def get_name(self):
        return self.name
