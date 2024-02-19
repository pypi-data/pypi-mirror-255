from peliqan.exceptions import PeliqanClientException
from peliqan.client import BaseClient


class BackendServiceClient(BaseClient):
    def __init__(self, jwt, backend_url):
        super(BackendServiceClient, self).__init__(jwt, backend_url)
        self._cache = {
            'connection': {},
            'database': {},
            'schema': {},
            'table': {}
        }

    def get_cached_results(self, resource_type, resource_id_or_name, property_name):
        try:
            resource_id_or_name = resource_id_or_name.lower()
        except AttributeError:
            pass

        resource_type = resource_type.lower()
        property_name = property_name.lower()
        return self._cache.get(resource_type, {}).get(resource_id_or_name, {}).get(property_name)

    def _cache_connection_data(self, data):
        connection_name = data.get('connection_name', '')
        if connection_name:
            connection_name = connection_name.lower()
            connection_id = data['connection_id']
            if connection_id:
                data_to_cache = {
                    connection_id: {
                        'connection_name': connection_name
                    },
                    connection_name: {
                        'connection_id': connection_id
                    }
                }
                self._cache['connection'].update(data_to_cache)

    def _cache_database_data(self, data):
        database_name = data.get('database_name', '')
        if database_name:
            database_name = database_name.lower()
            database_id = data['database_id']
            if database_id:
                data_to_cache = {
                    database_id: {
                        'database_name': database_name
                    },
                    database_name: {
                        'database_id': database_id
                    }
                }
                self._cache['database'].update(data_to_cache)

    def _cache_schema_data(self, data):
        schema_name = data.get('schema_name', '')
        if schema_name:
            schema_name = schema_name.lower()
            schema_id = data['schema_id']
            if schema_id:
                data_to_cache = {
                    schema_id: {
                        'schema_name': schema_name
                    },
                    schema_name: {
                        'schema_id': schema_id
                    }
                }
                self._cache['schema'].update(data_to_cache)

    def _cache_table_and_field_data(self, data):
        table_name = data.get('table_name', '')
        if table_name:
            table_name = table_name.lower()
            table_id = data['table_id']
            if table_id:
                data_to_cache = {
                    table_name: {
                        'table_id': table_id,
                    },
                    table_id: {
                        'table_name': table_name
                    }
                }
                self._cache['table'].update(data_to_cache)

                # cache field
                field_name = data.get('field_name', '')
                if field_name:
                    field_physical_name = data['field_physical_name']
                    if field_physical_name:
                        data_to_cache[table_name].update({field_name: field_physical_name})
                        data_to_cache[table_id].update({field_name: field_physical_name})

    def _update_cache(self, data):
        self._cache_connection_data(data)
        self._cache_database_data(data)
        self._cache_schema_data(data)
        self._cache_table_and_field_data(data)

    def find_connection(self, connection_id=None, connection_name=None):
        """

        :param connection_id:
        :param connection_name:
        :return:
        """
        url = f"{self.BACKEND_URL}/api/database/resource/lookup/connection/"
        data = {
            'connection_id': connection_id,
            'connection_name': connection_name,
        }
        data = self.call_backend("get", url, json=data)

        self._update_cache(data)
        return data

    def find_database(self, connection_id=None, connection_name=None, database_id=None, database_name=None):
        """

        :param connection_id:
        :param connection_name:
        :param database_id:
        :param database_name:
        :return:
        """
        url = f"{self.BACKEND_URL}/api/database/resource/lookup/database/"
        data = {
            'connection_id': connection_id,
            'connection_name': connection_name,
            'database_id': database_id,
            'database_name': database_name,
        }
        data = self.call_backend("get", url, json=data)

        self._update_cache(data)
        return data

    def find_schema(self, connection_id=None, connection_name=None, database_id=None, database_name=None,
                    schema_id=None, schema_name=None):
        """

        :param connection_id:
        :param connection_name:
        :param database_id:
        :param database_name:
        :param schema_id:
        :param schema_name:
        :return:
        """
        url = f"{self.BACKEND_URL}/api/database/resource/lookup/schema/"
        data = {
            'connection_id': connection_id,
            'connection_name': connection_name,
            'database_id': database_id,
            'database_name': database_name,
            'schema_id': schema_id,
            'schema_name': schema_name,
        }
        data = self.call_backend("get", url, json=data)

        self._update_cache(data)
        return data

    def find_table_or_field(
        self, connection_id=None, connection_name=None, database_id=None, database_name=None,
        schema_id=None, schema_name=None, table_id=None, table_name=None,
        field_id=None, field_name=None
    ):
        """
        Find the table information by passing in a table_id or table_name.
        Optionally pass in a field_id or field_name to retrieve that fields info.

        We can also pass in the optional connection_id/connection_name and optional database_id/database_name
        if we want to restrict the search.

        :param connection_id: (Optional) id of the connection the table belongs to.
        :param connection_name: (Optional) name of the connection the table belongs to.
        :param database_id: (Optional) name of the database the table belongs to.
        :param database_name: (Optional) name of the database the table belongs to.
        :param schema_id: (Optional) id of the schema the table belongs to.
        :param schema_name: (Optional) name of the schema the table belongs to.
        :param table_id: id of the table to find.
        :param table_name: name of the table to find.
        :param field_id: (Optional) id of the field to find.
        :param field_name: (Optional) name of the field to find.
        :return:
        """
        url = f"{self.BACKEND_URL}/api/database/resource/lookup/table/"
        data = {
            'connection_id': connection_id,
            'connection_name': connection_name,
            'database_id': database_id,
            'database_name': database_name,
            'schema_name': schema_name,
            'table_id': table_id,
            'table_name': table_name,
            'field_id': field_id,
            'field_name': field_name
        }
        data = self.call_backend("get", url, json=data)

        self._update_cache(data)
        return data

    def find_resource(self, resource_type, resource_id=None, resource_name=None, **kwargs):

        if resource_type not in ['connection', 'database', 'schema', 'table']:
            raise PeliqanClientException(f"{resource_type} is not valid. "
                                         f"Allowed resource types are 'connection', 'database', 'schema', 'table'.")

        if not resource_id and not resource_name:
            raise PeliqanClientException("resource_id or resource_name must be provided as kwargs.")

        if resource_type.lower() == 'connection':
            data = {
                'connection_id': resource_id,
                'connection_name': resource_name
            }
            # find connection
            return self.find_connection(**data)
        elif resource_type.lower() == 'database':
            data = {
                'database_id': resource_id,
                'database_name': resource_name,
            }
            # find database
            return self.find_database(**data, **kwargs)
        elif resource_type.lower() == 'schema':
            data = {
                'schema_id': resource_id,
                'schema_name': resource_name
            }
            return self.find_schema(**data, **kwargs)
        elif resource_type.lower() == 'table':
            data = {
                'table_id': resource_id,
                'table_name': resource_name
            }
            return self.find_table_or_field(**data, **kwargs)
        else:
            raise PeliqanClientException(f"{resource_type} is not valid. "
                                         f"Allowed resource types are 'connection', 'database', 'schema', 'table'.")

    def _is_refresh_allowed(self, resource_type):
        if resource_type not in ['connection', 'database', 'schema', 'table']:
            raise PeliqanClientException(f"{resource_type} is not valid. "
                                         f"Allowed resource types are 'connection', 'database', 'schema', 'table'.")

    def _get_resource_id(self, resource_id, resource_name, resource_type, **kwargs):
        if not resource_id and not resource_name:
            raise PeliqanClientException(f"{resource_type}_id or {resource_type}_name must be provided as kwargs.")

        elif not resource_id and resource_name:
            resource_id = self.get_cached_results(resource_type, resource_name, f'{resource_type}_id')

        if not resource_id:
            lookup_data = self.find_resource(resource_type=resource_type, resource_name=resource_name, **kwargs)
            resource_id = lookup_data[f'{resource_type}_id']

        return resource_id

    def refresh_resource(self, resource_type, refresh_baseurl, resource_name=None, resource_id=None, **kwargs):
        self._is_refresh_allowed(resource_type)
        resource_id = self._get_resource_id(resource_id, resource_name, resource_type, **kwargs)
        url = refresh_baseurl % resource_id

        # call sync url
        response = self.call_backend("get", url, expected_status_code=200)
        prepared_response = {
            'task_id': response['task_id'],
            'detail': response['detail'],
            'syncing': response['syncing']
        }
        return prepared_response

    def get_refresh_resource_task_status(self, resource_type, refresh_baseurl, resource_name=None, resource_id=None,
                                         task_id='', **kwargs):
        self._is_refresh_allowed(resource_type)
        resource_id = self._get_resource_id(resource_id, resource_name, resource_type, **kwargs)
        url = refresh_baseurl % resource_id + f"?task_id={task_id}"

        # call sync task status url
        return self.call_backend('get', url, expected_status_code=200)

    def update_record(self, url, data):
        return self.call_backend("patch", url, json=data, expected_status_code=204)

    def get_cdclogs(self, table_id, writeback_status, change_type, latest_changes_first=False):
        url = f"{self.BACKEND_URL}/api/database/cdclogs/table/{table_id}/?latest_changes_first={latest_changes_first}"

        if writeback_status or change_type:
            url += "&"
            if writeback_status:
                url += f"writeback_status={writeback_status}&"

            if change_type:
                url += f"change_type={change_type}"

        response_dict = self.call_backend("get", url)
        return response_dict

    def update_writeback_status(self, table_id, change_id, writeback_status):
        url = f"{self.BACKEND_URL}/api/database/cdclogs/table/{table_id}/changes/{change_id}/writeback_status/"

        data = {
            "change_id": change_id,
            "writeback_status": writeback_status
        }

        response_dict = self.call_backend("patch", url, json=data)
        return response_dict

    def get_databases(self):
        url = f"{self.BACKEND_URL}/api/applications"
        response_dict = self.call_backend("get", url)
        return response_dict

    def update_table(self, id, name=None, table_type=None, query=None, external=None, primary_field_id=None,
                     settings=None):
        url = f"{self.BACKEND_URL}/api/database/tables/%s/" % id
        data = {}
        if name:
            data["name"] = name
        if table_type:
            data["table_type"] = table_type
        if query:
            data["query"] = query
        if external:
            data["external"] = external
        if primary_field_id:
            data["primary_field_id"] = primary_field_id
        if settings:
            data["settings"] = settings
        response_dict = self.call_backend("patch", url, json=data)
        return response_dict

    def update_database_metadata(self, id, description=None, tags=None):
        url = f"{self.BACKEND_URL}/api/applications/%s/data-catalog/" % id
        data = {}
        if description:
            data["description"] = description
        if tags:
            data["tags"] = tags
        response_dict = self.call_backend("patch", url, json=data)
        return response_dict

    def update_table_metadata(self, id, description=None, tags=None):
        url = f"{self.BACKEND_URL}/api/database/tables/%s/data-catalog/" % id
        data = {}
        if description:
            data["description"] = description
        if tags:
            data["tags"] = tags
        response_dict = self.call_backend("patch", url, json=data)
        return response_dict

    def update_field_metadata(self, id, description=None, tags=None):
        url = f"{self.BACKEND_URL}/api/database/fields/%s/data-catalog/" % id
        data = {}
        if description:
            data["description"] = description
        if tags:
            data["tags"] = tags
        response_dict = self.call_backend("patch", url, json=data)
        return response_dict

    def get_interface(self, interface_id):
        url = f"{self.BACKEND_URL}/api/interfaces/{interface_id}/"
        return self.call_backend("get", url)

    def get_interface_state(self, interface_id):
        data = self.get_interface(interface_id)
        return data.get('state', '')

    def set_interface_state(self, interface_id, state):
        url = f"{self.BACKEND_URL}/api/interfaces/{interface_id}/"
        data = {'state': state}
        return self.call_backend("patch", url, json=data)

    def get_logs(self, connection_id):
        url = f"{self.BACKEND_URL}/api/servers/{connection_id}/logs"
        return self.call_backend("get", url)
