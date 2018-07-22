"""API module."""
import logging
from datetime import datetime
from os import path
import json
import pickle
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

    def upload(self, tag=None, expiry=None, **kwargs):
        """Upload file to File.io.

        :param tag: File tag (tag).
        :type tag: str

        :param expiry: File expire time (time file.io stores our file).
        :type expiry: str

        :return file_obj: FileIO obj that will help info about file.
        :rtype: .models.FileIO or None if file was not uploaded
        """
        params = {'expiry': expiry if expiry else None}

        file_data = {}

        data = kwargs['text'] if kwargs.get('text') else None

        filename = kwargs.get('filename')
        if filename:
            file_data = {
                'file': (
                    filename.split('/')[-1],
                    self._read_file(filename) if filename else None
                )
            }

        resp = requests.post(self.base_url, params=params, data=data,
                             files=file_data)
        resp_data = resp.json()
        if resp_data['success']:
            resp_data['tag'] = tag if tag else None
            resp_data['location'] = path.abspath(filename)
            file_obj = FileIO(**resp_data)
            self.file_obj_list.append(file_obj)
            return file_obj
        return None

    def download(self, key=None, tag=None):
        """Download file from file.io.

        :param key: Key of the file that was given during upload.
        :type key: str

        :param tag: Tag of the file that was given during upload.
        :type tag: str

        :return: ???
        :rtype: ???
        """
        files = self.show_uploads(key, tag)
        for item in files:
            print(item)
            if self._check_file_availability(item.expire_at):
                response = self._download_file(item.link)
                self._save_file(response, item.location)
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
                self.file_obj_list += [obj for obj in json.load(in_file)]
            else:
                self.file_obj_list += [obj for obj in pickle.load(in_file)]

    def show_uploads(self, key=None, tag=None):
        """Returns list of uploaded files.

        :param key: Key of the file that was given during
                    the upload to file.io.
        :type key: str

        :param tag: Tag of the file that was given during
                      the upload to file.io.
        :type tag: str

        :return files: List of uploaded files.
        :rtype: list
        """
        files = []
        if tag and not key:
            files += [obj for obj in self.file_obj_list if obj.tag == tag]
        elif key and not tag:
            files += [obj for obj in self.file_obj_list if obj.key == key]
        elif key and tag:
            files += [obj for obj in self.file_obj_list if obj.key == key
                      and obj.tag == tag]
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

        :return resp: Response from file.io.
        :rtype: requests.Response
        """
        return requests.get(url, stream=True)

    @staticmethod
    def _save_file(response, location):
        """Saves file under a given location.

        :param response: Response from file.io.
        :type response: bytes

        :param location: Location of the output file.
        :type location: str
        """
        with open(location, 'wb') as out_file:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    out_file.write(chunk)

    @staticmethod
    def _check_file_availability(expire_time):
        """Checks whether the file did not expire.

        :param expire_time: FileIO obj expire_at attribute.
        :type expire_time: datetime.datetime

        :return: True if file did not expire, False otherwise
        :rtype: bool
        """
        if expire_time > datetime.utcnow():
            return True
        return False
