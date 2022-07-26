from dart.models.Document import Document


class User(Document):

    def __init__(self, document):
        Document.__init__(self, document)
        self.reading_history = self.source['reading_history']
        try:
            self.id = self.source['userid']
            self.classification_preference = self.source['classification_preference']
            self.source_preference = self.source['source_preference']
            self.complexity_preference = self.source['complexity_preference']
            self.party_preference = self.source['party_preference']
        except KeyError:
            self.classification_preference = ''
            self.source_preference = ''
            self.complexity_preference = ''
            self.party_preference = ''

    # def select_reading_history(self, current_date, recommendation_type):
    #     """
    #     Given a user's reading history, a recommendation type and a date, extract that user's full reading history
    #     up to that date
    #     """
    #     current_date = datetime.strptime(current_date, '%Y-%m-%d')
    #     if recommendation_type in self.reading_history:
    #         relevant_history = self.reading_history[recommendation_type]
    #         dates = []
    #         # retrieve all the dates that are in the reading history
    #         for date in relevant_history:
    #             history_date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
    #             # only consider the recommendations before the current time
    #             if history_date < current_date:
    #                 dates.append(date)
    #         recommendations_of_type = []
    #         # append ids for all articles recommended before the current date
    #         for date in dates:
    #             for article in relevant_history[date]:
    #                 recommendations_of_type.append(article)
    #         # append the base reading history
    #         return self.reading_history['base'] + recommendations_of_type
    #     else:
    #         return self.reading_history['base']
