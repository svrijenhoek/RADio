import requests
from recommenders.models.newsrec.newsrec_utils import get_mind_data_set
from recommenders.models.deeprec.deeprec_utils import download_deeprec_resources 
import os

def download_politicians(config):
    url = "https://cdn.rawgit.com/everypolitician/everypolitician-data/35c09ba19b40bfd272953719e0b22126d76c589e/data/United_States_of_America/House/term-116.csv"

    r = requests.get(url)  
    with open(config["metadata_folder"] + "term-116.csv", 'wb') as f:
        f.write(r.content)

def download_mind(config):

    data_path = "data/"

    valid_news_file = os.path.join(data_path, r'news.tsv')
    
    mind_url, mind_train_dataset, mind_dev_dataset, mind_utils = get_mind_data_set(config["mind_type"])

    download_deeprec_resources(mind_url, data_path, mind_dev_dataset)

    if not os.path.exists(valid_news_file):
        download_deeprec_resources(mind_url, data_path, mind_dev_dataset)

