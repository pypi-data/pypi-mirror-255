from peliqan.client.base import BaseClient


class SFTPClient(BaseClient):
    def __init__(self, connection, jwt, backend_url):
        super(SFTPClient, self).__init__(jwt, backend_url)
        self.connection = connection

    def sftp_via_proxy(self, path, action, **kwargs):
        payload = {
            "connection": self.connection,
            "path": path,
            "action": action,
            "kwargs": kwargs
        }

        url = f"{self.BACKEND_URL}/api/proxy/sftp/"
        return self.call_backend('post', url, json=payload)

    def read_file(self, path, *args, **kwargs):
        kwargs = self.args_to_kwargs(args, kwargs)
        response = self.sftp_via_proxy(path, 'read_file', **kwargs)
        return response
    
    def dir(self, path, *args, **kwargs):
        kwargs = self.args_to_kwargs(args, kwargs)
        response = self.sftp_via_proxy(path, 'dir', **kwargs)
        return response

