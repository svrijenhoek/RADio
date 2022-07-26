import networkx as nx
import community
import pandas as pd
import itertools
from difflib import SequenceMatcher
from collections import defaultdict


class Clustering:

    def __init__(self, threshold, a, b, metric):
        self.threshold = threshold
        self.a = a
        self.b = b
        self.metric = metric

    @staticmethod
    def distance(names):
        """
        Calculates the distance between each name.
        If the label has less than three characters, skip
        If a is contained in b or the other way around (as in "Barack Obama", "Obama"), full match

        Otherwise calculate the SequenceMatcher ratio to account for slight spelling errors
        """

        output = []
        for a, b in itertools.combinations(names, 2):
            if len(a) < 3 or len(b) < 3:
                similarity = 0
            elif a in b or b in a:
                similarity = 1
            else:
                similarity = SequenceMatcher(None, a, b).ratio()
            output.append({'a': a, 'b': b, 'metric': similarity})
        return output

    def cluster(self, distances):
        """
        Cluster the names based on the distances found
        Lower thresholding will result in higher recall, but also lower precision.
        """
        if distances:
            df = pd.DataFrame(distances)
            thr = df[df.metric > self.threshold]
            G = nx.from_pandas_edgelist(thr, self.a, self.b, edge_attr='metric')
            partition = community.best_partition(G)
            return partition
        else:
            return {}

    @staticmethod
    def process(names, clusters):
        """
        Add all unique clusters that only occurred once to the result set
        """
        if clusters:
            v, k = max((v, k) for k, v in clusters.items())
            length = v + 1
        else:
            length = 0
        output = {}
        for name in names:
            if name in clusters:
                output[name] = clusters[name]
            else:
                output[name] = length
                length += 1

        d = defaultdict(list)
        for k, v in output.items():
            d[v].append(k)
        return dict(d)

    def execute(self, entities):
        if entities:
            output = []
            # group all entities of the same type
            types = list(set([x['label'] for x in entities]))
            for entity_type in types:
                of_type = [entity for entity in entities if entity['label'] == entity_type]
                names = [entity['text'] for entity in of_type]
                # calculate the distances between all the entity names
                distances = self.distance(names)
                # based on all the distances, cluster the entities
                clusters = self.cluster(distances)
                # assign each name to a cluster (cluster length 1 if none was identified)
                processed = self.process(names, clusters)
                for _, v in processed.items():
                    # find all entries of this cluster
                    with_name = [entity for entity in of_type if entity['text'] in v]
                    # find all unique occurrences of the cluster
                    all_names = [entity['text'] for entity in with_name]
                    label = with_name[0]['label']
                    # find the name that was most often used to refer to this cluster
                    most_frequent_name = max(set(all_names), key=all_names.count)
                    # if the cluster is about people names, favor names that contain a space
                    # eg: Barack Obama over just Obama
                    if label == 'PER' or label == 'PERSON':
                        with_space = [name for name in all_names if len(name.split(" ")) > 1]
                        if len(with_space) > 0:
                            most_frequent_name = max(set(with_space), key=with_space.count)
                    alternative_names = v
                    spans = [(entity['start_char'], entity['end_char']) for entity in with_name]
                    output.append({'text': most_frequent_name, 'alternative': alternative_names, 'frequency': len(with_name),
                                   'spans': spans, 'label': label})
            return output
        else:
            return []
