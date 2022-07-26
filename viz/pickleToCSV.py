import pandas as pd
import numpy as np
import pickle
from pathlib import Path
import os

## JS

d = pd.read_pickle("../../data/output.pickle")

columns = list(d.columns)[2:9]
for i, column in enumerate(columns):
    _, d[column], _  = d[column].str

# root JS
d.iloc[:,2:8] = d.iloc[:,2:8].apply(np.sqrt)
    
# d.iloc[:,0:8].groupby('rec_type', as_index=False).mean() * 100

# pd.options.display.float_format = '{:.2}%'.format

pd.options.display.float_format = '{:.2f}'.format

meanTable = d.iloc[:,0:8].groupby('rec_type', as_index=False).mean()
meanTable.iloc[:, 1:7] = meanTable.iloc[:, 1:7].mul(100)
print("\n" + meanTable.to_latex(index = False))
meanTable.to_pickle("meanTable.pickle")

medianTable = d.iloc[:,0:8].groupby('rec_type', as_index=False).median()


    
d.iloc[:,0:8].to_csv("../../data/output.csv")


## KL

d = pd.read_pickle("../../data/output.pickle")

columns = list(d.columns)[2:9]
for i, column in enumerate(columns):
    d[column], _ , _  = d[column].str

pd.options.display.float_format = '{:.2f}'.format

meanTable = d.iloc[:,0:8].groupby('rec_type', as_index=False).mean()
#meanTable.iloc[:, 1:7] = meanTable.iloc[:, 1:7].mul(100)
print("\n" + meanTable.to_latex(index = False))
meanTable.to_pickle("meanTableKL.pickle")

meanTable = pd.read_pickle("meanTableKL.pickle")
meanTable.to_csv("meanTableKL.csv")

medianTable = d.iloc[:,0:8].groupby('rec_type', as_index=False).median()


    
d.iloc[:,0:8].to_csv("../../data/outputKL.csv")



from functools import partial

class Infix(object):
    def __init__(self, func):
        self.func = func
    def __or__(self, other):
        return self.func(other)
    def __ror__(self, other):
        return Infix(partial(self.func, other))
    def __call__(self, v1, v2):
        return self.func(v1, v2)

@Infix
def add(a,b):
    return a + b
    
10 |add| 4
