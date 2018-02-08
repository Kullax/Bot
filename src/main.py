from __future__ import division
import sys
import requests
import time
import simplejson as json

sys.path.append('../extract')
import customsql


def checkOnline():
    headers = {'Accept' : 'application/json'}
    url = 'https://api.picarto.tv/v1/online?adult=true&gaming=true&categories='
    r_adult = requests.get(url, headers=headers)
    try:
     data = json.loads(r_adult.text)
    except:
     print "no input"
     return
    print "analysing"
    customsql.analysefile(data)
    print "done analysing"

if __name__ == "__main__":
    while True:
        checkOnline()
        time.sleep(30)
