from sqlalchemy import Column, Integer, String, ForeignKey, create_engine, DateTime, MetaData, Date, func, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker, backref

engine = create_engine("mysql+mysqldb://root:D120d10k83@localhost/meraki_db", encoding="utf-8", pool_recycle=3600,
                       echo=False)
Session = sessionmaker(bind=engine)
metadata = MetaData()
Base = declarative_base()


class Role(Base):
    __tablename__ = "role"
    roleid = Column(Integer, primary_key=True, autoincrement=True)
    rolename = Column(String(45), nullable=False)
    users = relationship("User", backref=backref('roles', uselist=True))

    # logging.info("Table Role created")
    def __init__(self, rolename):
        self.rolename = rolename


class User(Base):
    __tablename__ = 'user'
    userid = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(45), nullable=False)
    expDate = Column(DateTime)
    firstName = Column(String(45))
    isactive = Column(String(255))
    isnonexpired = Column(String(255))
    isnonlocked = Column(String(255))
    lastName = Column(String(45))
    password = Column(String(45), nullable=False)
    phone = Column(String(45))
    regdate = Column(DateTime)
    username = Column(String(45), nullable=False)
    roleid = Column(Integer, ForeignKey("role.roleid"))

    def __init__(self, userid, email, expDate, firstName, isactive, isnonexpired, isnonlocked, lastName, password,
                 phone, regdate, username, roleid):
        self.userid = userid
        self.email = email
        self.expDate = expDate
        self.firstName = firstName
        self.isactive = isactive
        self.isnonexpired = isnonexpired
        self.isnonlocked = isnonlocked
        self.lastName = lastName
        self.password = password
        self.phone = phone
        self.regdate = regdate
        self.username = username
        self.roleid = roleid
        # logger.info("Table User created")

    authenticated = False

    @property
    def is_active(self):
        """True, as all users are active."""
        return True


    def get_id(self):
        """Return the email address to satisfy Flask-Login's requirements."""
        return self.userid

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False


class Event(Base):
    __tablename__ = 'event'
    event_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255))
    location = Column(String(255))
    date_from = Column(Date())
    date_to = Column(Date())
    routers = relationship('ApMac', backref=backref("events", uselist=True))

    def __init__(self, event_name, location, date_from, date_to):
        self.event_name = event_name
        self.location = location
        self.date_from = date_from
        self.date_to = date_to
        # logger.info("Table Event created")


class Store(Base):
    __tablename__ = 'store'
    store_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255))
    location = Column(String(255))
    routers = relationship("ApMac", backref=backref('stores', uselist=True))

    def __init__(self, name, location):
        self.name = name
        self.location = location


class ApMac(Base):
    __tablename__ = 'router'
    router_id = Column(Integer, primary_key=True, autoincrement=True)
    router_name = Column(String(255))
    apMac = Column(String(255), unique=True, nullable=False)
    apTags = relationship("ApTag", backref=backref("apTag", uselist=True, cascade="save-update"))
    apFloors = relationship("ApFloor",
                            backref=backref("apFloor", uselist=True, cascade="save-update"))
    observations = relationship("Observation",
                                backref=backref("observation", uselist=True))
    event_id = Column(Integer, ForeignKey('event.event_id', ondelete="SET NULL", onupdate="SET NULL"))
    store_id = Column(Integer, ForeignKey('store.store_id', ondelete="SET NULL", onupdate="SET NULL"))

    def __init__(self, apMac, router_name):
        self.apMac = apMac
        self.router_name = router_name
        # logger.info("Table router created")


class ApTag(Base):
    __tablename__ = "apTag"
    id = Column(Integer, primary_key=True, autoincrement=True)
    apTags = Column(String(255), nullable=True)
    router_id = Column(Integer, ForeignKey('router.router_id', ondelete="CASCADE", onupdate="CASCADE"))

    def __init__(self, apTags):
        self.apTags = apTags
        # logger.info("Table apTag created")


class ApFloor(Base):
    __tablename__ = "apFloor"
    id = Column(Integer, primary_key=True, autoincrement=True)
    apFloors = Column(String(255), nullable=True)
    router_id = Column(Integer, ForeignKey('router.router_id', ondelete="CASCADE", onupdate="CASCADE"))

    def __init__(self, apFloors):
        self.apFloors = apFloors
        # logger.info("Table apFloor created")


class Observation(Base):
    __tablename__ = 'observation'
    id = Column(Integer, primary_key=True, autoincrement=True)
    clientMac = Column(String(255))
    ipv4 = Column(String(16), nullable=True)
    ipv6 = Column(String(32), nullable=True)
    ssid = Column(String(255), nullable=True)
    os = Column(String(255))
    manufacturer = Column(String(255))
    rssi = Column(Integer)
    seenEpoch = Column(Integer)
    seenTime = Column(DateTime)
    router_id = Column(Integer, ForeignKey('router.router_id', ondelete="CASCADE", onupdate="CASCADE"))

    # location_id = Column(Integer, ForeignKey("location.id"))
    # location = relationship("location", backref=backref("observations"))

    def __init__(self, clientMac, manufacturer, rssi, seenEpoch, seenTime, ipv4, ipv6, ssid, os):
        self.clientMac = clientMac
        self.manufacturer = manufacturer
        self.rssi = rssi
        self.seenEpoch = seenEpoch
        self.seenTime = seenTime
        self.ipv4 = ipv4
        self.ipv6 = ipv6
        self.ssid = ssid
        self.os = os
        # logger.info("Table observation created")


class BlackBook(Base):
    __tablename__ = "blackBook"
    id = Column(Integer, primary_key=True, autoincrement=True)
    clientMac = Column(String(255), unique=True)
    name = Column(String(255), default=None)

    def __init__(self, clientMac):
        self.clientMac = clientMac
        # loggers.info("Table blackBook created")
    def __repr__(self):
        return "<clientMac= %s>" % (self.clientMac)

def create_trigger(trigger_name):
    tr = """
        CREATE TRIGGER {}
        AFTER INSERT ON meraki_db.blackBook FOR EACH ROW
        BEGIN
          DELETE FROM meraki_db.observation WHERE meraki_db.observation.clientMac = NEW.clientMac
          HAVING count(meraki_db) > 50;
        END ;
        """.format(trigger_name, )
    conn = engine.connect()
    conn.execute(text(tr))





