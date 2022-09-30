import pandas as pd
import pickle
import os
from pathlib import Path
import json
import datetime
import random
import csv

import dart.Util
import dart.preprocess.downloads


ROOT_DIR = os.path.dirname(os.path.realpath(__file__))
BASE_DIR = os.path.dirname(ROOT_DIR)

config = dart.Util.read_config_file()

mind_type = config['mind_type']


def process():
    lstur = dart.Util.read_multiline_json('data/recommendations/lstur_pred_'+mind_type+'.json')

    naml = dart.Util.read_multiline_json('data/recommendations/naml_pred_'+mind_type+'.json')

    npa = dart.Util.read_multiline_json('data/recommendations/npa_pred_'+mind_type+'.json')

    nrms = dart.Util.read_multiline_json('data/recommendations/nrms_pred_'+mind_type+'.json')

    pop = dart.Util.read_multiline_json('data/recommendations/pop_pred_'+mind_type+'.json')
    sorted_pop = sorted(pop, key=lambda d: d['impr_index'])

    behavior_file = open('data/behaviors.tsv')
    behaviors_csv = csv.reader(behavior_file, delimiter="\t")
    behaviors = []
    for line in behaviors_csv:
        behaviors.append(line)

    data = []
    for (a, b, c, d, e, f) in zip(behaviors, lstur, naml, npa, nrms, sorted_pop):
        impression_index = a[0]
        userid = a[1]
        date = datetime.datetime.strptime(a[2], "%m/%d/%Y %I:%M:%S %p")
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
                random_index = random.randint(0, len(items)-1)
                random_list.append(items[random_index].split("-")[0])
            except IndexError:
                pass
        data.append({'impr_index': impression_index, 'userid': userid, 'date': date, 'lstur': lstur_list,
                     'naml': naml_list, 'npa': npa_list, 'nrms': nrms_list, 'pop': pop_list, 'random': random_list})
    df = pd.DataFrame(data)
    df = df.set_index('impr_index')
    dart.Util.create_pickle(df, config['recommendations'])
    # file = os.path.join(BASE_DIR, Path(config['recommendations']))
    # with open(file, 'wb') as f:
    #     pickle.dump(df, f)