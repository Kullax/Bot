from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
import os
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import exists

basedir = os.path.abspath(os.path.dirname(__file__))

mysqlstr = 'mysql+pymysql://root:Maggie4Now#@localhost/picarto?charset=utf8'

engine = create_engine(mysqlstr, echo=False)

Base = declarative_base()

session_factory = sessionmaker(bind=engine)


class Streamer(Base):
    __tablename__ = "streamers"
    id = Column(Integer, primary_key=True)
    name = Column(String(30))


class Tick(Base):
    __tablename__ = "ticks"
    id = Column(Integer, primary_key=True)
    epoch = Column(DECIMAL(12,2))


class Category(Base):
    __tablename__ = "category"
    id = Column(Integer, primary_key=True)
    category = Column(String(20))


class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True)
    tick = Column(Integer, ForeignKey(Tick.id))
    streamer = Column(Integer, ForeignKey(Streamer.id))
    category = Column(Integer, ForeignKey(Category.id))
    adult = Column(Boolean)
    commissions = Column(Boolean)
    gaming = Column(Boolean)
    multistream = Column(Boolean)
    viewers = Column(Integer)

def AddTick(db, epoch):
    tick = Tick()
    tick.epoch = float(epoch)
    db.add(tick)
    # Foreign Key needed then adding events - so commit early
    db.commit()
    print "committed tick"
    # Retrieve Key, as it's unknown at this point
    tick = db.query(Tick).filter(Tick.epoch == epoch).first()
    return tick.id


def AddStreamer(db, streamer):
    _id = int(streamer["user_id"])
    name = str(streamer["name"])

    (ret,), = db.query(exists().where(Streamer.id == _id))
    if ret:
        return

    streamer = Streamer()
    streamer.id = _id
    streamer.name = name
    db.add(streamer)
    # Foreign Key needed then adding events - so commit early
    db.commit()
    return


def AddEvent(db, streamer, tick):
    user_id = int(streamer["user_id"])
    category = streamer["category"]
    gaming = bool(streamer["gaming"])
    multistream = bool(streamer["multistream"])
    adult = bool(streamer["adult"])
    viewers = int(streamer["viewers"])
    commissions = bool(streamer["commissions"])

    (ret, ), = db.query(exists().where(and_(Event.tick == tick, Event.streamer == user_id) ))
    if ret:
        return

    event = Event()
    event.tick = tick
    event.streamer = user_id

    cat = db.query(Category).filter(Category.category == category).first()
    if cat:
        event.category = cat.id
    else:
        newCat = Category()
        newCat.category = category
        db.add(newCat)
        db.commit()
        event.category = db.query(Category).filter(Category.category == category).first().id

    event.gaming = gaming
    event.multistream = multistream
    event.adult = adult
    event.viewers = viewers
    event.commissions = commissions

    db.add(event)
    db.commit()
    return 1

def FindAllFromStreamer(db, name, delay=5):
    everything = db.query(Event.id, Streamer.name, Tick.epoch, Event.viewers).\
        join(Streamer, Streamer.id == Event.streamer).\
        join(Tick, Tick.id == Event.tick).\
        filter(Streamer.name == name).\
        order_by(Tick.epoch)\
        .all() #, Event.multistream == 1).\
    # print len(everything)
    streams = {}
    last = None
    first = None
    views = 0
    for id, name, tick, viewers in everything:
        if viewers > views:
            views = viewers
        if first == None:
            first = tick
            last = tick
        if (tick - last).total_seconds() > 60*delay:
            streams[first] = abs(first - last).total_seconds()
            first = tick
        last = tick
    if first == None or last == None:
        return 0
    streams[first] = abs(first - last).total_seconds()
    return streams

