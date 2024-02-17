from config_db import Database
from dosepack.web_command_handler.web_command_handler import WebCommandHandler
import json

COUCHDB_SERVER = "http://54.67.35.135:5984/"
CONFIG_DATABASE = "config_db"


class App(WebCommandHandler):
    def __init__(self, listening_ip, listening_port):
        super(App, self).__init__(listening_ip, listening_port, 'config_manager.html')
        self.database = Database(COUCHDB_SERVER, CONFIG_DATABASE)

    def api_create_config_data(self, args):
        data = eval("(" + str(args["args"]) + ")")
        return self.database.db_create_config_data(data)

    def api_get_config_data(self, args):
        return self.database.db_get_data_from_config_manager()

    def api_get_value_by_config_id(self, args):
        config_id = args["config_id"]
        return self.database.db_get_config_value_by_id(config_id)


def main():
    app = App('0.0.0.0', 10053)
    app.start()

if __name__ == '__main__':
    main()
