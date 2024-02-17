# Reference implementation

from dp_realtimedb_interface import Database
CONST_CAR = "c"
CONST_STATION = "s"
CONST_COUCHDB_SERVER_URL = "http://admin:1m2p3k4n@52.9.251.190:5984/"
CONST_DATABASE_NAME = "realtime-test-db"

class DeviceStoreDocument(object):
    """
    DeviceStoreDocument for each device
    This has to be instanciated for each device instance
    """
    def __init__(self, db, device_type, device_id, device_name):
        """
        db: Database instance
        object_type: "c": Car,"s": Stations
        object_id: car_unique_id in case c, station_unique_id in case of s
        """
        self.db = db
        self.device_type = device_type
        self.device_id = device_id
        self.device_name = device_name

    def initialize_doc(self):
        # Note: this is a separate function to reduce crm startup time
        # each object will have key like object_type + object_id
        # this will be unique to the database of given system
        self.device_doc = self.db.get_or_create(self.device_type + str(self.device_id))

        self.set_doc_values(self.device_doc, self.device_type, self.device_id, self.device_name)

    def set_doc_values(self, device_doc, device_type, device_id, 
            device_name = None, fsm_state_id = None, node = None, pack_id = None, wifi_strength = None,
            battery_percentage = None):
        """
        set all keys of doc values and then call db.save to persist
        """
        self.set_key_value(device_doc, "type", device_type)
        self.set_key_value(device_doc, "device_id", device_id)
        self.set_key_value(device_doc, "device_name", device_name)
        self.set_key_value(device_doc, "fsm_state_id", fsm_state_id)
        self.set_key_value(device_doc, "node", node)

        # add other fields based on object_type
        if device_type == CONST_CAR:
            self.set_key_value(device_doc, "pack_id", pack_id)
            self.set_key_value(device_doc, "wifi_strength", wifi_strength)
            self.set_key_value(device_doc, "battery_percentage", battery_percentage)

        self.db.save(device_doc)

    def set_key_value(self, doc, key, value):
        """
        set per key value
        """
        doc[key] = value

    def subscribe_to_doc_long_polling_feed(self, db_instance, _filter=None):
        #################### example to subscribe over long polling ###############################
        # ref: https://stackoverflow.com/questions/7840383/couchdb-python-change-notifications
        print "subscribing to filtered changes over long polling feed"
        since = 0
        while True:
            changes = db_instance.changes(since=since, filter = _filter)
            since = changes["last_seq"]
            for item in changes["results"]:
                try:
                    # print "observed change", item["id"], item
                    doc = db_instance.get(item["id"])
                    
                except Exception as ex:
                    print "Not able to get document by id:", item["id"]
                    continue
                else:
                    print "document changed: ", doc
                    continue

    def subscribe_to_doc_continuous_feed(self, db_instance, _filter=None):
        #################### example to subscribe over continuous feed ##############################
        print "subscribing to filtered changes over continuous feed"
        change_feed = db_instance.changes(feed="continuous",heartbeat="1000",include_docs=True, filter = _filter)

        for item in change_feed:
            doc = item["doc"]
            print "document changed: ", doc

if __name__ == "__main__":
    # testing purpose
    cdb = Database(CONST_COUCHDB_SERVER_URL, CONST_DATABASE_NAME)

    try:
        print "attempting to connect to db"
        cdb.connect()
        print "connection successful"
        dev = DeviceStoreDocument(cdb, "s", 2, "car-k")
        dev.initialize_doc()
        print "item", dev.device_doc, dev.device_doc["device_name"]

        dev.subscribe_to_doc_long_polling_feed(cdb)
        # dev.subscribe_to_doc_continuous_feed(cdb)

    except Exception as ex:
        print "Issues while executing couchdb reference implementation.", ex