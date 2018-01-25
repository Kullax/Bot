import simplejson as json
import io
import models
from sqlalchemy.orm import scoped_session

def analysefile(input):
    Session = scoped_session(models.session_factory)
    db = Session()
    date = float(input.split("/")[-1])
    print "date_ ", date,
    tick = models.AddTick(db, date)
    with io.open(input, "r", encoding="utf-8") as content:
        data = json.load(content)
        for streamer in data:
            db.flush()
            models.AddStreamer(db, streamer)
            models.AddEvent(db, streamer, tick)
        db.commit()
    Session.remove()
