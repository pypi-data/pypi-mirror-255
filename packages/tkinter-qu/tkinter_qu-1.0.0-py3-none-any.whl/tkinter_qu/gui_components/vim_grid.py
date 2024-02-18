from tkinter import messagebox

from tkinter_qu.gui_components.grid import Grid
from tkinter_qu.gui_components.input_field import InputField
from tkinter_qu.base.important_variables import WINDOW
from tkinter_qu.base import important_variables
from tkinter_qu.base.utility_functions import add_key_binding


class VimGrid:
    """ A Grid of Items that you can navigate through using vim key bindings (hjklio). You can turn on the navigation mode
        by hitting the caps lock key"""

    current_column = 0
    current_row = 0
    is_selected = False
    items = []
    grid = None
    dimensions = None
    in_use = False
    can_edit_grid = True

    class States:
        INPUT = "INPUT",
        MOVING_BETWEEN_INPUT_FIELDS = "MOVING_BETWEEN_INPUT_FIELDS",
        NOTHING = "NOTHING",

    current_state = States.INPUT

    def __init__(self, items, dimensions, grid_rows, grid_columns, can_edit_grid=True):
        """Initializes all the bindings"""

        self.can_edit_grid = can_edit_grid

        add_key_binding("<KeyPress-h>", lambda event: self.change_input_field_selection("Left"))
        add_key_binding("<KeyPress-b>", lambda event: self.change_input_field_selection("Beginning"))
        add_key_binding("<KeyPress-j>", lambda event: self.change_input_field_selection("Down"))
        add_key_binding("<KeyPress-k>", lambda event: self.change_input_field_selection("Up"))
        add_key_binding("<KeyPress-l>", lambda event: self.change_input_field_selection("Right"))
        add_key_binding("<KeyPress-o>", lambda event: self.change_input_field_selection("End"))
        add_key_binding("<KeyPress-Tab>", lambda event: self.change_input_field_selection("Right"))

        add_key_binding("<KeyPress-i>", lambda event: self.change_state(self.States.INPUT))
        add_key_binding("<KeyPress-Escape>", lambda event: self.change_state(self.States.MOVING_BETWEEN_INPUT_FIELDS))
        add_key_binding("<KeyPress-s>", lambda event: self.change_state(self.States.NOTHING))

        add_key_binding("<KeyPress-a>", lambda event: self.add_row(self.current_row + 1))
        add_key_binding("<KeyPress-A>", lambda event: self.add_row(self.current_row))
        add_key_binding("<KeyPress-d>", lambda event: self.delete_row(self.current_row))
        add_key_binding("<KeyPress-D>", lambda event: self.delete_row(self.current_row - 1))
        add_key_binding("<KeyPress-c>", lambda event: self.change_text())

        self.grid = Grid(dimensions, grid_rows, grid_columns)

        self.items = items

        for item in self.items:
            item: InputField = item
            item.set_command(self.handle_input_field_click)

        self.dimensions = dimensions

        self.grid.turn_into_grid(items, None, None)

    def get_item_row(self, row_number):
        """
            Returns:
                list[Component]: the items in the current row"""

        # By multiplying the row number by row_length, the row start is gotten. Adding row length will bring it to the end of the row
        start = row_number * self.row_length
        return self.items[start: start + self.row_length + 1]

    @property
    def grid_rows(self):
        return self.grid.get_rows(len(self.items))

    @property
    def grid_columns(self):
        return self.grid.get_columns(len(self.items))

    def change_input_field_selection(self, event):
            """ Changes the selected input field depending on what key was pressed

                Args:
                    event(str): the event name. Here are all the possible values:
                        'Up': Selects the next input field above the current one (belongs to the previous way point)
                        'Down': Selects the next input field below the current one (belongs to the next way point)
                        'Left': Selects the next input field to the right of the current one (belongs to the current way point)
                        'Right': Selects the previous input field to the left the current one (belongs to the current way point)

                Returns:
                    None
            """

            valid_event_types = ["Up", "Down", "Left", "Right", "Beginning", "End"]

            if not valid_event_types.__contains__(event):
                raise ValueError("Valid Data was not inputted!!!")

            if self.current_state != self.States.MOVING_BETWEEN_INPUT_FIELDS or not self.in_use:
                return

            # Modifying the numbers, so the selected input_field is not out of bounds of the input_fields on the screen
            max_column_number = self.grid_columns - 1
            max_row_number = self.grid_rows - 1

            if event == "Up":
                self.current_row -= 1

            if event == "Down":
                self.current_row += 1

            if event == "Left":
                self.current_column -= 1

            if event == "Right":
                self.current_column += 1

            if event == "Beginning":
                self.current_column = 0

            if event == "End":
                self.current_column = max_column_number

            # Column Checks
            if self.current_column > max_column_number:
                self.current_column = 0
                self.current_row += 1

            if self.current_column < 0:
                self.current_column = max_column_number
                self.current_row -= 1

            # Row Checks
            if self.current_row < 0:
                self.current_row = max_row_number

            if self.current_row > max_row_number:
                self.current_row = 0

            current_item = self.get_current_item()

            if current_item.is_editable:
                current_item.focus_force()

            else:
                self.change_input_field_selection(event)

    def change_state(self, new_state):
        """Changes the state of the VIM grid"""

        valid_new_states = [self.States.MOVING_BETWEEN_INPUT_FIELDS, self.States.INPUT, self.States.NOTHING]

        if not valid_new_states.__contains__(new_state):
            raise ValueError("Valid Data was not inputted!!!")

        if self.current_state == self.States.MOVING_BETWEEN_INPUT_FIELDS and new_state == self.States.INPUT:
            self.current_state = self.States.INPUT

        elif self.current_state == self.States.MOVING_BETWEEN_INPUT_FIELDS and new_state == self.States.NOTHING:
            self.current_state = self.States.NOTHING

        elif new_state == self.States.MOVING_BETWEEN_INPUT_FIELDS:
            self.current_state = self.States.MOVING_BETWEEN_INPUT_FIELDS

        important_variables.input_is_allowed = self.current_state == self.States.INPUT

    def add_row(self, row_number):
        """Adds a row to the grid at the row number provided"""

        if self.current_state != self.States.MOVING_BETWEEN_INPUT_FIELDS:
            return

        if not self.in_use or not self.can_edit_grid:
            return

        current_items_start_index = self.current_row * self.grid_columns
        current_items_end_index = current_items_start_index + self.grid_columns - 1
        current_items = self.items[current_items_start_index: current_items_end_index + 1]
        copied_current_items = [item.get_copy() for item in current_items]

        new_index = row_number * self.grid_columns

        if new_index < 0 or new_index > len(self.items):
            messagebox.showerror("ERROR", "This action can't be completed because the row_number is either too small or large")
            return

        self.items = self.items[:new_index] + copied_current_items + self.items[new_index:]
        self.grid.turn_into_grid(self.items, None, None)

    def delete_row(self, row_number, force=False):
        """Deletes the specified row from the grid"""

        if self.current_state != self.States.MOVING_BETWEEN_INPUT_FIELDS and not force:
            return

        if not self.in_use or not self.can_edit_grid:
            return

        for x in range(self.grid_columns):
            end_index = self.grid_columns * row_number + self.grid_columns - 1  # Indexes and lengths are offset by one
            index = end_index - x

            self.items[index].destroy()
            del self.items[index]

        self.grid.turn_into_grid(self.items, None, None)

    def get_current_item(self):
        """
            Returns:
                Component: the currently selected component in the grid
        """

        return self.items[self.current_row * self.grid_columns + self.current_column]

    def change_text(self):
        """Changes the text of the current component"""

        if self.current_state == self.States.MOVING_BETWEEN_INPUT_FIELDS:
            self.get_current_item().set_text("")
            self.change_state(self.States.INPUT)

    def handle_input_field_click(self, input_field):
        """ Updates the 'self.current_row' and 'self.current_column' attributes of this class, so
            it updates based on where you clicked"""

        self.current_row = input_field.row_number
        self.current_column = input_field.column_number

    def set_in_use(self, value):
        """Sets the variable 'self.in_use' which controls whether the 'Vim actions' are being used"""

        self.in_use = value
