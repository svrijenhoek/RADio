from textblob import TextBlob
from textblob_nl import PatternTagger as PatternTagger_nl, PatternAnalyzer as PatternAnalyzer_nl


class Sentiment:
    """
    Class that calculates the average Affect score based on absolute sentiment polarity values.
    This approach is an initial approximation of the concept, and should be refined in the future.
    Should also implement polarity analysis at index time.
    """

    def __init__(self, language):
        self.scores = {}
        self.language = language

    def analyze(self, text):
        # Analyze the polarity of each text in the appropriate language.
        # Uses Textblob mainly because of its ease of implementation in multiple languages.
        # Dutch Textblob uses the same engine as the English one, but with special Pattern tagger and analyzer.
        if self.language == 'english':
            blob = TextBlob(text)
        elif self.language == 'dutch':
            TextBlob(text, pos_tagger=PatternTagger_nl(), analyzer=PatternAnalyzer_nl())
        return blob

    def get_sentiment_score(self, text):
        blob = self.analyze(text)
        return blob.polarity

