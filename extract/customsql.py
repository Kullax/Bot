import shutil
import glob
import simplejson as json
from multiprocessing import Pool
import numpy as np
import io
from sklearn.model_selection import KFold
import time, datetime
import models
from sqlalchemy.orm import scoped_session


def analysefiles(input):
    Session = scoped_session(models.session_factory)
    db = Session()
    print "made connection"
    for f in input:
        print f
        date = float(f.split("/")[-1])
        tick = models.AddTick(db, date)
        with io.open(f, "r", encoding="utf-8") as content:
            data = json.load(content)
            for streamer in data:
                models.AddStreamer(db, streamer)
                models.AddEvent(db, streamer, tick)
        db.commit()
        print "committing"
#        shutil.move(f, "C:/Users/Martin/Desktop/loggedcopy/" + str(date))
    Session.remove()


def analyse():
    processors = 6
    kf = KFold(n_splits=processors)

    files_ = np.array(sorted(glob.glob("C:/Users/Martin/Desktop/logcopy2/*")))
    kf.get_n_splits(files_)

    d = []
    for train_index, test_index in kf.split(files_):
        d.append(files_[test_index])

    pool = Pool(processes=processors)
    #

    print "Starting Analysis", time.time()
    results = pool.map(analysefiles, d)


if __name__ == '__main__':
    Session = scoped_session(models.session_factory)
    db = Session()
    streams = models.FindAllFromStreamer(db, "Watsup", delay=30)
    if streams == 0:
        print "no result"
        import sys
        sys.exit()
    s = []
    for stream in sorted(streams):
        if stream.date() > datetime.date(2017, 1, 1):
            print stream, "lasted", str(datetime.timedelta(seconds=streams[stream]))
            s.append(streams[stream])
    print len(s), str(datetime.timedelta(seconds=np.average(np.array(s)))).split(".")[0]

