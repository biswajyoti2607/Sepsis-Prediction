##############################################
## Python File to run analysis on the features
##############################################

import sklearn 
import numpy as np 
import pandas as pd 
from matplotlib import pyplot as plt
from datetime import datetime
from sklearn.cross_validation import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score 
from sklearn.externals import joblib


def load_data(path1,path2,path3):
	df_icu_stays = pd.read_csv(path1)
	df_sepsis_occurance = pd.read_csv(path2)
	df_events = pd.read_csv(path3)
	return df_icu_stays, df_sepsis_occurance, df_events

def join_data(df_events,df_sepsis_occurance): 
	return pd.merge(df_events, df_sepsis_occurance, on='hadm_id', how='inner')

def get_features(df_joined):
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
	return rate_feat_x, rate_feat_y

#Here we select our features and drop NaNs
def filter_features(df,features,pred_label):
	all_feats = features+pred_label
	new_df = df[all_feats]
	new_df = new_df.dropna(axis=0)
	new_x = new_df[features]
	new_y = new_df[pred_label]
	return new_x, new_y 

def get_random_forest_model(Rxtrain, Rytrain):
	seed = 7
	rf = RandomForestClassifier(n_estimators= 25, max_depth= None,random_state=seed)
	rf.fit(Rxtrain, Rytrain)
	Rprediction = rf.predict(Rxtest)
	acc = accuracy_score(Rytest,Rprediction)
	return rf, acc

def viz(dataset):
	import matplotlib.pyplot as plt
	num_features = len(dataset.columns)
	# 3. Analyze Data
	## Descriptive Statistics
	print ('Descriptive Statistics')
	print ('Dataset Dimensions ' + str(dataset.shape)) # 208 rows, 61 attributes including class
	## Data types of each attribute
	pd.set_option('display.max_rows', 500)
	print ('Data Types of each Attribute\n' + str(dataset.dtypes))
	## Peek at first 20 rows of data
	pd.set_option('display.width', 100)
	print ('First 20 rows of data\n' + str(dataset.head(20)))
	## Summarize the distribution of each attribute
	pd.set_option('precision', 3)
	print ('Distribution of each Attribute\n' + str(dataset.describe()))
	## Distribution of Class Values
	# print ('Class Distribution\n' + str(dataset.groupby(num_features-1).size()))
	## Unimodal Data Visualizations
	### Histograms
	dataset.hist(sharex=False, sharey=False, xlabelsize=1, ylabelsize=1)
	plt.show()
	### Density Plots
	# dataset.plot(kind='density', subplots=True, layout=(num_features,num_features), sharex=False, legend=False, fontsize=1)
	# plt.show()
	### box and whisker plots
	# dataset.plot(kind='box', subplots=True, layout=(num_features,num_features), sharex=False, sharey=False, fontsize=1)
	# plt.show()
	## Multimodal Data Visualizations
	### correlation matrix
	fig = plt.figure()
	ax = fig.add_subplot(111)
	corr = dataset.corr()
	cax = ax.matshow(corr, vmin=-1, vmax=1, interpolation='none')
	fig.colorbar(cax)

	corr = dataset[dataset.columns[:-1]].apply(lambda x: x.corr(dataset[dataset.columns[len(dataset.columns)-1]]))
	cax = ax.matshow(corr, vmin=-1, vmax=1, interpolation='none')
	fig.colorbar(cax)
	plt.show()



def generate_item_ids(df_joined):
	#Creating the sparse rate feature vectors
	all_items = df_joined['itemid'].values
	all_rates = df_joined['rate'].values
	all_y = df_joined['curr_sepsis']
	item_ids = list(set(df_joined['itemid'].values)) 
	remap_items = range(len(item_ids))
	dict_items = dict(zip(item_ids,remap_items))
	dump_dict_items(dict_items)
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
	
	# rate_feat = np.append(rate_feat_x, rate_feat_y, axis=0)
	rate_feat = np.c_[rate_feat_x, rate_feat_y]
	df = pd.DataFrame(data=rate_feat[:,:])
	return df

def dump_dict_items(df):
	from sklearn.externals import joblib
	# now you can save it to a file
	joblib.dump(df, 'dict_items.p') 

if __name__ == "__main__":
	seed = 7

	path1 = 'm100s2/ICUSTAYS.csv'
	path2 = 'm100s2/sample_ids_2.csv'
	path3 = 'm100s2/sample_inputevents_mv_2.csv'

	df_icu_stays, df_sepsis_occurance, df_events = load_data(path1,path2,path3)
	df_joined = join_data(df_events, df_sepsis_occurance)

	#Convert columns to datetime objects 
	df_joined['sepsist0'] = df_joined['sepsist0'].apply(lambda i: datetime.strptime(i,'%Y-%m-%d %H:%M:%S'))
	df_joined['starttime'] = df_joined['starttime'].apply(lambda i: datetime.strptime(i,'%Y-%m-%d %H:%M:%S'))

	#Create time difference in hours column between sepsis t0 and starttime
	df_joined['time_diff'] = (df_joined['sepsist0'] - df_joined['starttime'])
	df_joined['time_diff'] = df_joined['time_diff'].apply(lambda i: i.seconds/3600)



	# Set Window Size
	accs = []
	hours = [8]
	for j in range(len(hours)):

		#1 if developed sepsis with 8 hours else 0
		df_joined['curr_sepsis'] = df_joined['time_diff'].apply(lambda i: 1 if i <= hours[j] else 0)

		df_joined = generate_item_ids(df_joined)
			
		# viz(df_joined)

	# 	rate_feat_x, rate_feat_y = get_features(df_joined)

	# 	Rxtrain, Rxtest, Rytrain, Rytest = train_test_split(rate_feat_x, rate_feat_y, test_size=0.20, random_state=seed)
		
	# 	model, acc = get_random_forest_model(Rxtrain, Rytrain)
	# 	print (str(hours[j]) + ' => ' + str(acc))
	# 	accs.append(acc)
	# plt.plot(hours, accs)
	# plt.show()