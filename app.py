#!/usr/bin/env python

import urllib
import json
import os
import re

from flask import Flask
from flask import request
from flask import make_response

# Flask app should start in global layout
app = Flask(__name__)


@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    print("Request:")
    print(json.dumps(req, indent=4))

    res = processRequest(req)

    res = json.dumps(res, indent=4)
    # print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r


def processRequest(req):
    if req.get("result").get("action") != "yahooWeatherForecast":
        return {}
    city_names=processlocation(req)
    sector_names=processSector(req)
    property_type=processPropertyType(req)
    minimum_value=processMinimum(req)
    maximum_value=processMaximum(req)
    latest=processLatestProperties(req)
    if minimum_value > maximum_value:
        minimum_value,maximum_value=maximum_value,minimum_value
    else:
        minimum_value,maximum_value=minimum_value,maximum_value    
    baseurl = "https://fazendanatureza.com/bot/botarz.php?city_name="+city_names+"&sector_name="+sector_names+"&minPrice="+minimum_value+"&maxPrice="+maximum_value+"&type="+property_type+"&LatestProperties="+ latest
    result = urllib.urlopen(baseurl).read()
    data = json.loads(result)
    res = makeWebhookResult(data)
    return res

def processlocation(req):
    result = req.get("result")
    parameters = result.get("parameters")
    city = parameters.get("city")
    return city

def processSector(req):
    result = req.get("result")
    parameters = result.get("parameters")
    sector = parameters.get("Location")
    return sector

def processMinimum(req):
    result = req.get("result")
    parameters = result.get("parameters")
    minimum = parameters.get("number")
    return minimum

def processMaximum(req):
    result = req.get("result")
    parameters = result.get("parameters")
    maximum = parameters.get("number1")
    return maximum


def processPropertyType(req):
    result = req.get("result")
    parameters = result.get("parameters")
    propertyType = parameters.get("PropertyType")
    return propertyType

def processLatestProperties(req):
    result = req.get("result")
    parameters = result.get("parameters")
    latest = parameters.get("LatestProperties")
    return latest

def makeWebhookResult(data):
    i=0
    length=len(data)
    row_id=['test','test1','test2']
    row_title=['test','test1','test2']
    row_location=['test','test1','test2']
    row_price=['test','test1','test2']
    while (i <length):
        row_id[i]=data[i]['p_id']
        row_title[i]=data[i]['title']
        row_location[i]=data[i]['address']
        row_price[i]=data[i]['address']
        i+=1
    
    # print(json.dumps(item, indent=4))
    speech = "This is the response from server."+ row_title[0] 
    print("Response:")
    print(speech)
    if "unable" in row_title[0]:
        message={
         "text":row_title[0]
    }
    else:
        message= {
         "attachment": {
           "type": "template",
             "payload": {
               "template_type": "generic",
               "elements": [{
               "title": row_title[0],
               "subtitle": row_location[0],
               "item_url": "http://www.aarz.pk/property-detail?id="+row_id[0],               
               "image_url": "http://www.aarz.pk/assets/images/properties/"+row_id[0]+"/"+row_id[0]+".actual.1.jpg" ,
                "buttons": [{
                "type": "web_url",
                "url": "www.aarz.pk",
                "title": "Open Web URL"
            }, 
                   ],
          }, 
                   {
                "title": row_title[1],
                "subtitle": row_location[1],
                "item_url":  "http://www.aarz.pk/property-detail?id="+row_id[1],               
                "image_url": "http://www.aarz.pk/assets/images/properties/"+row_id[1]+"/"+row_id[1]+".actual.1.jpg",
                "buttons": [{
                "type": "web_url",
                "url": "www.aarz.pk",
                "title": "Open Web URL"
            },
                   ]
          }]
        }
      }
    }

    return {
        "speech": speech,
        "displayText": speech,
        "data": {"facebook": message},
        # "contextOut": [],
        #"source": "apiai-weather-webhook-sample"
    }


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print "Starting app on port %d" % port

    app.run(debug=False, port=port, host='0.0.0.0')
