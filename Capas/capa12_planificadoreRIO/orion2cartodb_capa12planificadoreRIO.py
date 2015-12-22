# -*- encoding: utf-8 -*-
import webapp2
import yaml
from paste import httpserver
import logs
import processjson



logs.config_log()

# Load properties
logs.logger.info("Loading properties from deployconfig.yaml")
file = open("deployconfig.yaml")
properties = yaml.load(file)
logs.logger.info("Loaded")

file.close()

def main():
    application = webapp2.WSGIApplication(
        [('.*', processjson.jsonfromCB)],
        debug=True)

    httpserver.serve(application, host=properties["autoregister_host"], port=properties["autoregister_port"])



if __name__ == '__main__':
    main()
