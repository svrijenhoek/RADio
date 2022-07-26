import textstat


class TextStatHandler:

    def __init__(self, language):

        switcher = {
            "dutch": textstat.set_lang("nl"),
            "english": textstat.set_lang("en"),
            "german": textstat.set_lang("de")
        }
        switcher.get(language, "Invalid language")

    @staticmethod
    def flesch_kincaid_score(text):
        return textstat.flesch_reading_ease(text)

    @staticmethod
    def count_words(text):
        return textstat.lexicon_count(text)
