class ProduceBase:
    @classmethod
    def wrapper(cls, name=None):
        def w(d):
            return cls(d, name)

        return w

    def __init__(self, data, name=None):
        self.data = data
        self.name = name
