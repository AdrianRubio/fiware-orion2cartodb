import json
import time
import requests
import yaml
import logs
import time
from geopy.distance import great_circle


logs.config_log()


def checkbuoyinside(buoyfixlocation, buoyreallocation, buoyfixradius):
	
    logs.logger.info("Calculating the difference between the real position and ideal position")
    distance=great_circle(buoyfixlocation, buoyreallocation).meters
    #print distance
    #print buoyfixradius
    
    if float(buoyfixradius) >= float(distance):
	logs.logger.info("The buoy is within the edge")
        return True
    else:
	logs.logger.info("The buoy is outside the edge")
        return False


def sendalarmtoCB(buoy, positionAlarm):

    url = "http://int.dca.tid.es/NGSI10/updateContext"
	
    headers = {
        'accept': "application/json",
        'fiware-service': "tecnoport",
        'content-type': "application/json",
        'cache-control': "no-cache",
        'postman-token': "d260d0d2-601c-2d7b-474b-30bdb2d39612"
    }

    payload={
        "contextElements": [
            {
                "type": "buoy",
                "isPattern": "false",
                "id": buoy,
                "attributes": [
                {
                "name": "positionAlarm",
                "type": "boolean",
                "value": positionAlarm
              }
                ]
            }
        ],
        "updateAction": "APPEND"
    }

    response = requests.request("POST", url, data=json.dumps(payload), headers=headers)
    #print response.text


def retrievebuoys():

    logs.logger.info("Retriving bouys ...")

    url = "http://int.dca.tid.es/NGSI10/queryContext"

    headers = {
    'accept': "application/json",
    'fiware-service': "tecnoport",
    'content-type': "application/json"
    }

    payload={

    "entities": [
        {
          "type": "buoy",
          "isPattern": "true",
          "id": ".*"
        } ]
    }

    response = requests.request("POST", url, data=json.dumps(payload), headers=headers)
    #print response.text
    response=json.loads(response.text)["contextResponses"]
    for buoy in response:
        for attribute in buoy['contextElement']["attributes"]:
            if attribute["name"] == "position":
                buoyfixlocation=attribute["value"]
            if attribute["name"] == "GPSposition":
                    buoyreallocation=attribute["value"]
            if attribute["name"] == "alarmRadius":
                    buoyfixradius=attribute["value"]
            if attribute["name"] == "positionAlarm":
                    positionAlarm=attribute["value"]

        inside = checkbuoyinside(buoyfixlocation, buoyreallocation, buoyfixradius)

        if inside == True and (int(positionAlarm) == 1 or positionAlarm == None):
            	logs.logger.info("Desactivating the alarm for the buoy [ %s ]" % (buoy['contextElement']["id"]))  
		sendalarmtoCB(buoy['contextElement']["id"], "0" )

        if inside == False and (int(positionAlarm) == 0 or positionAlarm == None):
	        logs.logger.info("Activating the alarm for the buoy [ %s ]" % (buoy['contextElement']["id"]))
                sendalarmtoCB(buoy['contextElement']["id"], "1" )


while True:
    retrievebuoys()
    time.sleep(3600)

