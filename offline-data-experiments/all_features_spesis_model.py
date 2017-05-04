###################################################
## Python File version of the notebook by same name
###################################################

import sklearn 
import numpy as np 
import pandas as pd 
from datetime import datetime
from sklearn.cross_validation import train_test_split
from sklearn.ensemble import RandomForestClassifier


def load_data(path1,path2,path3):
    df_icu_stays = pd.read_csv(path1)
    df_sepsis_occurance = pd.read_csv(path2)
    df_events = pd.read_csv(path3)
    return df_icu_stays, df_sepsis_occurance, df_events

path1 = 'm100s2/ICUSTAYS.csv'
path2 = 'm100s2/sample_ids_2.csv'
path3 = 'm100s2/sample_inputevents_mv_2.csv'

df_icu_stays, df_sepsis_occurance, df_events = load_data(path1,path2,path3)

def join_data(df_events,df_sepsis_occurance): 
    df = pd.merge(df_events, df_sepsis_occurance, on='hadm_id', how='inner')
    return df

df_joined = join_data(df_events, df_sepsis_occurance)

#Convert columns to datetime objects 
df_joined['sepsist0'] = df_joined['sepsist0'].apply(lambda i: datetime.strptime(i,'%Y-%m-%d %H:%M:%S'))
df_joined['starttime'] = df_joined['starttime'].apply(lambda i: datetime.strptime(i,'%Y-%m-%d %H:%M:%S'))

#Create time difference in hours column between sepsis t0 and starttime
df_joined['time_diff'] = (df_joined['sepsist0'] - df_joined['starttime'])
df_joined['time_diff'] = df_joined['time_diff'].apply(lambda i: i.seconds/3600)

hours = 5
#1 if developed sepsis with 8 hours else 0
df_joined['curr_sepsis'] = df_joined['time_diff'].apply(lambda i: 1 if i <= hours else 0)

#Creating the sparse rate feature vectors
all_items = df_joined['itemid'].values
all_rates = df_joined['rate'].values
all_y = df_joined['curr_sepsis']
item_ids = list(set(df_joined['itemid'].values)) 
remap_items = range(len(item_ids))
dict_items = dict(zip(item_ids,remap_items))
item_ids = list(set(df_joined['itemid'].values)) 
item_id_feature = np.zeros((df_joined.shape[0],len(item_ids)))
x = []
y = []
for i in range(all_items.shape[0]): 
    val = all_items[i]
    rate = all_rates[i]
    remap_val = dict_items[val]
    z = np.zeros((1,len(item_ids)))[0]
    z[remap_val] = rate
    x.append(z)
    y.append(all_y[i])
rate_feat_x = np.array(x)
y = np.array(y)

#Removing rows with NaNs
nan_index = np.argwhere(np.isnan(rate_feat_x))
nan_rows = []
for i in nan_index: 
    nan_rows.append(i[0])
rate_feat_x = np.delete(rate_feat_x,nan_rows,0)
rate_feat_y = np.delete(y,nan_rows,0)

Rxtrain, Rxtest, Rytrain, Rytest = train_test_split(rate_feat_x, rate_feat_y, test_size=0.20)

rf = RandomForestClassifier(n_estimators= 25, max_depth= None,random_state= 11 )
rf.fit(Rxtrain, Rytrain)
Rprediction = rf.predict(Rxtest)

from sklearn.externals import joblib
# now you can save it to a file
joblib.dump(rf, 'random_forest.pkl') 
# and later you can load it
rf = joblib.load('random_forest.pkl')
