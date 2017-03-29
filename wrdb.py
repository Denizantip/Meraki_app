import database
import datetime
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


class JSON_data(object):
    def __init__(self, obj, session):
        logging.debug('getting data from json')
        self.apTags = obj['apTags']
        self.apMac = obj["apMac"]
        self.apFloors = obj['apFloors']
        self.observations = obj['observations']
        self.session = session

    def write_to_db(self):
        try:
            apMac_table = self.session.query(database.ApMac).filter_by(apMac=self.apMac).one_or_none()
            ###########################################################
            #### Dynamicalyl create database row for router############
            ###########################################################
            # if apMac_table is None:
            #     apMac_table = database.ApMac(self.apMac)
        except Exception:
            logging.error("Database must run")
            apMac_table = None
        if apMac_table:
            logging.info("Table of router exists")
            for apTag in self.apTags:
                instance = database.ApTag(apTag)
                apMac_table.apTags.append(instance)
                self.session.add(instance)
            else:
                logging.info("Adding apTags")
            for apFloor in self.apFloors:
                instance = database.ApFloor(apFloor)
                apMac_table.apFloors.append(instance)
                self.session.add(instance)
            else:
                logging.info("Adding apFloors")
            for observation in self.observations:
                if not self.check_black_list(observation['clientMac']):
                    del observation['location']
                    observation['seenTime'] = datetime.datetime.strptime(observation["seenTime"], "%Y-%m-%dT%H:%M:%SZ")
                    instance = database.Observation(**observation)
                    apMac_table.observations.append(instance)
                    self.session.add(instance)
            else:
                logging.info("add observations")
        else:
            logging.info("router table with getted mac not exists")
        self.session.commit()

    def check_black_list(self, client_mac):
        bl = (i.clientMac for i in self.session.query(database.BlackBook).all())
        if client_mac in bl:
            logging.info("Client from bl was detected")
            return True
        else:
            return False



def test_class():
    assert JSON_data({
        "observations": [{
            "ipv6": None,
            "ipv4": None,
            "ssid": None,
            "location": {
                "unc": 12.949704944981216,
                "y": [],
                "lng": 30.478811086822134,
                "x": [],
                "lat": 50.37944278510648

            },
            "seenTime": "2017-03-16T13:52:00Z",
            "rssi": 26,
            "os": None,
            "manufacturer": "Intel",
            "clientMac": "78:0c:b8:a2:c7:81",
            "seenEpoch": 1489672320

        },
            {
                "ipv6": None,
                "ipv4": None,
                "ssid": None,
                "location": {
                    "unc": 7.994796543091113,
                    "y": [],
                    "lng": 30.47902674886737,
                    "x": [],
                    "lat": 50.37946338081357},
                "seenTime": "2017-03-16T13:51:57Z",
                "rssi": 33,
                "os": "Mac OS X",
                "manufacturer": "Apple",
                "clientMac": "78:31:c1:ba:24:46",
                "seenEpoch": 1489672317

            },
            {
                "ipv6": None,
                "ipv4": None,
                "ssid": None,
                "location": {
                    "unc": 20.152192058468202,
                    "y": [],
                    "lng": 30.479129714927865,
                    "x": [],
                    "lat": 50.379455777035865
                },
                "seenTime": "2017-03-16T13:51:57Z",
                "rssi": 18,
                "os": "Windows",
                "manufacturer": "Intel",
                "clientMac": "00:22:fa:ad:c1:1c",
                "seenEpoch": 1489672317

            },
            {
                "ipv6": None,
                "ipv4": None,
                "ssid": None,
                "location": {
                    "unc": 14.244675417030098,
                    "y": [],
                    "lng": 30.47885113826794,
                    "x": [],
                    "lat": 50.379582314684995
                },
                "seenTime": "2017-03-16T13:52:05Z",
                "rssi": 29,
                "os": None,
                "manufacturer": "Shanghai Huaqin Telecom...",
                "clientMac": "90:21:81:da:ed:12",
                "seenEpoch": 1489672325
            },
            {
                "ipv6": None,
                "ipv4": None,
                "ssid": None,
                "location": {
                    "unc": 37.872191057754456,
                    "y": [],
                    "lng": 30.478976363468973,
                    "x": [],
                    "lat": 50.379512339465414

                },
                "seenTime": "2017-03-16T13:52:00Z",
                "rssi": 19,
                "os": None,
                "manufacturer": "Lenovo (Beijing)",
                "clientMac": "a0:32:99:56:7a:a8",
                "seenEpoch": 1489672320

            },
            {
                "ipv6": None,
                "ipv4": None,
                "ssid": None,
                "location": {
                    "unc": 33.52264639140593,
                    "y": [],
                    "lng": 30.478996257425024,
                    "x": [],
                    "lat": 50.37954085597527},
                "seenTime": "2017-03-16T13:52:06Z",
                "rssi": 19, "os": None, "manufacturer": "Sony Mobile...", "clientMac": "44:74:6c:af:89:a6",
                "seenEpoch": 1489672326}, {"ipv6": None, "ipv4": "/192.168.129.31", "ssid": "Presentation",
                                           "location": {"unc": 2.3013535751319965, "y": [], "lng": 30.479023829100072,
                                                        "x": [], "lat": 50.37952456901708},
                                           "seenTime": "2017-03-16T13:52:04Z", "rssi": 52, "os": "Mac OS X",
                                           "manufacturer": "Apple", "clientMac": "5c:f9:38:a6:92:5c",
                                           "seenEpoch": 1489672324}, {"ipv6": None, "ipv4": None, "ssid": None,
                                                                      "location": {"unc": 16.18135812700672, "y": [],
                                                                                   "lng": 30.47870972226798, "x": [],
                                                                                   "lat": 50.379559493359444},
                                                                      "seenTime": "2017-03-16T13:52:00Z", "rssi": 22,
                                                                      "os": None,
                                                                      "manufacturer": "Shenzhen Xin KingBrand...",
                                                                      "clientMac": "28:fc:f6:04:03:25",
                                                                      "seenEpoch": 1489672320},
            {"ipv6": None, "ipv4": None, "ssid": None,
             "location": {"unc": 4.405474095840357, "y": [], "lng": 30.478972593873436, "x": [],
                          "lat": 50.37950511623386}, "seenTime": "2017-03-16T13:51:59Z", "rssi": 32, "os": "Android",
             "manufacturer": "Sony Mobile...", "clientMac": "40:40:a7:32:f8:66", "seenEpoch": 1489672319},
            {"ipv6": None, "ipv4": None, "ssid": None,
             "location": {"unc": 9.284169514699853, "y": [], "lng": 30.47903686376003, "x": [],
                          "lat": 50.379473109389956}, "seenTime": "2017-03-16T13:51:57Z", "rssi": 26, "os": "Mac OS X",
             "manufacturer": "Apple", "clientMac": "a0:99:9b:06:84:43", "seenEpoch": 1489672317},
            {"ipv6": None, "ipv4": None, "ssid": None,
             "location": {"unc": 37.30749439490675, "y": [], "lng": 30.478977405946353, "x": [],
                          "lat": 50.3795127134878}, "seenTime": "2017-03-16T13:52:04Z", "rssi": 19, "os": "iOS",
             "manufacturer": "Apple", "clientMac": "88:15:44:2c:7b:30", "seenEpoch": 1489672324}],
        "apMac": "AA:AA:AA:AA:AA:AA",
        "apTags": ["234234234", "sdfghskdjhgksjhdhg"],
        "apFloors": ["1st-Floor", "2nd-Floor", "3rd_floor"]

    }).check_black_list("d0:e1:40:8c:68:46") == False
