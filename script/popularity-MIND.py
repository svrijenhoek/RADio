# Databricks notebook source
import datetime
import time
import numpy as np
import pyspark.sql.functions as F
from pyspark.sql.types import *
from pyspark.sql import Row
from pyspark.sql.window import Window
import math

from pyspark.ml.recommendation import ALS

from pyspark.sql import SparkSession
spark = SparkSession.builder.appName('recommendations-DEV-MIND').getOrCreate()


# COMMAND ----------

def read_data(path):
    myschema = StructType([
        StructField('index', IntegerType(), True),
        StructField('user', StringType(), True),
        StructField('datetime', StringType(), True),
        StructField('behavior_string', StringType(), True),
        StructField('preselection_string', StringType(), True)
    ])
    
    behaviors_presel_df = spark.read.csv(path, sep="\t", schema=myschema)#.drop('index')
    behaviors_presel_df = behaviors_presel_df.withColumn('behavior_array', F.split(F.col('behavior_string'),' ')).drop('behavior_string')
    behaviors_presel_df = behaviors_presel_df.withColumn('preselection_array', F.split(F.col('preselection_string'),' ')).drop('preselection_string')
#     behaviors_presel_df = behaviors_presel_df.withColumn('user_id', F.split(F.col('user'),'U').getItem(1).cast(IntegerType()))#.drop('user')
    
    behaviors_df = behaviors_presel_df.select('user', 'behavior_array', 'index')
#     behaviors_df = behaviors_df.withColumn('user_id', F.split(F.col('user'),'U').getItem(1).cast(IntegerType())).drop('user')
    behaviors_df = behaviors_df.withColumn('item', F.explode('behavior_array')).drop('behavior_array')
    behaviors_df = behaviors_df.withColumn('item_id', F.split(F.col('item'),'N').getItem(1).cast(IntegerType())).drop('item')
    behaviors_df = behaviors_df.withColumn('rating', F.lit(1).cast(IntegerType()))
    
    preselection_df = behaviors_presel_df.select('user', 'preselection_array', 'index')
#     preselection_df = preselection_df.withColumn('user_id', F.split(F.col('user'),'U').getItem(1).cast(IntegerType())).drop('user')
    preselection_df = preselection_df.withColumn('item', F.explode('preselection_array')).drop('preselection_array')
    preselection_df = preselection_df.withColumn('success', F.split(F.col('item'),'-').getItem(1).cast(IntegerType()))
    preselection_df = preselection_df.withColumn('item_id', 
                                     F.split(F.split(F.col('item'),'-').getItem(0),'N').getItem(1).cast(IntegerType()))#.drop('item')
    
    return behaviors_presel_df, behaviors_df, preselection_df


def rank_preselection_by_popularity(path_train, behaviors_df, preselection_df):
    _, behaviors_train_df, preselection_train_df = read_data(path_train)
    items_popularity_df = behaviors_train_df.union(behaviors_df).groupby('item_id').agg(F.count('item_id').alias('popularity')).sort(F.desc('popularity'))
    # add the items in preselection_df that were not in behaviors_df with a 0 popularity
    items_popularity_df = items_popularity_df.join(preselection_df.select('item_id').distinct(), 
                                                   'item_id', how='full').fillna(0)
    
    
    preselection_pop_df = preselection_df.join(items_popularity_df, 'item_id')
    
    preselection_pop_df = preselection_pop_df.withColumn('rank', F.row_number().over(Window.partitionBy('user', 'index').orderBy(F.desc('popularity'))))
    preselection_pop_df = preselection_pop_df.withColumn('dic', F.create_map(['item', 'rank']))\
                                             .drop('item_id')\
                                             .drop('rank')\
                                             .drop('popularity')\
                                             .drop('success')
    preselection_pop_df = preselection_pop_df.groupby('user', 'index').agg(F.collect_list('dic').alias('dic_list'))
    preselection_pop_df = preselection_pop_df.orderBy(['index', 'user'], ascending=[1,1])
    return items_popularity_df, preselection_pop_df


def get_pred_rank_per_row(x,y):
    one_dic = {k: v for d in x for k, v in d.items()}
    val = [one_dic[ele] if ele in one_dic.keys() else -1 for ele in y]
    return val


def get_pred_rank(preselection_pop_df, behaviors_presel_df):
#     result = preselection_pop_df.join(behaviors_presel_df.select('index', 'user', 'preselection_array'), ['index', 'user'])
    result = preselection_pop_df.join(behaviors_presel_df.select('index', 'preselection_array'), ['index'])
#     result = result.orderBy(['index'], ascending=[1])
    result = result.withColumn('pred_rank', F.udf(lambda x,y: get_pred_rank_per_row(x,y), ArrayType(IntegerType()))('dic_list', 'preselection_array'))
    result = result.drop('dic_list').drop('preselection_array')#.drop('user')
    result = result.withColumnRenamed('index', 'impr_index')
    result = result.sort(F.col('impr_index'))
    return result


def run(path_prefix, path_results, path_train):
    behaviors_presel_df, behaviors_df, preselection_df = read_data(path_prefix)
    items_popularity_df, preselection_pop_df = rank_preselection_by_popularity(path_train, behaviors_df, preselection_df)
    result = get_pred_rank(preselection_pop_df, behaviors_presel_df)
    result.repartition(1).write.json(path_results, mode='overwrite')
    return result, items_popularity_df
    

# COMMAND ----------

sufix = 'small'

