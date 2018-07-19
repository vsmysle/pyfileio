"""."""
import logging
from os import path
import json
import pickle
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

    def get_uploads(self):
        """."""
        return self.file_obj_list

    def upload(self, alias=None, expiry=None, **kwargs):
        """."""
        params = {'expiry': expiry if expiry else None}
        data = self.__read_file(kwargs['file']) if kwargs['file'] else None
        resp = requests.post(self.base_url, params=params, data=data,
                             files=data)
        resp_data = resp.json()
        resp_data['alias'] = alias if alias else None
        return FileIO(**resp_data) if resp_data['success'] is True else None

    def export(self, filename, out_type='json'):
        """."""
        if out_type not in ['pkl', 'json']:
            out_type = 'json'
        with open('%s.%s' % (filename, out_type), 'wb') as out_file:
            if out_type == 'json':
                json.dump(self.file_obj_list, out_file)
            else:
                pickle.dump(self.file_obj_list, out_file,
                            pickle.HIGHEST_PROTOCOL)

    def load(self, filename, in_type='json'):
        """."""
        if in_type not in ['pkl', 'json']:
            out_type = 'json'
        with open('%s.%s' % (filename, in_type), 'rb') as in_file:
            if out_type == 'json':
                self.file_obj_list.append(obj for obj in json.load(in_file))
            else:
                self.file_obj_list.append(obj for obj in pickle.load(in_file))

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
