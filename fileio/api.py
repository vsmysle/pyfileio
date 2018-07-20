"""."""
import logging
from datetime import datetime
from os import path
import json
import pickle
import re
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
        if resp_data['success']:
            resp_data['alias'] = alias if alias else None
            file_obj = FileIO(**resp_data)
            self.file_obj_list.append(file_obj)
            return file_obj
        return None

    def download(self, key=None, alias=None):
        """."""
        if alias:
            files = [obj for obj in self.file_obj_list if obj.alias == alias]
            for item in files:
                self.__check_file_availability(item.expire_at)
                self.__download_file(item.url)
                self.file_obj_list.remove(item)
        elif key:
            files = [obj for obj in self.file_obj_list if obj.key == key]
            for item in files:
                self.__check_file_availability(item.expire_at)
                self.__download_file(item.url)
                self.file_obj_list.remove(item)
        else:
            for item in self.file_obj_list:
                self.__check_file_availability(item.expire_at)
                self.__download_file(item.url)
                self.file_obj_list.remove(item)
        return True

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

    def show(self, key=None, alias=None):
        """."""
        if alias:
            return [obj for obj in self.file_obj_list if obj.alias == alias]
        elif key:
            return [obj for obj in self.file_obj_list if obj.key == key]
        return self.file_obj_list

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

    @staticmethod
    def __download_file(url):
        """."""
        resp = requests.get(url, stream=True)
        content_disposition = resp.headers['content-disposition']
        filename = re.findall("filaname=(.+)", content_disposition)
        with open(filename, 'wb') as out_file:
            for chunk in resp.iter_content(chunk_size=1024):
                if chunk:
                    out_file.write(chunk)

    @staticmethod
    def __check_file_availability(obj):
        """."""
        if obj.expire_at < datetime.utcnow():
            return True
        return False
