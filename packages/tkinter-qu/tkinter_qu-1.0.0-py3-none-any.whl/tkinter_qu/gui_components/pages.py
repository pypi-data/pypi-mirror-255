class Pages:
    """Shows the application in different pages"""

    page_components = []
    page_component_place_info = []

    def __init__(self, page_components, initial_page_index=0):
        """ Initializes the object

            Args:
                page_components (list[list[Component]]): the components of each page ([page_1_components, page_2_components, etc.])

            Returns:
                None"""

        self.page_components = page_components
        self.change_page(initial_page_index)

    def change_page(self, page_index):
        """Shows only the components related to 'page_index' and 'page_index' is the index of the page, so it starts at 0"""

        for i in range(len(self.page_components)):
            for j in range(len(self.page_components[i])):
                component = self.page_components[i][j]

                # Makes sure components that are not supposed to be visible disappear
                if page_index != i:
                    component.hide()

                # Makes sure that the components that are supposed to be visible are
                if page_index == i:
                    component.show()

    def get_max_page_index(self):
        return len(self.page_components) - 1

    def add_page(self, page_index, new_components):
        self.page_components.insert(page_index, new_components)

    def delete_page(self, page_index):
        del self.page_components[page_index]
