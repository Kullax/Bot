from __future__ import division

import os.path
import simplejson as json
import requests
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import csv
import time
import os
import signal

MAX_WIDTH = 60
MAX_HEIGHT = 50
BORDER_SIZE = 5
font_size = 16
streamer_font_size = 16

screen_width = 1920


font = ImageFont.truetype("Neo Sans.TTF", font_size)
streamer_font = ImageFont.truetype("impact.ttf", streamer_font_size)

text = Image.new('RGBA', (0, 0), (0, 0, 0, 0))
draw = ImageDraw.Draw(text)
text_0 = "I'm all alone"
w_0, _ = draw.textsize(text_0, font)
text_1 = "  Watch this one instead!  "
w_1, _ = draw.textsize(text_1, font)
text_2 = "  Watch these instead!  "
w_2, _ = draw.textsize(text_2, font)

text_size = max(max(w_0,w_1),w_2)

follows = []
filename = 'follows.csv'

def loadFollows():
    global follows
    with open(filename, 'rb') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            follows.append(row[0])

stamp = os.stat(filename).st_mtime

def drawProfile(input=["kullax"]):
    screen = Image.new('RGBA', (screen_width, MAX_HEIGHT + 2 * BORDER_SIZE + font_size), (0, 0, 0, 0))

    width, height = (max( (MAX_WIDTH*len(input) + 2*BORDER_SIZE), text_size), MAX_HEIGHT + 2*BORDER_SIZE + font_size)

    if len(input) == 0:
        screen.save("output.png")
        return
    elif len(input) == 1:
        text = text_1
    else:
        text = text_2



    background_outer = Image.new('RGBA', (width, height), (0, 0, 0, int(255/2) ))
    screen.paste(background_outer, (0,0))
    background_outer = screen
    draw = ImageDraw.Draw(background_outer)


    w,h = draw.textsize(text, font)
    draw.text((int((width-w)/2),0), text, (255,255,255), font)

    background_inner = Image.new('RGBA', (MAX_WIDTH*len(input), MAX_HEIGHT), (0, 0, 0, 255))
    background_outer.paste(background_inner, (BORDER_SIZE, BORDER_SIZE + font_size))

    count = 0
    for streamer in input:
        if os.path.isfile("avatars/" + streamer + ".png"):
            img = Image.open("avatars/" + streamer+".png", 'r')
        elif os.path.isfile("avatars/" + streamer + ".jpg"):
            img = Image.open("avatars/" + streamer+".jpg", 'r')
        else:
            continue
        img_width, img_height = img.size

        ratio = min(( MAX_WIDTH / img_width) , (MAX_HEIGHT / img_height))

        new_width = int(np.ceil(img_width * ratio))
        new_height = int(np.ceil(img_height * ratio))

        img = img.resize((new_width, new_height), Image.ANTIALIAS)
        img_width, img_height = img.size

        bg_width, bg_height = background_outer.size

        offset = (BORDER_SIZE + count * MAX_WIDTH + int((MAX_WIDTH-img_width) / 2), int((bg_height + font_size - img_height) / 2))
        background_outer.paste(img, offset)

        x = offset[0]
        y = img_height
        draw.text((x - 1 , y), streamer[0:6], font=streamer_font, fill="white")
        draw.text((x + 1 , y), streamer[0:6], font=streamer_font, fill="white")
        draw.text((x , y - 1), streamer[0:6], font=streamer_font, fill="white")
        draw.text((x , y + 1), streamer[0:6], font=streamer_font, fill="white")

        draw.text((offset[0] ,img_height), streamer[0:6], (0,0,0), streamer_font)
        count += 1


    background_outer.save("output.png")

def checkOnline():
    global stamp
    if os.stat(filename).st_mtime != stamp:
        print "file changed", stamp, os.stat(filename).st_mtime
        loadFollows()
        stamp = os.stat(filename).st_mtime


    headers = {'Accept' : 'application/json'}
    url = 'https://api.picarto.tv/v1/online?adult=true&gaming=true&categories='
    r_adult = requests.get(url, headers=headers)

    adult_content = json.loads(r_adult.content)


    os.system('cls' if os.name == 'nt' else 'clear')

    online = []
    viewers = 0
    top_stream = 0;
    top_stream_name = "";
    for streamer in adult_content:
        viewer = int(streamer["viewers"])
        viewers += viewer
        if(viewer >= top_stream):
            top_stream = viewer
            top_stream_name = streamer["name"]
        if streamer["name"] in follows:
            print streamer["name"], "is online!"
            online.append(streamer["name"])
    print len(adult_content), viewers
    print top_stream_name, top_stream
    return online

"""
id = 356312
url = "https://api.picarto.tv/v1/channel/name/watsup"
# request =  "https://api.picarto.tv/v1/channel/name/kullax"
# curl = "curl -X GET --header 'Accept: application/json' --header 'Authorization: Bearer " + token + "' '" + request + "'"
headers = {'Authorization' : 'Bearer ' + token,
           'Accept' : 'application/json'}
r = requests.get(url, headers=headers)
print r.content
"""

# url = 'https://api.picarto.tv/v1/webhooks?client_id=' + id + '&client_secret='+secret+'&channel_id='+channel_id
#
# headers = {'Accept': 'application/json',
#            'Authorization': 'Bearer '+persistant
#            }
# r = requests.get(url, headers=headers)
#
# print r.status_code, r.content
#
# url = 'https://api.picarto.tv/v1/webhooks'
# headers = {'Content-Type': 'application/x-www-form-urlencoded',
#            'Accept-Charset': 'text/plain',
#            'Authorization': 'Bearer ' + persistant}
#
# data = {'type' : 'offline',
#         'uri' : 'https://s1.feral.dk/TOKEN'}
#
#
# r = requests.post(url, data=data, headers=headers)
#
# print r.status_code, r.content
#

def DO_IT_UBF():

    try:
        online = checkOnline()
    except:
        online = []

    drawProfile(online)

def Clean(*args):
    print "cleaning"

    background_outer = Image.new('RGBA', (10, 10), (0, 0, 0,0 ))
    background_outer.save("output.png")
    os._exit(0)

if __name__ == "__main__":
    for sig in (signal.SIGABRT, signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, Clean)
    loadFollows()
    while True:
        DO_IT_UBF()
        # most endpoints have 30 second cache.
        time.sleep(30)

