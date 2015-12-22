import webapp2
import json
import requests
import yaml
from paste import httpserver
import logs

logs.config_log()

# Load properties
logs.logger.info("Loading properties from layerproperties")
file = open("layerproperties.yaml")
layerproperties = yaml.load(file)
logs.logger.info("Loaded")
file.close()


class jsonfromCB(webapp2.RequestHandler):

    def post(self):
        logs.logger.info("Received Json")
        response=json.loads(self.request.body)["contextResponses"]
        #print response
        self.parsejson(response)


    def parsejson(self, response):
        for entity in response:
            attributes = {}
            entity_id = entity["contextElement"]["id"]
            entity_attributes = entity["contextElement"]["attributes"]
            for attribute in entity_attributes:
                if attribute["type"] == "compound":

                    for subattribute in attribute["value"]:
                        attributes["%s_%s" % (attribute["name"],subattribute["name"])]  = subattribute["value"]

                else:
                    attributes[attribute["name"]] = attribute["value"]

            logs.logger.debug("Parsed attributes:[ %s ]" % attributes)
            #print attributes
            self.sendtocartodb(attributes)

    def sendtocartodb(self, attributes):
        column_names=""
        column_values=""
        array_index=1
        logs.logger.info("Preparing data for CartoDB")
        for attribute_name in attributes.keys():

            if array_index == len(attributes.keys()):
                column_names = ("%s"+"%s") % (column_names, attribute_name)
                column_values = ("%s"+"'%s'") % (column_values, attributes[attribute_name])
                #print array_index
            else:
                column_names = ("%s"+"%s, ") % (column_names, attribute_name)
                column_values =  ("%s"+"'%s', ") % (column_values, attributes[attribute_name])
                #print array_index
            array_index += 1

        url = layerproperties["cartodb_url"] % (layerproperties["table_name"],column_names,column_values,layerproperties["cartodb_apikey"])
        logs.logger.debug("Query for CartoDB:[ %s ]" % url)
        #print layerproperties["cartodb_url"]
        logs.logger.info("Send data to CartoDB")
        response = requests.post(url)
        logs.logger.info("Response from CartoDB: [ %s ]" % response)
