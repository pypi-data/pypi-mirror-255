from tkinter_qu.gui_components.dimensions import Dimensions
from tkinter_qu.gui_components.grid import Grid
from tkinter_qu.gui_components.component import Component


class GridType:
    """Holds all the types of grids that can be used"""

    # The order of the items follows this structure: [grid_rows, grid_columns]
    VERTICAL = [1, None]
    HORIZONTAL = [None, 1]


class GridItems(Component):
    """Holds all the items that should be in a grid"""

    items = []

    def __init__(self, items: list[Component], grid_type):
        """Initializes the object"""

        self.items = items
        self.grid = Grid(Dimensions.get_zero(), *grid_type)

    def number_set_dimensions(self, left_edge, top_edge, length, height):
        """Places all the items at that location in a grid format"""

        self.grid.number_set_dimensions(left_edge, top_edge, length, height)
        self.grid.turn_into_grid(self.items, None, None)
