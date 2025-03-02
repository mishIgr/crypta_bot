class Counter:

    def __init__(self, max_value):
        self.value = max_value - 1
        self.max_value = max_value

    def next(self):
        self.value = (self.value + 1) % self.max_value
        return self.value

    def next_str(self):
        return str(self.next())
