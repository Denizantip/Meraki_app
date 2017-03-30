import datetime
import time

import database

session = database.Session()
engine = database.engine
database.Base.metadata.create_all(engine)

def write_routers_to_db():
    tr = """INSERT INTO meraki_db.role (rolename) VALUES ('admin');
            INSERT INTO meraki_db.role (rolename) VALUES ('user');"""
    engine.connect().execute(tr)
    with open("apMac.txt", "r") as f:
        e = database.Event("test", "test", datetime.datetime.now(), datetime.datetime.now())
        for apMac in f.readlines():
            s = database.ApMac(apMac.strip(), "RouterName")
            e.routers.append(s)
            session.add(e)
        session.commit()


def db(obj):
    apMac_row = obj.pop('apMac')
    apMac_table = session.query(database.apMac).filter_by(apMac=apMac_row).one_or_none()

    def add_session(*args, **kwargs):
        database_table_method = getattr(database, class_name)
        o = database_table_method(*args, **kwargs)
        getattr(apMac_table, class_name).append(o)
        session.add(o)

    if apMac_table:
        for class_name, class_value in obj.items():
            if isinstance(class_value, list) and class_name in dir(database):
                for i in class_value:
                    if isinstance(i, (str, int, float)):
                        try:
                            print(class_name)
                            q = getattr(apMac_table, class_name)
                            if i not in (getattr(row, class_name) for row in q):
                                add_session(i)
                        except Exception:
                            add_session(i)

                    elif isinstance(i, dict):
                        if not check_black_list(i['clientMac']):
                            del i["location"]
                            i['seenTime'] = datetime.datetime.strptime(i["seenTime"], "%Y-%m-%dT%H:%M:%SZ")
                            i['seenEpoch'] = (i['seenTime'] - datetime.datetime.strptime(time.ctime(i['seenEpoch']),
                                                                                        "%a %b %d %H:%M:%S %Y")).seconds//3600

                            print(i['seenEpoch'])

                            add_session(**i)
            session.commit()
    else:
        pass


def check_black_list(str):
    bl = (i.clientMac for i in session.query(database.BlackBook).all())
    if str in bl:
        session.query(database.observations).filter_by(clientMac=str).delete()
        return True
    else:
        return False


write_routers_to_db()
