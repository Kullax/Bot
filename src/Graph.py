from collections import OrderedDict
from pylab import *
import glob
import simplejson as json
import csv
import time
import os
import copy
matplotlib.style.use("ggplot")

follows = []
with open('follows.csv', 'rb') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        follows.append(row[0])
times = {}
os.chdir("logs/")
old_files = []

streamer_data = OrderedDict()
streamer_checked = {}

my_cmap = copy.copy(plt.cm.get_cmap('Greens'))
my_cmap.set_bad(alpha=0)

"""
loop after this
"""
def DOIT():
    for streamer in follows:
        streamer_data[streamer] = []

    files = glob.glob("*")
    for file in files:
        if file in old_files:
            continue
        with open(file, 'rb') as content:
            data = json.load(content)
        times[float(file)] = data
        old_files.append(file)

    for time in sorted(times.items(), key=lambda x: x[0]):
        for streamer in follows:
            streamer_checked[streamer] = False
        for streamer in times[time[0]]:
            if streamer["name"] in follows:
                streamer_checked[streamer["name"]] = True
                streamer_data[streamer["name"]].append(int(streamer["viewers"]))
        for streamer in follows:
            if streamer_checked[streamer] is False:
                streamer_data[streamer].append(np.nan)

    dictlist = []
    streamers = []
    for key, value in streamer_data.iteritems():
        temp = value
        dictlist.append(temp)
        streamers.append(key)
    length = len(dictlist[0])
    fig, ax = plt.subplots(80, len(dictlist))

    ax.axis('off')
    ax.imshow(array(dictlist), cmap=my_cmap, interpolation='none', extent=[length-80, length, 0, len(dictlist)])
    plt.savefig('../activity.png', transparent=True)

if __name__ == "__main__":
    while True:
        DOIT()
        time.sleep(30)
