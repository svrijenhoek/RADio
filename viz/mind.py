from recommenders.datasets import mind

from recommenders.datasets.download_utils import unzip_file

# hypers

item_sim_measure = "item_feature_vector" #"item_cooccurrence_count"

p = "../../data/"
trainName = "MINDlarge_train.zip"
devName = "MINDlarge_dev.zip"

mind.download_mind(size="large", dest_path=p)
# mind.extract_mind(train_zip=p+trainName,
#                   valid_zip=p+devName)
#                   train_folder=p+"train",
#                   valid_folder=p+"valid")
unzip_file(p+trainName, p+"train", clean_zip_file=False)
unzip_file(p+devName, p+"valid", clean_zip_file=False)

news_words, news_entities = mind.get_words_and_entities(p+"train/"+"news.tsv", p+"train/"+"news.tsv")


os.path.basename(p)

import pandas as pd

lstur = pd.read_json(p+"recommendations/lstur_pred_large.json", lines = True)

