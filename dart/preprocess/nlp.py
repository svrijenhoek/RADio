import datetime
import pandas as pd
from textblob import TextBlob
import textstat
import os


class ProcessText:

    def __init__(self, config):
        self.config = config
        self.annotated_file = self.config["data_folder"]+"annotated.json"
        self.text_file = self.config["data_folder"]+"article_text.csv"
        language = config["language"]
        if language == 'english':
            import en_core_web_sm
            self.nlp = en_core_web_sm.load(disable=['parser'])
            textstat.set_lang("en")
        elif language == 'french':
            import fr_core_news_sm
            self.nlp = fr_core_news_sm.load(disable=['parser'])
            from textblob_fr import PatternAnalyzer
            TextBlob.analyzer = PatternAnalyzer
            textstat.set_lang("fr")
        elif language == "german":
            import de_core_news_sm
            self.nlp = de_core_news_sm.load(disable=['parser'])
            from textblob_de import PatternAnalyzer
            TextBlob.analyzer = PatternAnalyzer
            textstat.set_lang("de")
        elif language == "dutch":
            import nl_core_news_sm
            self.nlp = nl_core_news_sm.load(disable=['parser'])
            from textblob_nl import PatternAnalyzer
            TextBlob.analyzer = PatternAnalyzer
            textstat.set_lang("nl")

    def process(self, df):
        to_process = df[df.entities.isnull()]

        split = 100
        chunk_size = int(to_process.shape[0] / split)
        if chunk_size > 0:
            for start in range(0, to_process.shape[0], chunk_size):
                print("\t{:.0f}/{}".format(start / chunk_size, split))
                df_subset = to_process.iloc[start:start + chunk_size]

                enrich = list(self.nlp.pipe(df_subset.text))

                for i, doc in enumerate(enrich):
                    index = df_subset.iloc[i].name
                    entities = [{
                        'text': e.text,
                        'start_char': e.start_char,
                        'end_char': e.end_char,
                        'label': e.label_
                    } for e in doc.ents]
                    df.at[index, "entities"] = entities

                    blob = TextBlob(doc.text)
                    df.at[index, "sentiment"] = blob.polarity

                    complexity = textstat.flesch_reading_ease(doc.text)
                    df.at[index, "complexity"] = complexity

                df.to_json(self.annotated_file)
        return df

    @staticmethod
    def resolve_dates(df):
        df['date'] = df['date'].apply(lambda x: str(x).strip())
        df['publication_date'] = pd.to_datetime(df['date'], format='%m/%d/%Y', errors='raise')
        return df

    def execute(self):
        if os.path.exists(self.annotated_file):
            texts = pd.read_json(self.annotated_file)
        else:
            texts = pd.read_csv(self.text_file).set_index('ID')

        texts.drop(texts[texts.text == 'not found'].index, inplace=True)
        texts = texts.dropna(subset=['text'])

        if 'entities' not in texts:
            texts["entities"] = None
            texts["sentiment"] = None
            texts["complexity"] = None

        texts = self.process(texts)
        texts['publication_date'] = texts['date']
        return texts
