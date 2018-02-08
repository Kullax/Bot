import models
from sqlalchemy.orm import scoped_session
import time

def analysefile(data):
    Session = scoped_session(models.session_factory)
    db = Session()
    date = str(time.time())
    print "date_ ", date
    tick = models.AddTick(db, date)
    for streamer in data:
        models.AddStreamer(db, streamer)
        models.AddEvent(db, streamer, tick)
    db.commit()
    Session.remove()
