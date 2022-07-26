import dart.handler.elastic.base_handler
import dart.handler.mongo.connector
import dart.models.Handlers
import pandas as pd
import pickle
import os
from pathlib import Path
import json
from datetime import datetime
import random
import csv


ROOT_DIR = os.path.dirname(os.path.realpath(__file__))
BASE_DIR = os.path.dirname(ROOT_DIR)

elastic_connector = dart.handler.elastic.connector.ElasticsearchConnector()
mongo_connector = dart.handler.mongo.connector.MongoConnector()
handlers = dart.models.Handlers.Handlers(elastic_connector, mongo_connector)


def articles_to_pickle():
    # create articles pickle
    articles = [article['_source'] for article in handlers.articles.get_all_documents('articles')]
    df = pd.DataFrame(articles)
    df.set_index('newsid')
    file = os.path.join(BASE_DIR, Path('data/articles.pickle'))
    with open(file, 'wb') as f:
        pickle.dump(df, f)

# to do: add popularity
def recommendations_to_pickle():
    # for JSON
    lstur = []
    file = open(os.path.join(BASE_DIR, Path('data/recommendations/lstur_pred_large.json')))
    for line in file:
        json_line = json.loads(line)
        lstur.append(json_line)
    #
    naml = []
    file = open(os.path.join(BASE_DIR, Path('data/recommendations/naml_pred_large.json')))
    for line in file:
        json_line = json.loads(line)
        naml.append(json_line)
    #
    npa = []
    file = open(os.path.join(BASE_DIR, Path('data/recommendations/npa_pred_large.json')))
    for line in file:
        json_line = json.loads(line)
        npa.append(json_line)
    #
    nrms = []
    file = open(os.path.join(BASE_DIR, Path('data/recommendations/nrms_pred_large.json')))
    for line in file:
        json_line = json.loads(line)
        nrms.append(json_line)
    #
    pop = []
    file = open(os.path.join(BASE_DIR, Path('data/recommendations/pop_pred_large.json')))
    for line in file:
        json_line = json.loads(line)
        pop.append(json_line)
    sorted_pop = sorted(pop, key=lambda d: d['impr_index'])

    behavior_file = open(os.path.join(BASE_DIR, Path('data/recommendations/behaviors_large.tsv')))
    behaviors_csv = csv.reader(behavior_file, delimiter="\t")
    behaviors = []
    for line in behaviors_csv:
        behaviors.append(line)

    data = []
    for (a, b, c, d, e, f) in zip(behaviors, lstur, naml, npa, nrms, sorted_pop):
        impression_index = a[0]
        userid = a[1]
        date = datetime.strptime(a[2], "%m/%d/%Y %I:%M:%S %p")
        items = a[4].strip().split(" ")
        lstur_row = b['pred_rank']
        naml_row = c['pred_rank']
        npa_row = d['pred_rank']
        nrms_row = e['pred_rank']
        pop_row = f['pred_rank']
        lstur_list = []
        naml_list = []
        npa_list = []
        nrms_list = []
        pop_list = []
        random_list = []
        for x in range(1, min(9, len(items) + 1)):
            try:
                lstur_list.append(items[lstur_row.index(x)].split("-")[0])
                naml_list.append(items[naml_row.index(x)].split("-")[0])
                npa_list.append(items[npa_row.index(x)].split("-")[0])
                nrms_list.append(items[nrms_row.index(x)].split("-")[0])
                pop_list.append(items[pop_row.index(x)].split("-")[0])
                random_index = random.randint(0, len(items))
                random_list.append(items[random_index].split("-")[0])
            except IndexError:
                pass
        data.append({'impr_index': impression_index, 'userid': userid, 'date': date, 'lstur': lstur_list,
                     'naml': naml_list, 'npa': npa_list, 'nrms': nrms_list, 'pop': pop_list, 'random': random_list})
    df = pd.DataFrame(data)
    df = df.set_index('impr_index')
    file = os.path.join(BASE_DIR, Path('data/recommendations_large_all_recs.pickle'))
    with open(file, 'wb') as f:
        pickle.dump(df, f)


# articles_to_pickle()
recommendations_to_pickle()
