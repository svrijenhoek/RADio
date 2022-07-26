from datetime import datetime, timedelta
import os
import json
import numpy as np
import pandas as pd
import pickle

import random
import csv


class RecommendationGenerator:
    """
    Class that generates baseline recommendations based on the articles stored in the 'articles' Elasticsearch index.
    Eight articles are 'recommended' following to the following three methods:
    - Random --> recommends randomly chosen articles
    - Most popular --> recommends the articles that have been shared most on Facebook
    - More like this --> recommends the articles that are most similar to what the user has read before

    """

    def __init__(self, documents, size, handlers):
        self.documents = documents
        self.size = size
        self.handlers = handlers

    def generate_random(self):
        random_numbers = np.random.choice(len(self.documents), self.size, False)
        return [self.documents[i].id for i in random_numbers]

    def generate_most_popular(self):
        return [self.documents[i].id for i in range(int(self.size))]

    def generate_more_like_this(self, user, upper, lower):
        results = self.handlers.articles.more_like_this_history(user, upper, lower)
        return [results[i].id for i in range(min(int(self.size), len(results)))]

    def generate_political(self, user, upper, lower):
        political_documents = self.handlers.articles.get_political(user, upper, lower)
        return [political_documents[i].id for i in range(min(len(political_documents), self.size))]


