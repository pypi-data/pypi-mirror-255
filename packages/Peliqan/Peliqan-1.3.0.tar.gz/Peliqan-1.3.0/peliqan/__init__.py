__version__ = "1.3.0"
__author__ = 'Peliqan.io'
__credits__ = 'Peliqan.io'

__all__ = [
    "Peliqan",
    "BasePeliqanClient"
]

from peliqan.core import BasePeliqanClient
import os

PELIQAN_URL = os.environ.get("PELIQAN_URL", "https://app.eu.peliqan.io")
"""
The Peliqan environment's url that the client will connect to.
"""


class Peliqan(BasePeliqanClient):
    """
        Import this API client to connect to a Peliqan environment and perform valid operations.

        :param jwt: The jwt token assigned to an Account.

        :param backend_url: The url of the Peliqan environment we want to connect to. A default can be set using the 'PELIQAN_URl' environment variable. If no value is provided it will fall back to "https://app.peliqan.io".
    """

    def __init__(self, jwt, backend_url=PELIQAN_URL):
        super(Peliqan, self).__init__(jwt, backend_url)