PATH_PREFIX = 's3://ci-data-apps/mateo/MIND/behaviors_'+sufix+'.tsv'
PATH_TRAIN = 's3://ci-data-apps/mateo/MIND/behaviors_'+sufix+'_train.tsv'
PATH_RESULTS = 's3://ci-data-apps/mateo/MIND/pop_pred_'+sufix+'.json'

result, items_popularity_df = run(PATH_PREFIX, PATH_RESULTS, PATH_TRAIN)
display(result)

# COMMAND ----------

def train_ALS_model(df, rank, alpha, reg_par, max_iter):
    """ Trains the ALS model based on the implicit ratings created.
    http://www.yifanhu.net/PUB/cf.pdf
    Parameters
      df: a dataframe with the (unique) user-item interactions and their implicit ratings.
      rank: the rank of the lower dimension matrices X,Y to be learn to factorise the implicit ratings R (R = X'Y).
      alpha: the alpha parameter for the implicit feedback ALS version.
      reg_par: the regularization parameter for the ALS.
      max_iter: the maximum number of iterations before stopping.
    Returns
      model: the trained ALS model.
      als: the ALS object.
    """
    als = ALS(maxIter=max_iter, regParam=reg_par, rank=rank, implicitPrefs=True, alpha=alpha, userCol='index', itemCol='item_id', ratingCol='rating')
    model = als.fit(df)
    return model, als


def run_ALS(path_prefix, path_results, path_train, nr_predictions=300):
    behaviors_presel_df, behaviors_df, preselection_df = read_data(path_prefix)
    _, behaviors_train_df, preselection_train_df = read_data(path_train)
    max_index_behaviors_df = behaviors_df.groupby().max('index').first().asDict()['max(index)']  
    behaviors_train_df = behaviors_train_df.withColumnRenamed('index', 'i2')\
                                           .withColumn('index', F.col('i2') + max_index_behaviors_df)\
                                           .drop('i2')
    behaviors_train_df = behaviors_train_df.cache()
    behaviors_df_train = behaviors_train_df.select('index', 'item_id', 'rating', 'user').union(behaviors_df.select('index', 'item_id', 'rating', 'user'))

    model, als = train_ALS_model(behaviors_df_train, rank=100, alpha=10, reg_par=0.1, max_iter=10)
    
    index_subset = behaviors_df_train.filter(F.col('index') <= max_index_behaviors_df)

    index_recs = model.recommendForUserSubset(index_subset, nr_predictions)
    indexitem_recs_df = index_recs.select('index', F.explode(index_recs.recommendations))

    indexitem_df = indexitem_recs_df.select('index', F.col('col.item_id').alias('item_id'), F.col('col.rating').alias('prediction'))

    indexitem_predictions_df = indexitem_df.join(preselection_df.select('item_id', 'index', 'item').distinct(),['item_id', 'index'], how='inner')

    indexitem_predictions_df = indexitem_predictions_df.withColumn('rank', F.row_number().over(Window.partitionBy('index').orderBy(F.desc('prediction'))))
    indexitem_predictions_df = indexitem_predictions_df.withColumn('dic', F.create_map(['item', 'rank']))\
                                                       .select('index', 'dic')
    indexitem_predictions_df = indexitem_predictions_df.groupby('index').agg(F.collect_list('dic').alias('dic_list'))

    result = get_pred_rank(indexitem_predictions_df, behaviors_presel_df)
    
    result.repartition(1).write.json(path_results, mode='overwrite')
    return result, model

# COMMAND ----------

sufix = 'small'

PATH_PREFIX = 's3://ci-data-apps/mateo/MIND/behaviors_'+sufix+'.tsv'
PATH_TRAIN = 's3://ci-data-apps/mateo/MIND/behaviors_'+sufix+'_train.tsv'
PATH_RESULTS = 's3://ci-data-apps/mateo/MIND/als_pred_'+sufix+'.json'

path_prefix = PATH_PREFIX
path_train = PATH_TRAIN
path_results = PATH_RESULTS

result, model = run_ALS(path_prefix, path_results, path_train, nr_predictions=400)

display(result)


# COMMAND ----------



# COMMAND ----------



# COMMAND ----------



# COMMAND ----------



# COMMAND ----------

sufix = 'large'

PATH_PREFIX = 's3://ci-data-apps/mateo/MIND/behaviors_'+sufix+'.tsv'
PATH_TRAIN = 's3://ci-data-apps/mateo/MIND/behaviors_'+sufix+'_train.tsv'

path_prefix = PATH_PREFIX
path_train = PATH_TRAIN

behaviors_presel_df, behaviors_df, preselection_df = read_data(path_prefix)
_, behaviors_train_df, preselection_train_df = read_data(path_train)

# COMMAND ----------

display(behaviors_train_df)

# COMMAND ----------

display(preselection_df)

# COMMAND ----------

# small -> 33195
# large -> 79546
behaviors_train_df.select('item_id').distinct().count()

# COMMAND ----------

# small -> 37681
# large -> 66296
behaviors_df.select('item_id').distinct().count()

# COMMAND ----------

# small -> 5369
# large -> 6997
preselection_df.select('item_id').distinct().count()

# COMMAND ----------

# small -> 654
# large -> 1303
all_behaviors = behaviors_df.select('item_id').distinct().union(behaviors_train_df.select('item_id').distinct()).distinct()
join_pre_behaviors = preselection_df.select('item_id').distinct().join(all_behaviors, 'item_id')
join_pre_behaviors.select('item_id').distinct().count()

# COMMAND ----------



# COMMAND ----------



# COMMAND ----------


