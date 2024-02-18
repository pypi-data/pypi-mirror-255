import tkinter
from tkinter import OptionMenu, StringVar

from tkinter_qu.base.important_variables import WINDOW


class DropDownMenu(OptionMenu):
    """ Extends the tkinter's class OptionMenu and it shows a list of possible values once it is clicked. It adds the
        functionality of setting the selected value of the OptionMenu programmatically, which the regular OptionMenu does not have"""

    selected_item = None
    command = lambda unused: ""  # By default the command should do nothing when it is called
    command_args = []

    # The function and function_args should do nothing by default
    def __init__(self, master, current_item_index, items):
        """Initializes the object"""

        self.selected_item = StringVar()

        # The items other than the currently selected item
        other_items = items[:current_item_index] + items[current_item_index + 1:]

        super().__init__(master, self.selected_item, items[current_item_index], *other_items, command=lambda unused: self.handle_click())
        self.set_selected_item(items[current_item_index])

    def get_selected_item(self):
        """
            Returns:
                str: the item that is currently selected for the DropDownMenu"""

        return self.selected_item.get()

    def set_selected_item(self, value):
        """Sets the item that is currently selected for the DropDownMenu"""

        self.selected_item.set(value)

    def set_command(self, command, command_args):
        """Sets the function that is called when the DropDownMenu is clicked"""

        self.command, self.command_args = command, command_args

    def handle_click(self):
        """Calls the function 'command' when the DropDownMenu is clicked"""

        if len(self.command_args) != 0:
            self.command(*self.command_args)

        else:
            self.command()

    def focus_force(self) -> None:
        """Forces the mouse to focus on the DropDownMenu and for it to be opened"""

        pass

        # Get the center position of the OptionMenu widget
        # x_pos = self.winfo_rootx() + self.winfo_width() // 2
        # y_pos = self.winfo_rooty() + self.winfo_height() // 2

        # Move the mouse to the center of the OptionMenu widget
        # WINDOW.warp_pointer(x_pos, y_pos)

        # Programmatically open the dropdown list
        # self['menu'].unpost()
        # self['menu'].post(self.winfo_x(), self.winfo_y() + self.winfo_height())
