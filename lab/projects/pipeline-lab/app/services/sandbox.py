class Sandbox:
    def __init__(self):
        self.active = False

    def enter(self):
        self.active = True

    def exit(self):
        self.active = False
