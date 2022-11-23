from datetime import datetime, timedelta
import pandas as pd
import networkx as nx
import community.community_louvain as community_louvain
from collections import defaultdict
from statistics import mode, StatisticsError
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import math

import itertools
from difflib import SequenceMatcher


class StoryIdentifier:
    """
    Class that aims to identify news stories in a set of news articles according to the principles noted in
    Nicholls et al.
    """

    def __init__(self, config):
        self.config = config
        self.threshold = 0.50
        self.categories = ["news", "sports", "finance", "weather", "travel", "video", "foodanddrink", "lifestyle", "autos",
                           "health", "tv", "music", "movies", "entertainment"]
        self.v = TfidfVectorizer(stop_words='english')

    def vectorize(self, text):
        try:
            split = text.split('\n')
            return self.v.fit_transform(split)
        except ValueError:
            return []
        # self.v.fit_transform(x) if len(x[0]) > 1 or len(x) > 1 else []

    def execute(self, df):
        first_date = df.publication_date.min() # datetime.strptime("2019-10-01", '%Y-%m-%d')
        last_date = df.publication_date.max() # datetime.strptime("2019-12-07", '%Y-%m-%d')

        cosines = self.get_cosines_in_timerange(df, first_date, last_date)

        stories = self.identify(cosines)
        df['story'] = 0
        for k, v in stories.items():
            df.at[k, 'story'] = v
        return df

    def get_cosines_in_timerange(self, df, first_date, last_date):
        cosines = []
        delta = last_date - first_date
        for i in range(delta.days+1):
            today = first_date + timedelta(days=i)
            yesterday = today - timedelta(days=1)
            past_three_days = today - timedelta(days=3)
            documents_3_days = df.loc[(df['publication_date'] >= past_three_days) & (df['publication_date'] <= today)] # self.handlers.articles.get_all_in_timerange(past_three_days, today)
            documents_1_day = df.loc[(df['publication_date'] >= yesterday) & (df['publication_date'] <= today)] # self.handlers.articles.get_all_in_timerange(yesterday, today)
            for category in self.categories:
                subset_3 = documents_3_days.loc[documents_3_days['category'] == category]
                subset_1 = documents_1_day.loc[documents_1_day['category'] == category]

                if not subset_1.empty and not subset_3.empty:

                    subset_1_matrix = self.v.fit_transform(subset_1['text'].tolist())
                    subset_3_matrix = self.v.fit_transform(subset_1['text'].tolist())

                    cosine_similarities = cosine_similarity(subset_1_matrix, subset_3_matrix)

                    for x, row in enumerate(cosine_similarities):
                        for y, cosine in enumerate(row):
                            if self.threshold <= cosine < 1:
                                x_id = list(subset_1.index.values)[x]
                                y_id = list(subset_3.index.values)[y]
                                cosines.append({'x': x_id, 'y': y_id, 'cosine': cosine})
        return cosines

    @staticmethod
    def get_cosine(vec1, vec2):
        intersection = set(vec1.keys()) & set(vec2.keys())
        numerator = sum([vec1[x] * vec2[x] for x in intersection])

        sum1 = sum([vec1[x] ** 2 for x in list(vec1.keys())])
        sum2 = sum([vec2[x] ** 2 for x in list(vec2.keys())])
        denominator = math.sqrt(sum1) * math.sqrt(sum2)

        if not denominator:
            return 0.0
        else:
            return float(numerator) / denominator

    @staticmethod
    def identify(cosines):
        # calculate cosine similarity between documents
        # ids = [article.id for article in documents if not article.text == '']
        # cosines = self.cos.calculate_all_distances(ids)
        # if cosines:
        df = pd.DataFrame(cosines)
        df = df.drop_duplicates()
        # create graph
        G = nx.from_pandas_edgelist(df, 'x', 'y', edge_attr='cosine')
        # create partitions, or stories
        partition = community_louvain.best_partition(G)
        return partition
            # else:
            #    return {}

    def update_articles(self, stories, documents):
        docs = [{'id': doc_id, 'story': story_id} for doc_id, story_id in stories.items()]
        self.handlers.articles.update_bulk(docs)

        count = len(stories)
        documents_in_stories = [docid for docid in stories.keys()]
        all_documents = [doc.id for doc in documents]
        single_articles = sorted(set(all_documents).difference(documents_in_stories))
        docs = []
        for article in single_articles:
            docs.append({'id': article, 'story': count})
            count += 1
        self.handlers.articles.update_bulk(docs)

    def print_stories(self, stories, documents):
        v = defaultdict(list)
        for key, value in stories.items():
            v[value].append(key)
        for key, value in v.items():
            print(key)
            print(self.cos.most_relevant_terms(value))
            classifications = []
            titles = []
            for docid in value:
                article = self.handlers.articles.get_by_id(docid)
                titles.append(article.title)
                classifications.append(article.classification)
            try:
                print(mode(classifications))
            except StatisticsError:
                print(classifications)
            for title in titles:
                print("\t" + title)
        count = len(stories)
        documents_in_stories = [docid for docid in stories.keys()]
        all_documents = [doc.id for doc in documents]
        single_articles = sorted(set(all_documents).difference(documents_in_stories))
        for article_id in single_articles:
            article = self.handlers.articles.get_by_id(article_id)
            print("{}\t{}".format(count, article.title))
            count += 1

    def add_stories(self, stories):
        s = defaultdict(list)
        # make a dictionary where each story id is linked to its article ids
        for k, v in stories.items():
            s[v].append(k)
        # identify the most important keywords, most common classification and a title
        for story_id, doc_ids in s.items():
            keywords = self.cos.most_relevant_terms(doc_ids)
            classifications = []
            titles = []
            dates = []
            for doc_id in doc_ids:
                article = self.handlers.articles.get_by_id(doc_id)
                classifications.append(article.classification)
                titles.append(article.title)
                dates.append(article.publication_date)
                self.handlers.articles.update(doc_id, 'story', story_id)
            try:
                classification = mode(classifications)
            except StatisticsError:
                classification = classifications[0]
            self.handlers.stories.add_story(dates[0], dates, story_id, doc_ids, keywords, classification, titles[0])
            # self.handlers.stories.add_to_queue(dates[0], dates, story_id, doc_ids, keywords, classification, titles[0])

        # account for all the documents that are not part of stories
        # disabled during refactoring
        # count = len(stories)
        # documents_in_stories = [docid for docid in stories.keys()]
        # all_documents = [doc.id for doc in self.handlers.articles.get_all_articles()]
        # single_articles = sorted(set(all_documents).difference(documents_in_stories))
        # for article_id in single_articles:
        #     article = self.handlers.articles.get_by_id(article_id)
        #     keywords = self.cos.most_relevant_terms([article_id])
        #     self.handlers.stories.add_story(article.publication_date, article.publication_date, count, article.id,
        #                                     keywords, article.classification, article.title)
            # self.handlers.stories.add_to_queue(article.publication_date, article.publication_date, count, article.id,
            # keywords, article.classification, article.title)
            # count += 1
        # self.handlers.stories.add_bulk()

    @staticmethod
    def distance(names):
        output = []
        for a, b in itertools.combinations(names, 2):
            if len(a) < 3 or len(b) < 3:
                similarity = 0
            elif a in b or b in a:
                similarity = 1
            else:
                similarity = SequenceMatcher(None, a, b).ratio()
            output.append({'a': a, 'b': b, 'similarity': similarity})
        return output
