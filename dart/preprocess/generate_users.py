import json
import os
import pandas as pd
import dart.Util as Util


class UserSimulator:

    def __init__(self, config, handlers):
        self.config = config
        self.handlers = handlers
        self.queue = []

    def execute_legacy(self):
        for path, _, files in os.walk(self.folder):
            for name in files:
                # assumes all files are json-l, change this to something more robust!
                for line in open((os.path.join(path, name))):
                    json_doc = json.loads(line)
                    json_doc['_id'] = json_doc['id']
                    if self.alternative_schema == "Y":
                        json_doc = Util.transform(json_doc, self.schema)
                    if json_doc['reading_history']:
                        if self.user_reading_history_based_on == "title":
                            json_doc['reading_history'] = \
                                {'base': self.reading_history_to_ids(json_doc['reading_history'])}
                    else:
                        json_doc['reading_history'] = {'base': []}
                    self.handlers.users.add_user(json_doc)

    def execute(self, file_location):
        tsv_file = open(file_location, encoding="utf-8")
        df = pd.read_table(tsv_file, names=["id", "userid", "timestamp", "reading_history", "interactions"])
        userids = df.userid.unique()
        for userid in userids:
            user_sessions = df[df.userid == userid]
            try:
                hist = user_sessions.iloc[0].reading_history.split(" ")
                reading_history = []
                for entry in hist:
                    try:
                        reading_history.append(self.handlers.articles.get_field_with_value('newsid', entry)[0].id)
                    except IndexError:
                        pass
            except AttributeError:
                try:
                    reading_history = [self.handlers.articles.get_field_with_value('newsid', user_sessions.iloc[0].reading_history)]
                except IndexError:
                    pass
            interactions = {}
            for _, row in user_sessions.iterrows():
                interactions[row.timestamp] = row.interactions
            json_doc = {
                'userid': userid,
                'reading_history': reading_history,
                'interactions': interactions
            }
            self.handlers.users.add_user(json_doc)

