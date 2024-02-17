from python_sdk_remote.mini_logger import MiniLogger

from .Connector import get_connection

component_cache = {}


class Component:
    @staticmethod
    def get_details_by_component_id(component_id: int) -> dict:
        # sometimes we get a string, sometimes an int (json keys are always strings)
        if component_id in component_cache:
            return component_cache[component_id]
        try:
            connection = get_connection(schema_name="component")
            cursor = connection.cursor()
            sql_query = ("SELECT name, component_type, component_category, testing_framework, api_type "
                         "FROM component.component_table WHERE component_id = %s")
            cursor.execute(sql_query, (component_id,))
            result = cursor.fetchone()
            if not result:
                raise Exception(f"Component {component_id} not found in component.component_table")
            component_json = {
                "component_id": component_id,
                "component_name": result[0],
                "component_type": result[1],
                "component_category": result[2],
                "testing_framework": result[3],
                "api_type": result[4]
            }
            component_cache[component_id] = component_json
            return component_json
        except Exception as exception:
            MiniLogger.exception("Logger.Component.get_details_by_component_id", exception)
            raise exception
