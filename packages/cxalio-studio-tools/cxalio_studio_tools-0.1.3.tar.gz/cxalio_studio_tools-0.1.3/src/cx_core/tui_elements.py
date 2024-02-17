class JobCounter:
    def __init__(self, total=None):
        self.total = total
        self.current = 0
        self.number_length = 4 if self.total is None else len(str(self.total))
        self.template = '({0:>?}/{1})'.replace('?', str(self.number_length))

    def __str__(self):
        return self.template.format(self.current, self.total)

    def reset(self):
        self.current = 0
