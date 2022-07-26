

class Entity:
    def __init__(self, entity):
        self.text = entity['text']
        self.type = entity['label']
        self.start = entity['start_char']
        self.end = entity['end_char']
