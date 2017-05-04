from fhirclient import client
import fhirclient.models.patient as pat
import fhirclient.models.encounter as enc
import fhirclient.models.observation as obs
import fhirclient.models.practitioner as prac
import requests
import json
import logging
import time
import dateutil.parser
from dateutil.parser import parse
import datetime
import threading
from threading import Timer


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FHIR_Simulator_Client(object):
	def __init__(self, config):

# Specify in config.json		
		self.config = config 

# specify app name and base_URL		
		self.settings = self.config["settings"]
		self.smart = client.FHIRClient(settings=self.settings)

# How long the client would wait before querying again, in seconds
		self.interval = self.config["interval"] 

# ID of patients to retrieve, will retrieve all if not specified
		self.patient_ids = self.config.get("patient_ids", []) 
		self.next_url = self.settings["api_base"] +'/Patient'

# What time in the future/past that streaming starts from		
		self.offset_time = self.config.get("offset_time", None) 

# factor which mulitplied with interval gives the range of dates for which data is retrieved in a given streaming interval  
		self.acceleration_factor = self.config.get("acceleration_factor", 1) 

# codes for which observations should be retrieved
		self.code = self.config.get("code", None)

	def prepare(self):
		self.acc_interval = self.interval * self.acceleration_factor
		if(self.offset_time):
			self.last_fetched_time = parse(self.offset_time) - datetime.timedelta(seconds=self.acc_interval)
		else:
			self.last_fetched_time = datetime.utcnow().replace(tzinfo=pytz.utc) - self.acc_interval

# offset_interval is used so that we don't lose data on the margins.		
		self.offset_interval = self.acc_interval / 10

	def fetch_patient_ids(self):
		if not self.patient_ids:
			while(self.next_url):
				resp = requests.get(self.next_url)
				if resp.status_code == 200:
					json_response = resp.json()
					data = json_response['entry']
					self.patient_ids += list(map(lambda x: x['resource']['id'], data))
					self.next_url = False
					for item in json_response["link"]:
						
						# This achieves pagination
						if item["relation"] == "next":
							self.next_url = item["url"]
							break
				
	def fetch_patient_name(self, pid):
		return(self.smart.human_name(pat.Patient.read(pid,self.smart.server).name[0]))

	def practitioner(self, x):
		return(x.as_json()['participant'][0]['individual']['display'])

   	def fetch_patient_practitioners(self, pid):
   		enc_obj = enc.Encounter.where(struct={'patient':pid}).perform_resources(self.smart.server)
   		return(list(map(self.practitioner, enc_obj)))

   	def fetch_observations(self, pid):
   		obs_obj = obs.Observation.where(struct={'patient':pid}).perform_resources(self.smart.server)
	   	return(list(map(lambda x: x.as_json(), obs_obj)))

	def fetch_data(self):
		self.schedule_next()
		self.fetch_patient_ids()
		data = []
		for pid in self.patient_ids:
			patient_name = self.fetch_patient_name(pid)
			practitioners = self.fetch_patient_practitioners(pid)
			obs_json = self.fetch_observations(pid)
			for obs in obs_json:
	   			if 'valueQuantity' in obs: # Have to make sure to test this with the new data.
	   				data += [(pid, patient_name, obs['effectiveDateTime'], obs['code']['coding'][0]['code'], obs['valueQuantity']['value'], practitioners)]

# Sorting data in ascending order of timestamp	   	
	   	sorted_data = sorted(data, key=lambda tup: tup[2])
	   	start_time = self.last_fetched_time - datetime.timedelta(seconds=(self.offset_interval))
	   	end_time = start_time + datetime.timedelta(seconds=(self.acc_interval + (self.offset_interval)))

# Resetting last fetched time	   	
	   	self.last_fetched_time = end_time

# Filtering data for the time period
	   	filtered_data = [tup for tup in sorted_data if parse(tup[2]) >= start_time and parse(tup[2]) <= end_time]

# Filtering for code	   	
	   	if self.code:
	   		filtered_data = [tup for tup in filtered_data if self.code.get(tup[3], None)]
	   	print(filtered_data)

	def schedule_next(self):
		try:
			t = Timer(self.interval, self.fetch_data)
			t.start()
		except Exception as e:
			logger.error("Error obtaining data :: " + str(e), exc_info=True)


class Utils(object):
	@staticmethod
	def read_json(file_name):
		with open(file_name) as json_data:
			data = json.load(json_data)
			return data

if __name__ == "__main__":
	c = FHIR_Simulator_Client(Utils.read_json("config.json"))
	c.prepare()
	c.fetch_data()