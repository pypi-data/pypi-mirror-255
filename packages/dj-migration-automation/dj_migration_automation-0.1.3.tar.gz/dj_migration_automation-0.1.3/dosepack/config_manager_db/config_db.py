import couchdb
from couchdb.client import Server
from dosepack.error_handling.error_handler import create_response, error


class Database(object):
    """Base class for storing the config detail in couchdb."""
    def __init__(self, server_ip, database_name):
        self.my_server = Server(server_ip)
        try:
            self.db = self.my_server.create(database_name)
        except Exception:
            self.db = self.my_server[database_name]

    def db_create_config_data(self, data_info):
        """ Create or update a row in config_manager database

            Args:
                data_info (dict): dict of all config values to be stored in database

            Returns:
                json: success or the failure response along with the id of the document.
        """
        try:
            data = self.db.get("config_manager")
            config_data = data["data"]
            for key, value in data_info.items():
                config_data[key] = {"config_name": value["config_name"], "config_value": value["config_value"],
                                    "config_id": value["config_id"]}
            data_id = data.id
            self.db[data.id] = data
        except couchdb.http.ResourceConflict:
            # settings.logger.info("EXCEPTION: Document update conflict.")
            return error(1013, "Problem in updating data.")
        except Exception:
            doc = {"_id": "config_manager", "data": data_info}
            data_id, rev = self.db.save(doc)

        return create_response(data_id)

    def db_get_data_from_config_manager(self):
        """ Retrieve data from database

            Args:

            Returns:
                {}
        """
        try:
            data = self.db.get("config_manager")
            return create_response(data["data"])
        except Exception as e:
            # settings.logger.info("ERROR: unable to retrieve data from couchdb. Error msg: " + str(e))
            return create_response({})

    def db_get_config_value_by_id(self, config_id):
        """ Get the config value for given config Id.

            Args:
                config_id (str): config Id

            Returns:
                 config value of the given config id, if available.
        """
        try:
            data = self.db.get("config_manager")
            config_value = data["data"][str(config_id)]["config_value"]
            return create_response(config_value)
        except Exception as e:
            # settings.logger.info("ERROR: unable to retrieve data from couchdb. Error msg: " + str(e))
            return error(1004, "Value is not available for the Config id.")


if __name__ == '__main__':
    database = Database("http://54.67.35.135:5984/", "config_db")
    data = {
        "car1": {"config_name": "car1", "config_id": "car1", "config_value": "192.168.1.144"},
        "car2": {"config_name": "car2", "config_id": "car2", "config_value": "192.168.1.167"},
        "car3": {"config_name": "car3", "config_id": "car3", "config_value": "192.168.1.103"},
        "robot4": {"config_name": "robot4", "config_id": "robot4", "config_value": "172.168.1.101"},
        "robot6": {"config_name": "robot6", "config_id": "robot6", "config_value": "172.168.1.102"},
        "backend": {"config_name": "backend", "config_id": "backend", "config_value": "54.67.35.135:10008"},
        "interface": {"config_name": "dosepack_interface", "config_id": "interface",
                      "config_value": "54.67.35.135:5555"},
        "printer": {"config_name": "printer", "config_id": "printer", "config_value": "192.168.1.142"}
    }
    # database.db_create_config_data(data)
    print(database.db_get_data_from_config_manager())
    print(database.db_get_config_value_by_id("robot6"))
    print(database.db_get_config_value_by_id("robot"))
