from flask import Flask
from flask import Response
from flask import jsonify
import json
import csv
import pandas as pd
import numpy as np
import traceback

app = Flask(__name__)
config = None
data = None
index = "time"
resource = "subject_id"

def init():
	global data
	global config
	data = None
	with open("config.json") as json_config:
		config = json.load(json_config)
	for file in config["files"]:
		df = pd.read_csv(file["file_name"])
		df.columns = df.columns.map(lambda x: file["file_id"] + "_" + str(x))
		df[index] = df[file["file_id"] + "_" + file["file_index"]]
		df[resource] = df[file["file_id"] + "_" + resource]
		if data is None:
			data = df
		else:
			data = pd.merge(data, df, on=[index, resource], how="outer")
	data.sort([index], ascending=[True])
	data[index] = pd.to_datetime(data[index])
	data["returned"] = 0

@app.route("/")
def main():
	return "Welcome to FHIR Simulator!"
	
@app.route("/subject/<value>")
def getSubject(value):
	try:
		idx = data.loc[(data["returned"] == 0) & (data[resource] == float(value))].index.tolist()
		resp = None
		if len(idx) :
			data.set_value(idx[0], "returned", 1)
			resp = Response(response=data.iloc[idx[0]].to_json(), status=200, mimetype="application/json")
		else :
			resp = jsonify({})
		return(resp)
	except Exception as e:
		traceback.print_exc()
		return "Internal Error :: " + str(e), 500

if __name__ == "__main__":
	init()
	app.run(host= '0.0.0.0', port=int(config["port"]), threaded=True)