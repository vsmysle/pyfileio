"""."""
import logging
from os import path
import requests

from .models import FileIO
from .exceptions import InvalidFile


class API(object):
    """."""

    def __init__(self, debug=False):
        """."""
        self.debug = debug
        self.base_url = 'https://file.io/'
        self.logger = logging.getLogger(__name__)
        self.file_obj_list = []

    def upload(self, alias=None, expiry=None, **kwargs):
        """."""
        params = {'expiry': expiry if expiry else None}
        data = self.__read_file(kwargs['file']) if kwargs['file'] else None
        resp = requests.post(self.base_url, params=params, data=data,
                             files=data)
        resp_data = resp.json()
        resp_data['alias'] = alias if alias else None

        return FileIO(**resp_data)

    def get_uploads(self):
        """."""
        pass

    def export(self):
        """."""
        pass

    def load(self):
        """."""
        pass

    def get(self, key=None, alias=None):
        """."""
        pass

    @staticmethod
    def __read_file(filename):
        """."""
        if not path.isfile(filename) or path.islink(filename):
            raise InvalidFile(
                "File do not exist or it is a link!"
            )
        else:
            with open(filename, 'rb') as file_obj:
                return file_obj.read()
