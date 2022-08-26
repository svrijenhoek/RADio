import requests
from recommenders.models.newsrec.newsrec_utils import get_mind_data_set
from recommenders.models.deeprec.deeprec_utils import download_deeprec_resources 
import os
import pandas as pd
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

    download_deeprec_resources(mind_url, data_path, mind_dev_dataset)

    if not os.path.exists(valid_news_file):
        download_deeprec_resources(mind_url, data_path, mind_dev_dataset)


def request_article(url):
    try:
        fp =request.urlopen(url)
        mybytes = fp.read()
        mystr = mybytes.decode("utf8")
        fp.close()
        return mystr
    except error.HTTPError:
        time.sleep(5)
        return self.request(url)

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

    data_path = "data/"
    news = pd.read_csv("data/news.tsv", sep = "\t", header = None)
    n = news.shape[0]
    if os.path.exists("data/article_text.csv"):
        article_text = pd.read_csv("data/article_text.csv")
    else:
        article_text = pd.DataFrame({"ID": ["..."] * n,
                                     "date": ["..."] * n,
                                     "text": ["..."] * n})
    
    t1 = time.time()
    for i, news_entry in news.iterrows():
        url = news_entry[5]
        if url == "...":
            r = request_article(url)
            date, text = read(r)
            # if date and text:
            #     date = datetime.datetime.strptime(date.replace("/", "-").strip(), '%m-%d-%Y')
            print(i)
            article_text.loc[i] = [news_entry[0], date, text]
    t2 = time.time()
    print(t2-t1)

    article_text.to_csv("data/article_text.csv")


def execute(config):
    print("downloading MIND dataset – " + config["mind_type"] + " version")
    download_mind(config)
    print("scraping MIND article text – " + config["mind_type"] + " version")    
    download_article_text(config)    
    print("downloading politicians metadata")
    download_politicians(config)
