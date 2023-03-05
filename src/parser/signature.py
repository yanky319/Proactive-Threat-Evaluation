class Signature:

    def __init__(self, name):
        self.name = name

    def extract(self, content):
        raise NotImplementedError
