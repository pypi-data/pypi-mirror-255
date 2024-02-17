from python_sdk_remote.mini_logger import MiniLogger
from python_sdk_remote.utilities import our_get_env

from .Connector import get_connection

# TODO: We should move this code to python-sdk/infrastructure repo.
#  We should call our_python_init() which calls get_debug() as we might want to add things in the future
os_debug = our_get_env('DEBUG', "False")
is_debug = os_debug.lower() == 'true' or os_debug == '1'

if is_debug:
    MiniLogger.info("Writer.py debug is on debug=" + str(is_debug))


class Writer:
    @staticmethod  # TODO: not used. Can we / shall we have one add_message...()  method?
    def add_message(message: str, severity_id: int) -> None:
        if is_debug:
            MiniLogger.info("add_message" + message + ' ' + str(severity_id),
                            object={"message": message, "log_level": severity_id})
        connection = None
        try:
            # creating connection
            connection = get_connection(schema_name="logger")
            cursor = connection.cursor()
            query = (f"INSERT INTO logger.logger_table (message, severity_id) "
                     f"VALUES ('{message}', {severity_id})")
            cursor.execute(query)
        except Exception as exception:
            MiniLogger.exception("Exception Writer.py Writer.add_message caught", exception)
        finally:
            if connection:
                connection.commit()

    # TODO We prefer to have one INSERT to the logger_table
    # INSERT to logger_table should be disabled by default and activated using combination of json and Environment variable enabling INSERTing to the logger_table
    # This function is called `if self.write_to_sql and self.debug_mode.is_logger_output(component_id=
    #                               self.component_id, logger_output=LoggerOutputEnum.MySQLDatabase, message_severity.value)`
    @staticmethod
    def add_message_and_payload(message: str = None, **kwargs) -> None:
        connection = None
        try:
            connection = get_connection(schema_name="logger")
            params_to_insert = kwargs['object']
            cursor = connection.cursor()
            cursor.execute(
                f"INSERT INTO location.location_table (coordinate) "
                f"VALUES (POINT({params_to_insert.get('latitude') or 0},{params_to_insert.get('longitude') or 0}));")
            coordinate_id = cursor.lastrowid

            params_to_insert.pop('latitude', None)
            params_to_insert.pop('longitude', None)

            params_to_insert['location_id'] = coordinate_id
            listed_values = list(params_to_insert.values())
            joined_keys = ','.join(list(params_to_insert.keys()))
            if message is not None:
                listed_values.append(message)
                joined_keys += (',' if joined_keys else '') + 'message'

            placeholders = ','.join(['%s'] * len(listed_values))
            query = f"INSERT INTO logger.logger_table ({joined_keys}) VALUES ({placeholders})"
            cursor = connection.cursor()
            cursor.execute(query, listed_values)
        except Exception as exception:
            MiniLogger.exception("Exception logger Writer.py add_message_and_payload ", exception)
        finally:
            if connection:
                connection.commit()
