from flask import Flask
from flask import Response
from flask import jsonify
from flask.ext.cors import CORS, cross_origin
import json
import csv
import pandas as pd
import numpy as np
import traceback

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
config = None
data = None
index = "storetime"
resource = "icustay_id"

def init():
	global config
	global data
	data = None
	with open("config.json") as json_config:
		config = json.load(json_config)
	for file in config["files"]:
		df = pd.read_csv(file["file_name"])
		if data is None:
			data = df
		else:
			data = data.append(df)
	data.sort([index], ascending=[True])
	data[index] = pd.to_datetime(data[index])
	data["returned"] = 0

@app.route("/")
def main():
	return "Welcome to ICU Prediction Simulator!"
	
@app.route("/drive/rest/enrichment_manager/entity_profile/get/Patient/<value>")
@cross_origin()
def getSubject(value):
	try:
		idx = data.loc[(data["returned"] == 0) & (data[resource] == float(value))].index.tolist()
		resp = None
		if len(idx) :
			data.set_value(idx[0], "returned", 1)
			respDict = {}
			respDict["name"] = "sepsisPrediction"
			valDict = {}
			valDict["boolList"] = []
			valDict["double"] = data.iloc[idx[0]]["risk_score"]
			valDict["doubleList"] = []
			valDict["integerList"] = []
			valDict["longList"] = []
			valDict["stringList"] = []
			respDict["singleValue"] = valDict
			#resp = Response(response=data.iloc[idx[0]].to_json(), status=200, mimetype="application/json")
			resp = jsonify(respDict)
		else :
			resp = jsonify({})
		return(resp)
	except Exception as e:
		traceback.print_exc()
		return "Internal Error :: " + str(e), 500

if __name__ == "__main__":
	init()
	app.run(host= '0.0.0.0', port=int(config["port"]), threaded=True)