from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
import os
from sqlalchemy.orm import sessionmaker, scoped_session
import datetime

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
    epoch = Column(DECIMAL(10,2))


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
    commission = Column(Boolean)
    gaming = Column(Boolean)
    multistream = Column(Boolean)
    viewers = Column(Integer)


db = scoped_session(session_factory)
categories = db.query(Category).filter().all()
cats = {}
for category in categories:
    cats[category.category] = category.id
db.remove()


def GetCategories():
    db = scoped_session(session_factory)
    categories = db.query(Event.category).distinct().all()
    for category in categories:
        print category
        cat = Category()
        cat.category = str(category[0])
        db.add(cat)
        db.commit()
    print categories
    db.remove()


def AddTick(db, epoch):
    # date = datetime.datetime.fromtimestamp(epoch).replace(microsecond=0)
    tick = db.query(Tick).filter(Tick.epoch == epoch).first()

    if not tick:
        tick = Tick()
        tick.epoch = epoch
        db.add(tick)
        # Foreign Key needed then adding events - so commit early
        db.commit()
        # Retrieve Key, as it's unknown at this point
        tick = db.query(Tick).filter(Tick.epoch == epoch).first()
    return tick.id


def AddStreamer(db, streamer):
    id = int(streamer["user_id"])
    name = str(streamer["name"])
    streamer = db.query(Streamer).filter(Streamer.id == id).first()

    if streamer:
        if streamer.id == id and streamer.name == name:
            return
    else:
        streamer = Streamer()
    streamer.id = id
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

    (ret, ), = db.query(exists().where(and_(Event.tick == tick, Event.streamer == user_id) ))
    if ret:
        return 0

    event = Event()
    event.tick = tick
    event.streamer = user_id
    event.cat = cats[category]
    event.gaming = gaming
    event.multistream = multistream
    event.adult = adult
    event.viewers = viewers

    db.add(event)
    return 1


# def UpdateCategory(db):
#     categories = db.query(Category).filter().all()
#     cats = {}
#     for category in categories:
#         cats[category.category] = category.id
#     print cats
#
#     added = 0
#     while true:
#         try:
#             added += 1
#             em = db.query(Event).filter().get(added)
#             em.cat = cats[em.category]
#             if (added % 1000) == 0:
#                 print added
#                 db.commit()
#         except:
#             db.commit()

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
        return {}
    streams[first] = abs(first - last).total_seconds()
    # print views
    return streams

