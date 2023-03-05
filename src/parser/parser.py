class Parser:

    def __init__(self):
        self.signatures = []
        # self.record_class = None
        self.records = []

    def add_signature(self, signature):
        self.signatures.append(signature)

    def extract(self, content):
        for signature in self.signatures:
            records = signature.extract(content)
            self.records.extend(records)
