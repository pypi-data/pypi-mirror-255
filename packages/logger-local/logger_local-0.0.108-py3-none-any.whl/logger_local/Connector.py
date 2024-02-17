import mysql.connector
from python_sdk_remote.utilities import get_sql_hostname, get_sql_username, get_sql_password

connections_pool = {}


# We are using the database directly to avoid cyclic dependency
def get_connection(schema_name: str) -> mysql.connector:
    if (schema_name in connections_pool and
            connections_pool[schema_name] and
            connections_pool[schema_name] and
            connections_pool[schema_name].is_connected()):
        return connections_pool[schema_name]
    else:
        connection = mysql.connector.connect(
            host=get_sql_hostname(),
            user=get_sql_username(),
            password=get_sql_password(),
            database=schema_name
        )
        connections_pool[schema_name] = connection
        return connection
