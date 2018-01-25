from __future__ import division
import sys
import simplejson as json
import requests
import time

sys.path.append('../extract')
import customsql

def checkOnline():

    headers = {'Accept' : 'application/json'}
    url = 'https://api.picarto.tv/v1/online?adult=true&gaming=true&categories='
    r_adult = requests.get(url, headers=headers)

    adult_content =  json.loads(r_adult.content)

    file = "/mnt/volume-nyc3-01/logs/" + str(time.time())
    with open(file, 'w') as outfile:
        json.dump(adult_content, outfile)
    print "analysing"
    customsql.analysefile(file)
    print "done analysing"

def DO_IT_UBF():

    try:
        online = checkOnline()
    except:
        online = []

if __name__ == "__main__":
    while True:
        DO_IT_UBF()
        time.sleep(30)

