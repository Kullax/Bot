from __future__ import division

import os.path
import simplejson as json
import requests
import numpy as np
import csv
import time
import os
import signal

def checkOnline():

    headers = {'Accept' : 'application/json'}
    url = 'https://api.picarto.tv/v1/online?adult=true&gaming=true&categories='
    r_adult = requests.get(url, headers=headers)

    adult_content =  json.loads(r_adult.content)

    with open("/mnt/volume-nyc3-01/logs/" + str(time.time()), 'w') as outfile:
        json.dump(adult_content, outfile)

def DO_IT_UBF():

    try:
        online = checkOnline()
    except:
        online = []

if __name__ == "__main__":

    while True:
        DO_IT_UBF()
        time.sleep(30)

