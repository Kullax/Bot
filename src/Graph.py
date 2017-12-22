import matplotlib
matplotlib.use('Agg')

from collections import OrderedDict
from pylab import *
import glob
import simplejson as json
import csv
import time
import os
import copy

# CSV_LOCATION = '/home/kullax/picartobot/Bot/src/follows.csv'
# ACTIVITY_LOCATION = '/var/www/html/dump/stats/activity.png'
# STATS_LOCATION = '/var/www/html/dump/stats/'
# LOG_DIRECTORY = '/home/kullax/picartobot/Bot/src/logs/'
CSV_LOCATION = 'follows.csv'
ACTIVITY_LOCATION = 'C:\\Users\\Martin\\PycharmProjects\\Bot\\src\\stats\\activity.png'
STATS_LOCATION = 'C:\\Users\\Martin\\PycharmProjects\\Bot\\src\\stats\\'
LOG_DIRECTORY = 'logs/'



follows = []
with open(CSV_LOCATION, 'rb') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        follows.append(row[0])
times = {}
os.chdir(LOG_DIRECTORY)

streamer_data = OrderedDict()
streamer_checked = {}

my_cmap = copy.copy(plt.cm.get_cmap('Greens'))
my_cmap.set_bad(alpha=0)


"""
loop after this
"""
def DOIT(start, end):
    for streamer in follows:
        streamer_data[streamer] = []

    files_ = glob.glob("*")

    for file in sorted(files_):
        if float(file) < start or float(file) > end:
            continue
        with open(file, 'rb') as content:
            data = json.load(content)
            for streamer in follows:
                streamer_checked[streamer] = False
            for streamer in data:
                if streamer["name"] in follows:
                    streamer_checked[streamer["name"]] = True
                    streamer_data[streamer["name"]].append(int(streamer["viewers"]))
            for streamer in follows:
                if streamer_checked[streamer] is False:
                    streamer_data[streamer].append(np.ma.masked)
    dictlist = []
    streamers = []
    for key, value in streamer_data.iteritems():
        temp = value
        dictlist.append(temp)
        # if key < 0:
        #     streamer.append(np.ma.masked)
        # else:
        streamers.append(key)

    index = 0
    for streamer in dictlist:
        data = np.array([streamer])
        # data = np.ma.masked_where(data < 0, data)
        # print data
        fig, ax = plt.subplots()
        ax.axis('off')
        ax.imshow(data, cmap=my_cmap, interpolation='none', extent=[0, 100, 0, 1])
        plt.savefig(STATS_LOCATION + streamers[index] + '.png', transparent=True, bbox_inches='tight')
        index+=1
        fig.clf()


    fig, ax = plt.subplots()
    ax.axis('off')
    ax.imshow(array(dictlist), cmap=my_cmap, interpolation='none', extent=[0, 100, 0, len(dictlist)])
    plt.savefig(ACTIVITY_LOCATION, transparent=True, bbox_inches='tight')
    fig.clf()




if __name__ == "__main__":
    import warnings
    warnings.filterwarnings("ignore")

    now = time.time()
    interval = 2 * 24 * 60 * 60
    DOIT(start = now - interval, end = now)
