# xxunscrambl

"""FHIR parser"""

import datetime
import time
import operator#srujana
from datetime import timedelta#srujana

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
        self._fhir_settings = {'app_id': app_id, 'api_base': api_base}
        self._smart = None 
        self._fetch_interval_in_seconds = fetch_interval_in_seconds
        self._patient_ids = patient_ids
        self._codes = codes
        self._next_url = api_base + '/Patient'
        self._start_offset_time = start_offset_time
		#Srujana starts
		if self._start_offset_time==None:
			self._start_offset_time=datetime.datetime(2008,01,01,00,00,00)
		#srujana ends
        self._acceleration_factor = acceleration_factor
        self._actual_interval = self._fetch_interval_in_seconds * \
            self._acceleration_factor
        self._date_format = "%Y-%m-%dT%H:%M:%S"

    def prepare(self, context):
        self._context = context
        self._smart = client.FHIRClient(self._fhir_settings)

    def fetch_patient_name(self, pid):
        return(self._smart.human_name(patient.Patient.read(pid,self._smart.server).name[0]))

    def practitioner(self, x):
        return(x.as_json()['participant'][0]['individual']['display'])

    def fetch_patient_practitioners(self, pid):
        enc_obj = encounter.Encounter.where(struct={'patient':pid}).perform_resources(self._smart.server)
        return(list(map(self.practitioner, enc_obj)))

#    def fetch_observations(self, pid): srujana
	def fetch_observations(self, pid):
		obs_list=list()
        obs_obj = observation.Observation.where(struct={'patient':pid}).perform_resources(self._smart.server)
		#srujana starts
		starttime=self._start_offset_time
		endtime = starttime + timedelta(seconds=self._actual_interval)
		for o in obs_obj:
			curr_obs=o.as_json()
			curr_obstime=curr_obs['effectiveDateTime']
			if curr_obstime > starttime and curr_obstime<endtime:
				obs_list.append(curr_obs)
        #return(list(map(lambda x: x.as_json(), obs_obj)))	
		obs_list=sorted(obs_list, key=lambda o:o['effectiveDateTime']) #sort observation in ascending order based on onbservation time
		return obs_list
		#srujana ends

    def perform_work(self):
        try:
            out_tuple = self._context.create_outgoing_tuple(0)
            for pid in self._patient_ids:
                out_tuple.patientId = pid
                out_tuple.patientName = self.fetch_patient_name(pid)
                out_tuple.practitioners = list(set(self.fetch_patient_practitioners(pid)))
                obs_json = self.fetch_observations(pid)
                for obs in obs_json:
                    if 'valueQuantity' in obs:
                        out_tuple.code = obs['code']['coding'][0]['code']
                        out_tuple.effectiveDateTime = obs['effectiveDateTime']
                        out_tuple.value = float(obs['valueQuantity']['value'])
                        out_tuple.ts = time.mktime(
                            datetime.datetime.strptime(
                                out_tuple.effectiveDateTime[0:19],
                                self._date_format).timetuple())
                        self._context.emit(0, out_tuple)
        except Exception as e:
            print "error retrieving data: " + str(e)
        return WorkStatus.WAIT, self._fetch_interval_in_seconds * 1000
