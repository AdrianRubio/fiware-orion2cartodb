# -*- encoding: utf-8 -*-

import webapp2
import json
import requests
import yaml
import logs

logs.config_log()

# Load properties
logs.logger.info("Loading properties from layerproperties")
file = open("layerproperties.yaml")
layerproperties = yaml.load(file)
logs.logger.info("Loaded")
file.close()


class jsonfromCB(webapp2.RequestHandler):

    logs.logger.info("A notification received")

    def post(self):
        response=json.loads(self.request.body)["contextResponses"]
        #print response
        created = self.checkcreatedtable()
        if created:
            self.parsejson(response)
        else:
            #TODO: Hacer la query para crear la tabla
            pass


    def parsejson(self, response):

        for entity in response:
            attributes = {}
            entity_id = entity["contextElement"]["id"]
            entity_attributes = entity["contextElement"]["attributes"]
            for attribute in entity_attributes:
                if attribute["type"] == "compound":

                    for subattribute in attribute["value"]:
                        subattribute["name"]=subattribute["name"].replace("-","_")
                        subattribute["name"]=subattribute["name"].replace(":","_")
                        attributes["%s_%s" % (attribute["name"],subattribute["name"])]  = subattribute["value"]
                else:
                    attributes[attribute["name"]] = attribute["value"]
            #print attributes
            self.sendtocartodb(attributes)


    def checkcreatedtable(self):

        logs.logger.info("Checking if the table exists")
        url = layerproperties["table_checker_url"] % layerproperties["cartodb_apikey"]
        #print url
        response = requests.get(url)
        data=json.loads(response.text)["rows"]
        #print '{cdb_usertables: %s}' % layerproperties["table_name"]
        #TODO: Jose cuando veas esto (que lo verás...) no me mates, mi vida es muy dura y esto no va de otra manera
        exist = False
        for element in data:
            if str(element) == "{u'cdb_usertables': u'%s'}" % layerproperties["table_name"] :
                exist = True
                logs.logger.info("The table [ %s ] exists" % layerproperties["table_name"])
        return exist


    def sendtocartodb(self, attributes):

        logs.logger.info("Sending values to CartoDB")
        column_names=""
        column_values=""
        array_index=1

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
        logs.logger.info(url)
        #print layerproperties["cartodb_url"]
        response = requests.post(url)
        logs.logger.info(response)
