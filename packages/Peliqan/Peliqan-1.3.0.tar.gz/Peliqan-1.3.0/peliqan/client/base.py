from json import JSONEncoder

import requests

from peliqan.exceptions import PeliqanClientException, PeliqanJsonSerializerException


def _serialize_data(obj):
    if type(obj) == dict:
        formatted_obj = {}
        for k, v in obj.items():
            formatted_obj[k] = _serialize_data(v)

    elif type(obj) in (list, tuple):
        formatted_obj = []
        for v in obj:
            data = _serialize_data(v)
            formatted_obj.append(data)

    elif isinstance(obj, (int, float, type(None), str)):
        formatted_obj = obj

    else:
        try:
            formatted_obj = JSONEncoder().encode(obj)
        except Exception as e:
            try:
                formatted_obj = str(obj)
            except Exception:
                raise PeliqanJsonSerializerException(
                    f"Could not serialize {obj.__class__.__name__} with value {obj}. "
                    f"Original error is {e}"
                )

    return formatted_obj


class BaseClient:

    def __init__(self, jwt, backend_url):
        self.JWT = jwt
        self.BACKEND_URL = backend_url

    def get_headers(self):
        return {
            "Content-Type": "application/json",
            "Authorization": "JWT %s" % self.JWT
        }

    def call_backend(self, method, url, expected_status_code=200, **kwargs):
        if not kwargs.get('headers'):
            headers = self.get_headers()
            kwargs.update(headers=headers)

        json_data = kwargs.get('json')
        if json_data:
            serialized_data = _serialize_data(json_data)
            kwargs['json'] = serialized_data

        response = requests.request(method, url, **kwargs)
        try:
            response_dict = response.json()
        except ValueError:
            response_dict = {}

        # handle error responses
        if response.status_code != expected_status_code:
            error_message = f"Server responded with status code {response.status_code}"
            if response_dict:
                error_message += f" and error details \n{response_dict}"
            raise PeliqanClientException(error_message)

        return response_dict

    def args_to_kwargs(self, args, kwargs):
        """
        Used to allow using both a dict argument or keyword arguments:
        pq.add("contact", name='John', city='NY') or
        pq.add("contact", contact_obj)
        """
        for arg in args:
            if type(arg) != dict:
                raise PeliqanClientException("Only arguments of type dict and kwargs are accepted")
            kwargs.update(**arg)
        return kwargs
