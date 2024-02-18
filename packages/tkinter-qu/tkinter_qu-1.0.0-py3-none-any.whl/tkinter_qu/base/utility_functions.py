"""This class contains utility functions that can be useful for many applications."""

import os
from tkinter_qu.base import important_variables
from tkinter_qu.base.important_variables import *


def get_measurement(unit_of_measurement, amount):
    """
        Returns:
            float: unit_of_measurement / 100 * amount
    """

    return unit_of_measurement / 100 * amount


def get_mouse_position():
    """
        Returns:
            list[int]: {mouse_left_edge, mouse_top_edge}; the mouse's position on the screen"""

    return [WINDOW.winfo_pointerx() - WINDOW.winfo_rootx(),
            WINDOW.winfo_pointery() - WINDOW.winfo_rooty()]


def get_lines(string):
    """
        Returns:
            list[str]: the lines contained within that string (each '/n' creates a new line). Every item in the list is a line"""

    current_line = ""
    lines = []
    enter = "\n"

    for ch in string:
        if ch == enter:
            lines.append(current_line)
            current_line = ""

        else:
            current_line += ch

    return lines + [current_line]  # The last line doesn't have an enter at the end, so adding that line here



def truncate(number, decimal_places):
    """
        Returns:
            number: the number to that many decimal places (it removes the other decimal places)"""

    # Getting the whole number with the decimals removed (to accuracy of decimal places) then making it go back
    # To the original decimal by dividing by 10^decimal_places
    return (number * pow(10, decimal_places) // 1) / pow(10, decimal_places)


def get_next_index(max_index, current_index):
    """
        Returns:
            int: the next index after the 'current_index' and it does cycle 0 -> max_index -> 0 -> etc."""

    next_index = current_index + 1
    return next_index if next_index <= max_index else 0  # If the index is too big it should go back to 0


def get_previous_index(max_index, current_index):
    """
        Returns:
            int: the previous index after the 'current_index' and it does cycle max_index -> 0 -> max_index -> etc."""

    previous_index = current_index - 1

    return previous_index if previous_index >= 0 else max_index


def swap_list_items(items, index1, index2):
    """Swaps the two indexes, so items[index1] = items[index2] and items[index2] = items[index1]"""

    temporary_item = items[index2]
    items[index2] = items[index1]
    items[index1] = temporary_item


def copy_list(items):
    """
        Returns:
            list[obj]: The items that are at a new spot in memory"""

    return_value = []

    for item in items:
        return_value.append(item)

    return return_value


def get_index_of_range(range_lengths, number):
    """
        Returns:
            int: index of range"""

    index = -1
    start_time = 0

    for x in range(len(range_lengths)):
        end_time = start_time + range_lengths[x]

        if number >= start_time and number <= end_time:
            index = x

        start_time = end_time

    return index


def delete_file(file_path):
    """Deletes the file if the file exists"""

    if os.path.exists(file_path):
        os.remove(file_path)


def create_file(file_path):
    """Creates the file if the file does  not exist"""

    if os.path.exists(file_path):
        os.remove(file_path)

    file = open(file_path, "x")
    file.close()


def get_dictionary_value(dictionary: dict, key, default_value):
    """
        Returns:
            object: the value associated with that key if it exists otherwise it returns the default_value"""

    return default_value if not dictionary.__contains__(key) else dictionary[key]


def get_string_after(string, string_start):
    """
        Returns:
            str: the string after 'string_start'"""

    index = string.index(string_start)
    return string[index + 1:]


def get_string(string_list):
    """
        Returns:
            str: the string from all the string_list items"""

    return_value = ""

    for item in string_list:
        return_value += item

    return return_value


def get_file_name(file):
    """
        Returns:
            str: the name of the file - all the contents after the last '/'"""

    file_path = file.name

    last_slash_index = file_path.rindex("/")
    file_name = file_path[last_slash_index + 1:]

    return file_name


def call_functions(functions, event):
    """Calls the functions provided giving each function in function the parameter 'event'"""

    for function in functions:
        function(event)


def add_key_binding(key_binding, function):
    """ Adds the specified key binding that is kept track of (if a key binding is added  to this function, that key will
        be kept track of, so it will not be typed into input fields when the user presses the key"""

    first_dash_index = key_binding.index("-")
    event_key_binding = key_binding[first_dash_index + 1:]
    event_key_binding = event_key_binding[:-1]  # The last character of the string is '>' which is not needed

    if important_variables.key_binding_to_function.get(key_binding) is None:
        important_variables.key_binding_to_function[key_binding] = [function]
        important_variables.all_key_bindings.append(event_key_binding)
        key_binding_functions = important_variables.key_binding_to_function.get(key_binding)
        WINDOW.bind(key_binding, lambda event: call_functions(key_binding_functions, event))

    else:
        important_variables.key_binding_to_function.get(key_binding).append(function)