class RunRecommendations:

    def __init__(self, config, handlers):
        self.handlers = handlers
        self.size = config["recommendation_size"]

        self.users = self.handlers.users.get_all_users()
        self.baseline_recommendations = config['baseline_recommendations']

    def generate_recommendations(self, user, date, upper, lower, generator):
        # generate random selection
        if 'random' in self.baseline_recommendations:
            random_recommendation = generator.generate_random()
            self.handlers.recommendations.add_to_queue(date, user.id, 'random', random_recommendation)
        # select most popular
        if 'most_popular' in self.baseline_recommendations:
            most_popular_recommendation = generator.generate_most_popular()
            self.handlers.recommendations.add_to_queue(date, user.id, 'most_popular', most_popular_recommendation)
        # get more like the user has previously read
        if 'more_like_this' in self.baseline_recommendations:
            more_like_this_recommendation = generator.generate_more_like_this(user, upper, lower)
            self.handlers.recommendations.add_to_queue(date, user.id, 'more_like_this', more_like_this_recommendation)
        # get more like the user has previously read
        if 'political' in self.baseline_recommendations:
            political_recommendation = generator.generate_political(user, upper, lower)
            self.handlers.recommendations.add_to_queue(date, user.id, 'political', political_recommendation)
        self.handlers.recommendations.add_bulk()

    def load(self):
        for path, _, files in os.walk(self.folder):
            for name in files:
                # assumes all files are json-l, change this to something more robust!
                for line in open((os.path.join(path, name))):
                    json_doc = json.loads(line)
                    # if self.schema:
                    #     json_doc = Util.transform(json_doc, self.schema)
                    if json_doc:
                        date = json_doc['date']
                        date = datetime.strptime(date, '%m/%d/%Y %H:%M:%S %p').strftime('%Y-%m-%d')
                        user_id = json_doc['userid']
                        recommendation_type = json_doc['type']
                        # to account for nan article ids
                        articles = [article_id for article_id in json_doc['articles'] if not article_id != article_id]
                        self.handlers.recommendations.add_to_queue(date, user_id, recommendation_type, articles)

                    if len(self.handlers.recommendations.queue) > 1000:
                        self.handlers.recommendations.add_bulk()

        if self.handlers.recommendations.queue:
            self.handlers.recommendations.add_bulk()

    def generate_reading_histories(self):
        for recommendation_type in self.handlers.recommendations.get_recommendation_types():
            for user in self.users:
                recommendations = self.handlers.recommendations.get_recommendations_to_user(user.id, recommendation_type)
                user.interactions[recommendation_type] = {entry.date: entry.articles for entry in recommendations}
                self.handlers.users.update_reading_history(user)

    def execute(self):
        if self.load_recommendations == 'Y':
            self.load()
        # go over every date specified in the config file
        if self.baseline_recommendations:
            for date in self.dates:
                # define the timerange for retrieving documents
                upper = datetime.strptime(date, '%Y-%m-%d')
                lower = upper - timedelta(days=self.timerange)
                # retrieve all the documents that are relevant for this date
                documents = self.handlers.articles.get_all_in_timerange(lower, upper)
                # retrieve all recommendations at date if exhaustive = minimal. This causes an exception when no own
                # recommendations are loaded.
                if self.exhaustive == 'minimal':
                    # fix this
                    rec_at_date = self.handlers.recommendations.get_users_with_recommendations_at_date(date, 'npa')
                # to account for a very sparse index
                recommendation_size = min(len(documents), self.size)
                rg = RecommendationGenerator(documents, recommendation_size, self.handlers)
                if self.exhaustive == 'full':
                    user_base = self.users
                elif self.exhaustive == 'minimal':
                    user_base = [self.handlers.users.get_by_id(i) for i in rec_at_date]
                for user in user_base:
                    try:
                        self.generate_recommendations(user, date, upper, lower, rg)
                    except KeyError:
                        print("Help, a Key Error occurred!")
                        continue
        # self.generate_reading_histories()

    def execute_tsv(self):
        # for JSON
        lstur = []
        file = open('data/recommendations/lstur_pred_small.json')
        for line in file:
            json_line = json.loads(line)
            lstur.append(json_line)
        #
        naml = []
        file = open('data/recommendations/naml_pred_small.json')
        for line in file:
            json_line = json.loads(line)
            naml.append(json_line)

        npa = []
        file = open('data/recommendations/npa_pred_small.json')
        for line in file:
            json_line = json.loads(line)
            npa.append(json_line)

        nrms = []
        file = open('data/recommendations/nrms_pred_small.json')
        for line in file:
            json_line = json.loads(line)
            nrms.append(json_line)

        pop = []
        file = open('data/recommendations/pop_pred_small.json')
        for line in file:
            json_line = json.loads(line)
            pop.append(json_line)

        behavior_file = open('data/recommendations/behaviors_small.tsv')
        behaviors_csv = csv.reader(behavior_file, delimiter="\t")
        behaviors = []
        for line in behaviors_csv:
            behaviors.append(line)

        for (a, b, c, d, e, f) in zip(behaviors, lstur, npa, naml, nrms, pop):
            impression_index = a[0]
            userid = a[1]
            date = datetime.strptime(a[2], "%m/%d/%Y %I:%M:%S %p")
            items = a[4].strip().split(" ")
            lstur_row = b['pred_rank']
            npa_row = c['pred_rank']
            naml_row = d['pred_rank']
            nrms_row = e['pred_rank']
            pop_row = f['pred_rank']
            npa_list = []
            lstur_list = []
            naml_list = []
            nrms_list = []
            random_list = []
            pop_list = []
            for x in range(1, min(5, len(items) + 1)):
                try:
                    npa_list.append(
                        self.handlers.articles.get_field_with_value('newsid', items[npa_row.index(x)].split("-")[0])[0].id)
                    lstur_list.append(self.handlers.articles.get_field_with_value('newsid', items[lstur_row.index(x)].split("-")[0])[0].id)
                    naml_list.append(self.handlers.articles.get_field_with_value('newsid', items[naml_row.index(x)].split("-")[0])[0].id)
                    nrms_list.append(self.handlers.articles.get_field_with_value('newsid', items[nrms_row.index(x)].split("-")[0])[0].id)
                    pop_list.append(self.handlers.articles.get_field_with_value('newsid', items[pop_row.index(x)].split("-")[0])[0].id)
                    random_index = random.randint(0, len(items))
                    random_list.append(
                        self.handlers.articles.get_field_with_value('newsid', items[random_index].split("-")[0])[0].id)
                except IndexError:
                    pass
            lstur_recommendation = {'impr_index': impression_index, 'userid': userid, 'type': 'lstur', 'date': date, 'articles': lstur_list}
            npa_recommendation = {'impr_index': impression_index, 'userid': userid, 'type': 'npa', 'date': date,
                                  'articles': npa_list}
            naml_recommendation = {'impr_index': impression_index, 'userid': userid, 'type': 'naml', 'date': date, 'articles': naml_list}
            nrms_recommendation = {'impr_index': impression_index, 'userid': userid, 'type': 'nrms', 'date': date, 'articles': nrms_list}
            pop_recommendation = {'impr_index': impression_index, 'userid': userid, 'type': 'pop', 'date': date, 'articles': pop_list}

            random_recommendation = {'impr_index': impression_index, 'userid': userid, 'type': 'random', 'date': date,
                                     'articles': random_list}
            self.handlers.recommendations.add_recommendation(lstur_recommendation, 'lstur')
            self.handlers.recommendations.add_recommendation(npa_recommendation, 'npa')
            self.handlers.recommendations.add_recommendation(naml_recommendation, 'naml')
            self.handlers.recommendations.add_recommendation(nrms_recommendation, 'nrms')
            self.handlers.recommendations.add_recommendation(pop_recommendation, 'pop')
            self.handlers.recommendations.add_recommendation(random_recommendation, 'random')


