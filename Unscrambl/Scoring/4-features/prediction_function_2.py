def predict(tup):
    from sklearn.externals import joblib
    import numpy as np
    import pickle
    import math
    #Load random forest model
    rf = joblib.load('random_forests_CE_2.pkl')
    
    #Create query vector
    arr = np.zeros((1,4))[0]
    for i in range(4):
        arr[i] = tup[i+4]
    arr = np.array(arr)
    
    #return prediction as probability of sepsis in 8 hours
    preds = rf.predict_proba(arr)[:,1]
    return preds[0]


id0 = 220052
id1 = 224690
id2 = 223761
id3 = 220277
rate0 = 43
rate1 = 23
rate2 = 72
rate3 = 90

if __name__ == "__main__":
    tup = (id0,id1,id2,id3,rate0,rate1,rate2,rate3)
    pred = predict(tup)
    print(pred)
