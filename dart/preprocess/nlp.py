import spacy
# if that doesn't work, do pip install -U numpy
 # https://discuss.pytorch.org/t/valueerror-and-importerror-occurred-when-import-torch/5818
import pandas as pd
import en_core_web_sm

article_text = pd.read_csv("data/article_text.csv")

nlp = en_core_web_sm.load(disable=['parser'])

enrich = list(nlp.pipe(article_text.text.head()))

article_text["entities"] = None

for i, doc in enumerate(enrich):
    entities = [{
        'text': e.text,
        'start_char': e.start_char,
        'end_char': e.end_char,
        'label': e.label_
    } for e in doc.ents]
    article_text.loc[i, "entities"] = entities


article_text.to_csv("data/article_text_entities.csv")
