import datetime
# if that doesn't work, do pip install -U numpy
 # https://discuss.pytorch.org/t/valueerror-and-importerror-occurred-when-import-torch/5818
import pandas as pd
import en_core_web_sm
from textblob import TextBlob
import textstat
import json
import os

nlp = en_core_web_sm.load(disable=['parser'])
textstat.set_lang("en")


def process(df):

    to_process = df[df.entities.isnull()]

    split = 100
    chunk_size = int(to_process.shape[0] / split)
    if chunk_size > 0:
        for start in range(0, to_process.shape[0], chunk_size):
            print("\t{}/{}".format(start / chunk_size, split))
            df_subset = to_process.iloc[start:start + chunk_size]

            enrich = list(nlp.pipe(df_subset.text))

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

            df.to_json("data/annotated.json")
    return df


def resolve_dates(df):
    df['date'] = df['date'].apply(lambda x: str(x).strip())
    df['publication_date'] = pd.to_datetime(df['date'], format='%m/%d/%Y', errors='raise')
    return df


def execute():
    if os.path.exists("data/annotated.json"):
        texts = pd.read_json("data/annotated.json")
    else:
        texts = pd.read_csv("data/article_text.csv").set_index('ID')

    texts.drop(texts[texts.text == 'not found'].index, inplace=True)
    texts = texts.dropna(subset=['text'])

    if 'entities' not in texts:
        texts["entities"] = None
        texts["sentiment"] = None
        texts["complexity"] = None

    texts = process(texts)
    texts['publication_date'] = texts['date']
    return texts
