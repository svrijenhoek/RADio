import csv
import time
from urllib import request, error
from bs4 import BeautifulSoup
import datetime

from dart.handler.elastic.connector import ElasticsearchConnector
import dart.handler.NLP.annotator


class AddArticles:
    """
    Class that adds articles into an ElasticSearch index. Articles are first annotated using spaCy's tagger and
    Named Entity Recognizer.
    """

    def __init__(self, config, handlers):
        self.handlers = handlers
        self.language = config['language']
        self.annotator = dart.handler.NLP.annotator.Annotator(self.language)
        self.queue = []

    def request(self, url):
        try:
            fp =request.urlopen(url)
            mybytes = fp.read()
            mystr = mybytes.decode("utf8")
            fp.close()
            return mystr
        except error.HTTPError:
            time.sleep(5)
            return self.request(url)

    @staticmethod
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

    def execute(self, file_location):
        success = 0
        no_text = 0

        tsv_file = open(file_location, encoding="utf-8")
        read_tsv = csv.reader(tsv_file, delimiter="\t")

        for line in read_tsv:
            if not self.handlers.articles.get_field_with_value('newsid', line[0]):
                json_doc = {'newsid': line[0],
                            'category': line[1],
                            'subcategory': line[2],
                            'title': line[3],
                            'abstract': line[4],
                            'url': line[5],
                }
                try:
                    json_doc['title_entities'] = line[6]
                    json_doc['abstract_entities'] = line[7]
                except IndexError:
                    continue
                data = self.request(json_doc['url'])
                date, text = self.read(data)
                if date and text:
                    _, entities, tags = self.annotator.annotate(text)
                    date = datetime.datetime.strptime(date.replace("/", "-").strip(), '%m-%d-%Y')
                    json_doc['publication_date'] = date.strftime("%Y-%m-%d")
                    json_doc['text'] = text
                    json_doc['entities'] = entities
                    self.queue.append(json_doc)
                    success += 1
                else:
                    no_text += 1
                    print(json_doc['url'])
                if len(self.queue) > 0 and len(self.queue) % 25 == 0:
                    self.handlers.articles.add_bulk(self.queue)
                    self.queue = []
        if self.queue:
            self.handlers.articles.add_bulk(self.queue)



