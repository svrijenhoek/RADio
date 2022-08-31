class Article:

    def __init__(self, document):
        print(document)
        self.newsid = document[0]
        values = document[1]
        self.text = values['text']
        self.publication_date = values['publication_date']
        try:
            self.entities = values['entities']
        except KeyError:
            self.entities = None
        try:
            self.complexity = values['complexity']
        except KeyError:
            self.complexity = 0
        try:
            self.url = values['url']
        except KeyError:
            self.url = None
        try:
            self.annotated = values['annotated']
        except KeyError:
            self.annotated = 'N'
        try:
            self.story = values['story']
        except KeyError:
            self.story = None
        try:
            self.sentiment = values['sentiment']
        except KeyError:
            self.sentiment = None
