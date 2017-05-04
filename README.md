# Sepsis Prediction

This is the code repository for Sepsis Prediction Project in CS6440 (Gatech). This project enables ICUs to pull patient data from FHIR enabled EHR servers and present the risk of the occurrence of sepsis.

The objectives of this project are
- to develop a FHIR connector that can be deployed on an Unscrambl platform
- to develop a prediction model and deploy the model on the Unscrambl platform
- to develop a visualization which can pull the prediction from Unscrambl platform and present it in a web application

What is FHIR? [Have a look!](https://www.hl7.org/fhir/overview.html)
What is Unscrambl? [Have a look!](http://unscrambl.com/)

### FHIR Connector
FHIR\FHIR-client contains a python client to connect to the FHIR server and pull data
```sh
$ python streaming_client.py
```

FHIR\FHIR-simulator contains a python server which simulates the FHIR server using sample CSV patient data files and a python client to connect to the same
```sh
$ python simulator.py
```
```sh
$ python client.py
```
**Note:** The data files are not included in the repository. Please copy the data files into server\Data folder.

### ML Models (generated offline)
'offline-data-experiments' folder contains the IPython notebooks used to run the various machine learning and feature engineering experiments. Please look into the individual files for their specific purpose.
**Note:** The data files are not included in the repository. Please copy the data files into offline-data-experiments\m100s2 folder.

### Unscrambl platform code
 - Unscrambl\FHIR-Client\real contains the code to connect Unscrambl to a FHIR server
 - Unscrambl\FHIR-Client\simulation contains the code to connect Unscrambl to the FHIR simulator
 - Unscrambl\Scoring\all-features contains the model and scoring function to generate the risk score on Unscrambl using all possible features.
 - Unscrambl\Scoring\4-features contains the model and scoring function to generate the risk score on Unscrambl using 4 features present on Tech-on-FHIR server.

### Visualization Example
vis\static contains the ICU Chart Visualization API (api.js) and an example of an ICU having 4 beds and pulling static data from CSV files (anonymized).

vis\simulation contains the ICU Chart Visualization API (api.js) and an example client of an ICU having 4 beds and pulling data from a server emulating Unscrambl platform (present in the server folder). To run the server -
```sh
$ python simulator.py
```

### Visualization API
This API is based on d3.js and visualizes one ICU chart. The API can be initialized with the following -
 - datum
 - width
 - height
 - border
 - title
 - xTitle
 - yTitle
 - yDomain
 - debug
 - halt


### List of Python Dependencies
fhirclient, requests, json, logging, time, dateutil, datetime, threading, sched, traceback, unscrambl, sklearn, numpy, pandas, matplotlib, pickle

