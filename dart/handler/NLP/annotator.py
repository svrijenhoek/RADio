import spacy
import en_core_web_sm


class Annotator:

    def __init__(self, language):
        if language == 'dutch':
            self.nlp = spacy.load('nl_core_news_sm', disable=['parser'])
        elif language == 'english':
            self.nlp = en_core_web_sm.load(disable=['parser'])
        elif language == 'german':
            self.nlp = spacy.load('de_core_news_sm', disable=['parser'])

    def annotate(self, text):
        doc = self.nlp(text)
        entities = [{
            'text': e.text,
            'start_char': e.start_char,
            'end_char': e.end_char,
            'label': e.label_
        } for e in doc.ents]

        tags = [{
            'text': token.text,
            'tag': token.pos_
        } for token in doc]

        return doc, entities, tags

