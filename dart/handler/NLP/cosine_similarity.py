from dart.handler.elastic.connector import ElasticsearchConnector
import math
import itertools
import numpy as np
import collections, functools, operator
from stop_words import get_stop_words
from statistics import StatisticsError


# basically copied from https://www.datasciencecentral.com/profiles/blogs/
# document-similarity-analysis-using-elasticsearch-and-python
class CosineSimilarity:

    def __init__(self, language):
        self.connector = ElasticsearchConnector()
        self.stop_words = get_stop_words(language)
        self.term_vectors = {}

    def create_dictionary(self, doc):
        output = {}
        try:
            # count the total number of terms in document
            sum_terms = sum([v['term_freq'] for k, v in doc.get('term_vectors').get('text').get('terms').items()])
            # gets the total number of documents with the text field
            # this number seems to be wrong though? as if it performs on a subset of docs. However, for now we assume that
            # proportions are similar to reality.
            total_docs = doc.get('term_vectors').get('text').get('field_statistics')['doc_count']
            for k, v in doc.get('term_vectors').get('text').get('terms').items():
                if k not in self.stop_words:
                    term_freq = v['term_freq']/sum_terms
                    doc_freq = v['doc_freq']
                    inverse_document_freq = 1.0 + math.log(total_docs / doc_freq)
                    output[k] = term_freq * inverse_document_freq
        except AttributeError:
            pass
        return output

    def most_relevant_terms(self, doclist):
        tv1 = [self.connector.get_term_vector('articles', doc) for doc in doclist]
        dict1 = [self.create_dictionary(tv) for tv in tv1]
        merged1 = dict(functools.reduce(operator.add,
                                        map(collections.Counter, dict1)))
        sorted_x = sorted(merged1.items(), key=lambda kv: kv[1], reverse=True)
        output = [x[0] for x in sorted_x[:5]]
        return output

    @staticmethod
    def cosine(vec1, vec2):
        intersection = set(vec1.keys()) & set(vec2.keys())
        numerator = sum([vec1[x] * vec2[x] for x in intersection])
        sum1 = sum([vec1[x]**2 for x in vec1.keys()])
        sum2 = sum([vec2[x]**2 for x in vec2.keys()])
        denominator = math.sqrt(sum1) * math.sqrt(sum2)
        if not denominator:
            return 0.0
        else:
            return float(numerator) / denominator

    def prepare_vector(self, doc):
        if doc in self.term_vectors:
            return self.term_vectors[doc]
        else:
            tv = self.connector.get_term_vector('articles', doc)
            if 'term_vectors' in tv and 'text' in tv['term_vectors']:
                vector = self.create_dictionary(tv)
                self.term_vectors[doc] = vector
                return vector

    def calculate_cosine_similarity(self, doc1, doc2):
        v1 = self.prepare_vector(doc1)
        v2 = self.prepare_vector(doc2)
        if v1 and v2:
            return self.cosine(v1, v2)
        else:
            return 0

    def prepare_vectors(self, doclist):
        output = []
        for doc in doclist:
            if doc in self.term_vectors:
                output.append(self.term_vectors[doc])
            else:
                tv = self.connector.get_term_vector('articles', doc)
                if 'term_vectors' in tv and 'text' in tv['term_vectors']:
                    vector = self.create_dictionary(tv)
                    output.append(vector)
                    self.term_vectors[doc] = vector
        return output

    # def calculate_cosine_similarity(self, list1, list2):
    #     try:
    #         vectors1 = self.prepare_vectors(list1)
    #         vectors2 = self.prepare_vectors(list2)
    #
    #         if vectors1 and vectors2:
    #             output = []
    #             for _, x in enumerate(vectors1):
    #                 for _, y in enumerate(vectors2):
    #                     cosine = self.cosine(x, y)
    #                     output.append(cosine)
    #             return median(output)
    #         else:
    #             return 0
    #     except (AttributeError, TypeError):
    #         print("Error!")
    #         print(list1)
    #         print(list2)
    #     except StatisticsError:
    #         return 0

    def calculate_all(self, doc_list):
        try:
            vectors = self.prepare_vectors(doc_list)
            output = []
            for x, y in itertools.combinations(vectors, 2):
                cosine = self.cosine(x, y)
                output.append(cosine)
            return np.mean(output), np.std(output)
        except StatisticsError:
            return 0

    # def calculate_all_distances(self, doc_list):
    #     dict_list = self.prepare_vectors(doc_list)
    #     output = []
    #     for ix, x in enumerate(dict_list):
    #         for iy, y in enumerate(dict_list):
    #             if ix > iy:
    #                 cosine = self.cosine(x, y)
    #                 output.append({'x': doc_list[ix], 'y': doc_list[iy], 'cosine': cosine})
    #     return output

    # def calculate_cosine_experiment(self, list1, list2):
    #     vector1 = self.prepare_vectors(list1)
    #     merged1 = dict(functools.reduce(operator.add,
    #                                     map(collections.Counter, vector1)))
    #     vector2 = self.prepare_vectors(list2)
    #     merged2 = dict(functools.reduce(operator.add,
    #                                     map(collections.Counter, vector2)))
    #     return self.cosine(merged1, merged2)
