import couchdb
from uuid import uuid4
from singleton import singleton

class Database(object):
    """
        Base class for the persistent pack details to be stored in couchdb.
    """
    __metaclass__ = singleton
    def __init__(self, server_url, db_name):
        self.server_url = server_url
        self.db_name = db_name
        self.server_instance = None
        self.db_instance = None
            
    def connect(self):
        """
        Connect to database based on url and database name present in the instance
        """
        self.server_instance = couchdb.Server(self.server_url)

        try:
            self.db_instance = self.server_instance.create(self.db_name)
        except couchdb.http.PreconditionFailed:
            self.db_instance = self.server_instance[self.db_name]

        # TODO: check if design document present, if not then add one

    def save(self, _doc):
        """
        save the document to couchdb
        _doc: document to persist
        """
        # if id not there then generate uuid and append, this is based on recommendation by couchdb
        if '_id' not in _doc:
            _doc['_id'] = uuid4().hex

        return self.db_instance.save(_doc)

    def get(self, _id):
        """
        get document from couchdb by id
        _id: document id
        """
        return self.db_instance.get(_id)

    def get_all(self):
        """
        get all documents in one go
        can be used during initialization
        """
        pass

    def get_or_create(self, _id):
        """
        return object with the given id if present in database, else create and return
        _id: document id
        """
        _doc = self.db_instance.get(_id)
        if _doc is None:
            _doc = {'_id': _id}
            self.db_instance.save(_doc)
        
        return _doc

    def changes(self, **opts):
        """
        Retrieve a changes feed from the database.
        opts: dictionary of options (ref: http://guide.couchdb.org/draft/notifications.html)
        """
        return self.db_instance.changes(**opts)
