# -*- coding:utf-8 -*-
# use snappy to compress data 
# install snappy in Mac
# $ brew install snappy # snappy library from Google
# $ CPPFLAGS="-I/usr/local/include -L/usr/local/lib" pip install python-snappy

import urllib
import urllib2
import snappy
import json


url = "https://api.growingio.com/custom/${ai}/events"

# http://help.growingio.com 
parameters = [{
    "tm":1480042727121,
    "stm":1480042728943,
    "cs1":"user:526",
    "p":"/v2/projects/yYo1XPl1/charts",
    "s":"bb9aa471-3bc9-455b-b3a1-eeb9e0e9a0e3",
    "u":"7328beea-ee89-43a0-86cb-48879e90a67d",
    "ai":"${ai}",
    "t":"cstm",
    "d":"gta.growingio.com",
    "n": "create_chart",
    "e": {
        "account_id": "${ai}",
        "chart_dimension_count": 12,
        "chart_id": 9999,
        "chart_metric_count": 1,
        "chart_name": "python dim test",
        "chart_type": "line"
    }}]
raw_data = json.dumps(parameters)
compressed_data = snappy.compress(raw_data) # need to compress data !
request = urllib2.Request(url, compressed_data) 
request.add_header('Content-Type', 'text/plain')
request.add_header('charset', 'utf-8')
request.add_header('X-Client-Id', '${client id}')
response = urllib2.urlopen(request)

print response.read()
