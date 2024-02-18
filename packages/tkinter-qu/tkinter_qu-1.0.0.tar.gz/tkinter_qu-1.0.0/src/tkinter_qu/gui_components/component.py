import tkinter

from tkinter_qu.gui_components.dimensions import Dimensions


class Component(tkinter.Widget, Dimensions):
    """A component of any application (has some additional features on top of tkinter.Widget)"""

    saved_place_info = None
    is_currently_hidden = False

    def hide(self):
        """Hides the component, so it is no longer rendered"""

        if not self.is_currently_hidden:
            self.saved_place_info = self.place_info()
            self.place_forget()
            self.is_currently_hidden = True

    def show(self):
        """Shows the component, so it is rendered again"""

        if self.saved_place_info is not None:
            self.place(**self.saved_place_info)
            self.is_currently_hidden = False

    def number_set_dimensions(self, left_edge, top_edge, length, height):
        """Sets the dimensions of the component with the numbers provided"""

        super().number_set_dimensions(left_edge, top_edge, length, height)
        self.place(x=int(left_edge), y=int(top_edge), width=int(length), height=int(height))



