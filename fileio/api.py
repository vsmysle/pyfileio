"""API module."""
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
    """API class."""

    def __init__(self, debug=False):
        """API initialization method.

        :param debug: Debug flag (used for logging).
        :type debug: bool
        """
        self.debug = debug
        self.base_url = 'https://file.io/'
        self.logger = logging.getLogger(__name__)
        self.file_obj_list = []

    def upload(self, alias=None, expiry=None, **kwargs):
        """Upload file to File.io.

        :param alias: File alias (tag).
        :type alias: str

        :param expiry: File expire time (time file.io stores our file).
        :type expiry: str

        :return file_obj: FileIO obj that will help info about file.
        :rtype: .models.FileIO or None if file was not uploaded
        """
        params = {'expiry': expiry if expiry else None}
        data = self._read_file(kwargs['file']) if kwargs['file'] else None
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
        """Download file from file.io.

        :param key: Key of the file that was given during upload.
        :type key: str

        :param alias: Alias of the file that was given during upload.
        :type alias: str

        :return: ???
        :rtype: ???
        """
        files = self.show_uploads(key, alias)
        for item in files:
            if self._check_file_availability(item.expire_at):
                self._download_file(item.url)
                self.file_obj_list.remove(item)
        return True

    def export(self, filename, out_type='json'):
        """Export information about uploaded files.

        :param filename: Filename of the output file.
        :type filename: str

        :param out_type: Type of output file (json or pkl).
        :type out_type: str
        """
        if out_type not in ['pkl', 'json']:
            out_type = 'json'
        with open('%s.%s' % (filename, out_type), 'wb') as out_file:
            if out_type == 'json':
                json.dump(self.file_obj_list, out_file)
            else:
                pickle.dump(self.file_obj_list, out_file,
                            pickle.HIGHEST_PROTOCOL)

    def load(self, filename, in_type='json'):
        """Load infomation about uploaded files.

        :param filename: Filename of the input file.
        :type filename: str

        :param in_type: Type of the input file (json or pkl).
        :type in_type: str
        """
        if in_type not in ['pkl', 'json']:
            out_type = 'json'
        with open('%s.%s' % (filename, in_type), 'rb') as in_file:
            if out_type == 'json':
                self.file_obj_list.append(obj for obj in json.load(in_file))
            else:
                self.file_obj_list.append(obj for obj in pickle.load(in_file))

    def show_uploads(self, key=None, alias=None):
        """Returns list of uploaded files.

        :param key: Key of the file that was given during
                    the upload to file.io.
        :type key: str

        :param alias: Alias of the file that was given during
                      the upload to file.io.
        :type alias: str

        :return files: List of uploaded files.
        :rtype: list
        """
        files = []
        if alias and not key:
            files.append(
                [obj for obj in self.file_obj_list if obj.alias == alias]
            )
        elif key and not alias:
            files.append([obj for obj in self.file_obj_list if obj.key == key])
        elif key and alias:
            files.append(
                [obj for obj in self.file_obj_list if obj.key == key
                 and obj.alias == alias]
            )
        else:
            files = self.file_obj_list
        files = list(set(files))
        return files

    @staticmethod
    def _read_file(filename):
        """Reads the file content.

        :param filename: Filename of the file.
        :type filename: str

        :return file_content: File content.
        :rtype: bytes

        :raises InvalidFile if the file is do not exist of it is a link
        """
        if not path.isfile(filename) or path.islink(filename):
            raise InvalidFile(
                "File do not exist or it is a link!"
            )
        else:
            with open(filename, 'rb') as file_obj:
                return file_obj.read()

    @staticmethod
    def _download_file(url):
        """Downloads the file by the url.

        :param url: Link to the file.
        :type url: str
        """
        resp = requests.get(url, stream=True)
        content_disposition = resp.headers['content-disposition']
        filename = re.findall("filaname=(.+)", content_disposition)
        with open(filename, 'wb') as out_file:
            for chunk in resp.iter_content(chunk_size=1024):
                if chunk:
                    out_file.write(chunk)

    @staticmethod
    def _check_file_availability(obj):
        """Checks whether the file did not expire.

        :param obj: FileIO obj.
        :type obj: .models.FileIO

        :return: True if file did not expire, False otherwise
        :rtype: bool
        """
        if obj.expire_at < datetime.utcnow():
            return True
        return False
