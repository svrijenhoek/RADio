import dart.Util
import pandas as pd
from random import sample
import itertools
from dart.external.rbo import rbo


pd.set_option('display.float_format', '{:.5f}'.format)

config = dart.Util.read_full_config_file()
articles = dart.Util.read_pickle(config['articles'])
recommendations = dart.Util.read_pickle(config['recommendations'])
behavior_file = dart.Util.read_behavior_file(config['behavior_file'])
behavior_file = sample(behavior_file, 1000)
mod = round(len(behavior_file)/1000)

recommendation_types = ['lstur', 'naml', 'pop', 'random']

categories = {}

faults = 0


def recommendations_overlap():
    data = []
    for name, group in recommendations.groupby('impr_index'):
        for a, b in itertools.combinations(group.iterrows(), 2):
            if a[1]['articles'] and b[1]['articles']:
                overlap = rbo(a[1]['articles'], b[1]['articles'], 0.9)
                data.append([a[1]['type'], b[1]['type'], overlap.ext])
    results = pd.DataFrame(data)
    grouped = results.groupby([0, 1]).mean()
    print(grouped)


def retrieve_articles(newsids):
    categories_in_list = []
    for newsid in newsids:
        if newsid not in categories:
            try:
                categories[newsid] = articles.loc[articles['newsid'] == newsid].iloc[0].category
            except(IndexError, KeyError):
                pass
        try:
            categories_in_list.append(categories[newsid])
        except KeyError:
            pass
    return pd.Series(categories_in_list)
    #return articles[articles['newsid'].isin(newsids)]


def category_analysis():
    candidate_df = pd.DataFrame(columns=articles.category.unique())
    recommendation_df = pd.DataFrame(columns=articles.category.unique())
    history_df = pd.DataFrame(columns=articles.category.unique())

    for i, impression in enumerate(behavior_file):
        if i % 1000 == 0:
            print(i)
        impr_index = impression['impression_index']

        pool_articles = retrieve_articles([article for article in impression['items_without_click']])
        candidate_count = pool_articles.value_counts(normalize=True)
        candidate_count['impr_index'] = impr_index
        candidate_df = candidate_df.append(candidate_count, ignore_index=True)

        reading_history = retrieve_articles([_id for _id in impression['history']])
        history_count = reading_history.value_counts(normalize=True)
        history_count['impr_index'] = impr_index
        history_df = history_df.append(history_count, ignore_index=True)

        recommendation = recommendations.loc[impr_index]
        for rec_type in ['lstur', 'pop', 'random']:
            # recommendation = recommendations.loc[
            #     (recommendations['impr_index'] == impr_index) &
            #     (recommendations['type'] == rec_type)]
            recommendation_articles = retrieve_articles([_id for _id in recommendation[rec_type]])
            recommendation_count = recommendation_articles.value_counts(normalize=True)
            recommendation_count['rec_type'] = rec_type
            recommendation_count['impr_index'] = impr_index
            recommendation_df = recommendation_df.append(recommendation_count, ignore_index=True)

    history_df = history_df.set_index('impr_index')
    history_df = history_df.fillna(0)
    recommendation_df = recommendation_df.set_index('impr_index')
    recommendation_df = recommendation_df.fillna(0)
    candidate_df = candidate_df.set_index('impr_index')
    candidate_df = candidate_df.fillna(0)

    all = articles.category.value_counts(normalize=True)
    candidate_mean = candidate_df.mean().T
    history_mean = history_df.mean().T
    recommendations_mean = recommendation_df.groupby('rec_type').mean().T

    frames = [all, candidate_mean, history_mean, recommendations_mean]
    result = pd.concat(frames, axis=1)

    print(result)

    # print("====all====")

    # print(all)
    # print('===candidate===')
    # print(df.mean())
    # print('===recommendations===')
    # print(recommendation_df.groupby('rec_type').mean().T)
    # print('===history===')
    # print(history_df.mean().T)
    # print('===STD===')
    # print(df.std())
    # print(recommendation_df.groupby('rec_type').std().T)
    # print(history_df.std().T)


# recommendations_overlap()
category_analysis()





