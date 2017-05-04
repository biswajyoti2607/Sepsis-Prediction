import datetime
import json
import logging
import requests
import sched
import time
import traceback

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FHIR_Simulator_Client(object):
	def __init__(self, config):
		self.config = config
		self.latest_data = None
		self.URLs = []
		self.shouldStop = False
		self.scheduler = None
		
	def prepare(self):
		self.URLs.append(self.config["Base_URI"] + "/" + self.config["resource"]["patient"])
		self.timer_delay = self.config["interval"]
		
	def stop():
		self.shouldStop = True
	
	def fetch_data(self, id):
		if self.shouldStop == True:
			self.timer.cancel()
			return
		
		for url in self.URLs:
			try:
				resp = requests.get(url + "/" + id)
				if resp.status_code == 200:
					out_tuple = {}
					out_tuple["patientId"] = id
					obs_json = resp.json()
					#for obs in obs_json:
					if 'inputevents_rate' in obs_json:
						if obs_json['inputevents_itemid'] is not None and obs_json['inputevents_rate'] is not None and obs_json['inputevents_storetime'] is not None:
							out_tuple["code"] = obs_json['inputevents_itemid']
							out_tuple["value"] = float(obs_json['inputevents_rate'])
							out_tuple["effectiveDateTime"] = obs_json['inputevents_storetime']
							out_tuple["ts"] = time.mktime(
								datetime.datetime.strptime(
									out_tuple["effectiveDateTime"][0:19],
									"%Y-%m-%d %H:%M:%S").timetuple())
						print out_tuple
			except Exception as e:
				logger.error("Error obtaining data :: " + str(e), exc_info=True)
		if self.scheduler is None:
			self.scheduler = sched.scheduler(time.time, time.sleep)
			self.scheduler.enter(self.timer_delay, 1, self.fetch_data, (id, ))
			self.scheduler.run()
		else:
			self.scheduler.enter(self.timer_delay, 1, self.fetch_data, (id, ))
		
class Utils(object):
	@staticmethod
	def read_json(file_name):
		with open(file_name) as json_data:
			data = json.load(json_data)
			return data

if __name__ == "__main__":
	c = FHIR_Simulator_Client(Utils.read_json("config.json"))
	c.prepare()
	c.fetch_data("55973")