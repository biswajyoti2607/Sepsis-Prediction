###################################################
## Python File version of the notebook by same name
###################################################

from sklearn.externals import joblib
import numpy as np
import pickle
import math

def predict(tup):
    #tup is in form (id, rate)
    
    #Dictionary for lookup of id
    d = pickle.load( open( "dict_items.p", "rb" ) )
    indx = d[tup[0]]
    
    #Handle NaN
    if math.isnan(tup[1]): 
        tup = (tup[0],0)
        
    #Load random forest model 
    rf = joblib.load('random_forest.pkl')
    
    #Create query vector 
    arr = np.zeros((1,193))[0]
    arr[indx] = tup[1]
    
    #return prediction as probability of sepsis in 8 hours
    preds = rf.predict_proba(arr)[:,1]
    return preds[0]


id = 225843
rate = 43

if __name__ == "__main__":
	tup = (id,rate)
	pred = predict(tup)
	print(pred)