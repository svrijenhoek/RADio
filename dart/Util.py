import json
import csv
import numpy as np
import random
import string
import pandas
import os
from datetime import datetime
import pickle
from pathlib import Path

ROOT_DIR = os.path.dirname(os.path.realpath(__file__))
BASE_DIR = os.path.dirname(ROOT_DIR)


def read_config_file():
    with open(os.path.join(BASE_DIR, 'config.json')) as json_data_file:
        data = json.load(json_data_file)
    return data


def read_full_config_file():
    data = read_config_file()
    dictionary = {}
    dictionary['append'] = data['append']
    dictionary['test_size'] = data['test_size']
    dictionary['metrics'] = data['metrics']
    dictionary['cutoff'] = data['cutoff']
    dictionary['language'] = data['language']

    dictionary['behavior_file'] = data['behavior_file']
    dictionary['algorithms'] = data['algorithms']
    dictionary["politics_file"] = data["political_file"]
    dictionary["articles"] = data["articles"]
    dictionary["recommendations"] = data["recommendations"]
    dictionary["output_folder"] = data["output_folder"]
    return dictionary


def random_string(N):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=N))


def get_random_number(mean, sdev):
    return int(np.random.normal(mean, sdev))


def write_to_json(file, s):
    with open(file, 'w') as outfile:
        json.dump(s, outfile, indent=4, separators=(',', ': '), sort_keys=True)


def read_json_file(file):
    with open(file) as F:
        return json.load(F)


def read_csv(file):
    df = pandas.read_csv(file, sep=';', encoding="ISO-8859-1")
    return df


def transform(doc, schema):
    try:
        for key, value in schema.items():
            if value:
                doc[key] = doc.pop(value)
        # if 'teaser' in doc and doc['teaser'] not in doc['text']:
        #     doc['text'] = doc['teaser'] + '\n' + doc['text']
        return doc
    except KeyError:
        pass


def read_behavior_file(file):
    behavior_file = open(Path(file))
    behaviors_csv = csv.reader(behavior_file, delimiter="\t")
    behaviors = []
    for a in behaviors_csv:
        impression_index = a[0]
        userid = a[1]
        date = datetime.strptime(a[2], "%m/%d/%Y %I:%M:%S %p")
        history = a[3].split(" ")
        items = a[4].strip().split(" ")
        items_without_click = [item.split("-")[0] for item in items]
        behaviors.append({'impression_index': impression_index, "userid": userid, 'date': date, 'history': history, 'items': items, 'items_without_click': items_without_click})
    return behaviors


def read_pickle(path):
    return pickle.load(open(Path(path), "rb"))


def create_pickle(o, path):
    file = os.path.join(BASE_DIR, Path(path))
    with open(file, 'wb') as f:
        pickle.dump(o, f)


