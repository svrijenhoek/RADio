import requests
from recommenders.models.newsrec.newsrec_utils import get_mind_data_set
from recommenders.models.deeprec.deeprec_utils import download_deeprec_resources 
import os
import pandas as pd
import numpy as np
from urllib import request, error
from bs4 import BeautifulSoup
import datetime
import time


def download_politicians(config):
    url = "https://cdn.rawgit.com/everypolitician/everypolitician-data/35c09ba19b40bfd272953719e0b22126d76c589e/data/United_States_of_America/House/term-116.csv"

    r = requests.get(url)  
    with open(config["metadata_folder"] + "term-116.csv", 'wb') as f:
        f.write(r.content)


def download_mind(config):

    data_path = "data/"

    valid_news_file = os.path.join(data_path, r'news.tsv')
    
    mind_url, mind_train_dataset, mind_dev_dataset, mind_utils = get_mind_data_set(config["mind_type"])

    if not os.path.exists(valid_news_file):
        download_deeprec_resources(mind_url, data_path, mind_dev_dataset)


def request_article(url):
    try:
        fp =request.urlopen(url)
        mybytes = fp.read()
        mystr = mybytes.decode("utf8")
        fp.close()
        return mystr
    except (error.HTTPError, ValueError, error.URLError):
        time.sleep(5)
        return # request_article(url)


def read(data):
    soup = BeautifulSoup(data, 'lxml')
    date = soup.find('time').text
    try:
        text = soup.find('section', class_="articlebody").text
    except AttributeError:
        try:
            text = soup.find('div', class_="body-text").text
        except AttributeError:
            try:
                text = soup.find('div', class_="video-description").text
            except AttributeError:
                text = ''
    return date, text        

        
def download_article_text(config):
    # 3-4h for the small MIND dataset

    data_path = "data/"
    news = pd.read_csv("data/news.tsv", sep = "\t", header = None)
    n = news.shape[0]
    if os.path.exists("data/article_text.csv"):
        article_text = pd.read_csv("data/article_text.csv", )
    else:
        article_text = pd.DataFrame({"ID": ["..."] * n,
                                     "date": ["..."] * n,
                                     "category": ["..."] * n,
                                     "url": ["..."] * n,
                                     "text": ["..."] * n})
    
    t1 = time.time()

    not_processed = np.where(article_text.ID == "...")
    if len(not_processed[0]) > 0:
        last = not_processed[0][0]
        for i, news_entry in news.iterrows():
            if i >= last:
                url = news_entry[5]
                ID = news_entry[0]
                category = news_entry[1]
                r = request_article(url)
                if r:
                    date, text = read(r)
                else:
                    date, text = ("–", "not found")
                    print("\tarticle " + str(ID) + " not found")
                if i % 100 == 0:
                    print("\t{}/{}".format(i, n))
                    article_text.to_csv("data/article_text.csv", index=False)
                article_text.loc[i] = [ID, date, category, url, text]
        t2 = time.time()
        print(t2-t1)

        article_text.to_csv("data/article_text.csv", index=False)


def execute(config):
    print("\tdownloading MIND dataset – " + config["mind_type"] + " version")
    download_mind(config)
    print("\tscraping MIND article text – " + config["mind_type"] + " version")
    download_article_text(config)    
    print("\tdownloading politicians metadata")
    download_politicians(config)
