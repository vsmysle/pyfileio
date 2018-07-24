"""API module."""
import logging
from datetime import datetime
import os
import json
import pickle
import requests

from .models import FileIO
from .exceptions import InvalidFile, NoFileOrTextProvided, APIConnectionError


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
        self.json_export_path = 'exported.json'
        self.pkl_export_path = 'exported.pkl'
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

        path = kwargs.get('path')

        if path:
            file_data = {
                'file': (
                    path.split('/')[-1],
                    self._read_file(path)
                )
            }

        if not path and not data:
            raise NoFileOrTextProvided(
                "Please, provide file or text for uploading it!"
            )

        resp = requests.post(self.base_url, params=params, data=data,
                             files=file_data)

        # convert response to python dict
        data = resp.json()

        # get response status code
        status_code = data['error'] if data['success'] is False else 200

        # parsing response status code
        self.__parse_status_code(status_code)

        # assign tag and abs path values to FileIO attrs
        data['tag'] = tag if tag else None
        data['path'] = os.path.abspath(path)
        file_obj = FileIO(**data)
        self.file_obj_list.append(file_obj)
        return file_obj

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
                self._save_file(response, item.path)
                self.file_obj_list.remove(item)
        return True

    def export(self, path=None, out_type=None):
        """Export information about uploaded files.

        :param path: Path to the output file.
        :type path: str

        :param out_type: Type of output file (json or pkl).
        :type out_type: str
        """
        valid_types = ['pkl', 'json']

        if not path and out_type == 'json':
            export_path = self.json_export_path
        elif not path and out_type == 'pkl':
            export_path = self.pkl_export_path
        elif not path and out_type is None:
            export_path = self.json_export_path
        elif path and out_type is None or out_type in valid_types:
            if path.split('.')[-1] in valid_types and out_type is None:
                export_path = path
            else:
                export_path = '%s.%s' % (
                    path, out_type if out_type in valid_types else 'json'
                )
        else:
            export_path = '%s.%s' % (path, 'json')

        out_type = export_path.split('.')[-1]

        prefix = 'b' if out_type == 'pkl' else ''
        with open(export_path, 'w%s' % prefix) as out_file:
            if out_type == 'json':
                out_dict = {
                    'uploaded': [obj.__dict__ for obj in self.file_obj_list]
                }
                json.dump(out_dict, out_file, sort_keys=True, indent=4)
            else:
                pickle.dump(self.file_obj_list, out_file,
                            pickle.HIGHEST_PROTOCOL)

    def load(self, path, in_type=None):
        """Load infomation about uploaded files.

        :param path: Filename of the input file.
        :type path: str

        :param in_type: Type of the input file (json or pkl).
        :type in_type: str
        """

        # setting to default 'json' if in_type is different from pkl or json
        if in_type not in ['pkl', 'json']:
            in_type = 'json'

        # if file extension is pkl
        if path.split('.')[-1] == 'pkl':
            in_type = 'pkl'

        # prefix for opening file in binary mode if in_type = 'pkl'
        prefix = 'b' if in_type == 'pkl' else ''

        load_path = '%s.%s' % (''.join(path.split('.')[:-1]), in_type)

        # opening the file for reading
        with open(load_path, 'r%s' % prefix) as in_file:
            if in_type == 'json':
                self.file_obj_list += [
                    FileIO(**obj) for obj in json.load(in_file)['uploaded']
                ]
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
        if not os.path.isfile(filename) or os.path.islink(filename):
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
    def _encrypt_file(file_content, public_key):
        """Encrypts file content.

        :param file_content: Content of the file.
        :type file_content: bytes

        :param public_key: Receiver public key.
        :type public_key: ???
        """
        pass

    @staticmethod
    def _decrypt_file(ciphertext, private_key):
        """Decrypts file content.

        :param ciphertext: Ciphertext.
        :type ciphertext: bytes

        :param private_key: Receipient private key.
        :type private_key: ???
        """
        pass

    @staticmethod
    def _save_file(response, path):
        """Saves file under a given location.

        :param response: Response from file.io.
        :type response: bytes

        :param path: Location of the output file.
        :type path: str
        """
        with open(path, 'wb') as out_file:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    out_file.write(chunk)

    @staticmethod
    def _check_file_availability(expire_time):
        """Checks whether the file did not expire.

        :param expire_time: FileIO obj expire_at attribute.
        :type expire_time: str

        :return: True if file did not expire, False otherwise
        :rtype: bool
        """
        if expire_time > datetime.utcnow().isoformat():
            return True
        return False

    @staticmethod
    def __parse_status_code(status_code):
        """Parses status code from remote server response.

        :param status_code: Response status code.
        :type status_code: int

        :raises APIConnectionError if status code != 200
        """
        if status_code == 200:
            return
        elif status_code == 404:
            raise APIConnectionError("Message was not found on file.io!")
        elif status_code == 429:
            raise APIConnectionError("Too many requests to file.io!")
        else:
            raise APIConnectionError(
                "Unknown error with %d status code!" % status_code
            )
