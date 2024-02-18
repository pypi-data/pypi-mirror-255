from tkinter_qu.base import important_variables


class LibraryChanger:
    """This class changes the library default values"""

    @staticmethod
    def set_all_values(background_color, title, screen_length, screen_height):
        """Sets all the 'important' values"""

        LibraryChanger.set_background_color(background_color)
        LibraryChanger.set_title(title)
        LibraryChanger.set_screen_length(screen_length)
        LibraryChanger.set_screen_height(screen_height)

    @staticmethod
    def set_background_color(background_color):
        """Sets the background color of the window"""

        important_variables.BACKGROUND_COLOR = background_color
        important_variables.WINDOW.configure(bg=background_color)

    @staticmethod
    def set_title(title):
        """Sets the title of the window"""

        important_variables.WINDOW.title(title)

    @staticmethod
    def set_screen_length(screen_length):
        """Sets the length of the window"""

        LibraryChanger.set_screen_dimensions(screen_length, important_variables.SCREEN_HEIGHT)

    @staticmethod
    def set_screen_height(screen_height):
        """Sets the height of the window"""

        LibraryChanger.set_screen_dimensions(important_variables.SCREEN_LENGTH, screen_height)

    @staticmethod
    def set_screen_dimensions(screen_length, screen_height):
        """Sets the dimensions of the window"""

        important_variables.SCREEN_LENGTH = screen_length
        important_variables.SCREEN_HEIGHT = screen_height

        important_variables.WINDOW.geometry(f'{screen_length}x{screen_height}')



