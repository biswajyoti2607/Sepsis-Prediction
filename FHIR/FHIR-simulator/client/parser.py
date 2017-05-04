# xxunscrambl

"""FHIR parser"""

import datetime
import time
import requests

from fhirclient import client
import fhirclient.models.patient as patient
import fhirclient.models.encounter as encounter
import fhirclient.models.observation as observation
import fhirclient.models.practitioner as practitioner
import json

from unscrambl.core.constants import TimeConstants
from unscrambl.oxygen.composer.base import Operator, WorkStatus, oxygen_operator


class FHIRParser(Operator):

    """Operator that hooks up to FHIR server for fetching data"""

    @oxygen_operator
    def __init__(self, app_id=None, api_base=None,
                 fetch_interval_in_seconds=20, patient_ids=None, codes=None,
                 start_offset_time=None, acceleration_factor=1576800):
        super(FHIRParser, self).__init__()
        self._context = None
        self._fetch_interval_in_seconds = fetch_interval_in_seconds
        self._patient_ids = patient_ids
        self._start_offset_time = start_offset_time
        self._acceleration_factor = acceleration_factor
        self._actual_interval = self._fetch_interval_in_seconds * \
            self._acceleration_factor
        self._date_format = "%Y-%m-%d %H:%M:%S"
		self._url = "http://localhost:5000/subject"

    def prepare(self, context):
        self._context = context

    def fetch_observations(self, pid):
        try:
			resp = requests.get(self._url + "/" + pid)
			if resp.status_code == 200:
				return resp.json()
		except Exception as e:
			print "Error obtaining data :: " + str(e)

    def perform_work(self):
        try:
            out_tuple = self._context.create_outgoing_tuple(0)
            for pid in self._patient_ids:
                out_tuple.patientId = pid
                obs_json = self.fetch_observations(pid)
				if 'inputevents_rate' in obs_json:
					if obs_json['inputevents_itemid'] is not None and obs_json['inputevents_rate'] is not None and obs_json['inputevents_storetime'] is not None:
						out_tuple.code = obs_json['inputevents_itemid']
						out_tuple.effectiveDateTime = obs_json['inputevents_storetime']
						out_tuple.value = float(obs_json['inputevents_rate'])
						out_tuple.ts = time.mktime(
							datetime.datetime.strptime(
								out_tuple.effectiveDateTime[0:19],
								self._date_format).timetuple())
						self._context.emit(0, out_tuple)
        except Exception as e:
            print "error retrieving data: " + str(e)
        return WorkStatus.WAIT, self._fetch_interval_in_seconds * 1000