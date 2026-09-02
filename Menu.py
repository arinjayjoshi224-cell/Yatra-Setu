class menu:
    def __init__(self, name, options):
        self.name = name
        self.options = options

    def display(self):
        print(f"Menu: {self.name}")
        for index, option in enumerate(self.options, start=1):
            print(f"{index}. {option}")