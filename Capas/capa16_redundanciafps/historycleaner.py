import urllib2
import json
import time
import yaml


file = open("historycleaner.yaml")
param = yaml.load(file)

tablename= str(param["tablename"])
columname= str(param["columname"])
daystosave= int(param["daystosave"])
cartodbapikey= str(param["cartodbapikey"])

#Configuration parameters

Non_encode_symbols = "&:/=(),'?!."

datetodelatefrom=str(time.gmtime()[0])+"-"+str(time.gmtime()[1])+"-"+str(time.gmtime()[2]-daystosave)
#url="https://iotsupport.cartodb.com/api/v2/sql?q=DELETE FROM testhistoric WHERE timeinstant ~ '"+datetodelate+".*'&api_key=6e87270accdefa4e1126d00cbbd6caa4132c3619"

url="https://iotsupport.cartodb.com/api/v2/sql?q=DELETE FROM "+tablename +" WHERE "+ columname +" < '"+datetodelatefrom+"'&api_key="+cartodbapikey
print(url)


#Send request to cartodb
url= urllib2.quote(url,Non_encode_symbols)
f = urllib2.urlopen(url)

#Print answer from cartodb
response=f.read()
resp=json.dumps(response)

timenow=time.time()

print (timenow)

print(resp)











