from dart.models.Document import Document


class Article(Document):

    def __init__(self, document):
        Document.__init__(self, document)
        self.text = self.source['text']
        self.title = self.source['title']
        self.publication_date = self.source['publication_date']
        try:
            self.doctype = self.source['doctype']
        except KeyError:
            self.doctype = None
        try:
            self.entities = self.source['entities']
        except KeyError:
            self.entities = None
        try:
            self.tags = self.source['tags']
        except KeyError:
            self.tags = None
        try:
            self.author = self.source['byline']
        except KeyError:
            self.author = None
        try:
            self.complexity = self.source['complexity']
            self.nwords = self.source['nwords']
            self.nsentences = self.source['nsentences']
        except KeyError:
            self.complexity = 0
            self.nwords = 0
            self.nsentences = 0
        try:
            self.url = self.source['url']
        except KeyError:
            self.url = None
        try:
            self.popularity = self.source['popularity']
        except KeyError:
            self.popularity = 0
        try:
            self.recommended = self.source['recommended']
        except KeyError:
            self.recommended = []
        try:
            self.tag_percentages = self.source['tag_percentages']
        except KeyError:
            self.tag_percentages = []
        try:
            self.annotated = self.source['annotated']
        except KeyError:
            self.annotated = 'N'
        try:
            self.classification = self.source['classification']
        except KeyError:
            self.classification = None
        try:
            self.editorialTags = self.source['editorialTags']
        except KeyError:
            self.editorialTags = None
        try:
            self.subcategory = self.source['subcategory']
        except KeyError:
            self.subcategory = None
        try:
            self.story = self.source['story']
        except KeyError:
            self.story = None
        try:
            self.sentiment = self.source['sentiment']
        except KeyError:
            self.sentiment = None

    def get(self, x):
        return self.source[x]
