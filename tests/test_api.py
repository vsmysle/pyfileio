"""File.io API tests."""
from os import path, remove


def test_upload(api):
    """Testing file upload functionality.

    :param api: Instance of fileio.API class.
    :type api: fileio.API
    """
    # upload the file to file.io servers
    uploaded_file = api.upload(
        tag='test_upload',
        expiry='1w',
        path='tests/test_file.txt'
    )

    assert uploaded_file.link
    assert uploaded_file.key
    assert uploaded_file.tag
    assert uploaded_file.path


def test_download(api):
    """Testing file upload functionality.

    :param api: Instance of fileio.API class.
    :type api: fileio.API
    """
    # upload file prior to download
    uploaded_file = api.upload(
        tag='test_upload',
        expiry='1w',
        path='tests/test_file.txt'
    )

    # check that instance of FileIO has these fields
    assert uploaded_file.link
    assert uploaded_file.key
    assert uploaded_file.tag
    assert uploaded_file.path

    # remove the uploaded file from the os
    remove('tests/test_file.txt')

    # download and save the file
    api.download(tag='test_upload')

    # check that file was saved in a filesystem
    assert path.isfile('tests/test_file.txt')


def test_export(api):
    """Testing export method functionality.

    :param api: Instance of fileio.API class.
    :type api: fileio.API
    """
    # upload file to file.io servers
    uploaded_file = api.upload(
        tag='test_file',
        expiry='1d',
        path='tests/test_file.txt'
    )

    # check that instance of FileIO has these fields
    assert uploaded_file.link
    assert uploaded_file.key
    assert uploaded_file.tag
    assert uploaded_file.path

    # check that the uploaded file was added to uploaded files list
    assert api.show_uploads()

    # testing that export works
    api.export('tests/files_data.json')

    # check that the exported file exists
    assert path.isfile('tests/files_data.json')

    remove('tests/files_data.json')

    # testing that export in pkl works
    api.export(out_type='pkl')

    # check that the exported file exists
    assert path.isfile('exported.pkl')

    remove('exported.pkl')

    # testong that export in pkl works
    api.export('tests/exported.pkl')

    # check that the exported file exists
    assert path.isfile('tests/exported.pkl')

    remove('tests/exported.pkl')

    # testing that export in json with default path works
    api.export()

    # check that exported file exists
    assert path.isfile('exported.json')

    remove('exported.json')

    # check that export with provided path works
    api.export('tests/exporte.d.pkl', out_type='json')

    # testing that export works
    assert path.isfile('tests/exporte.d.pkl.json')

    remove('tests/exporte.d.pkl.json')

    # check that export works correctly with strange path
    api.export('tests/t.e.s.t.p.k.l', out_type='pkl')

    # testing that export works
    assert path.isfile('tests/t.e.s.t.p.k.l.pkl')

    remove('tests/t.e.s.t.p.k.l.pkl')


def test_load(api):
    """Testing load method functionality.

    :param api: Instance of fileio.API class.
    :type api: fileio.API
    """
    # upload file to file.io servers
    uploaded_file = api.upload(
        tag='test_file',
        expiry='1d',
        path='tests/test_file.txt'
    )

    # check that instance of FileIO has these fields
    assert uploaded_file.link
    assert uploaded_file.key
    assert uploaded_file.tag
    assert uploaded_file.path

    # check that the uploaded file was added to uploaded files list
    assert api.show_uploads()

    # check that our list is not empty
    assert api.file_obj_list

    # export the file in json format
    api.export('tests/exported.json')

    # check that exported file exists
    assert path.isfile('tests/exported.json')

    # set it to empty list
    api.file_obj_list = []

    # load the file in json format
    api.load('tests/exported.json')

    # remove the file
    remove('tests/exported.json')

    # check that the uploaded file was added to uploaded files list
    assert api.show_uploads()

    # check that our list is not empty
    assert api.file_obj_list

    # export the file in pkl format
    api.export('tests/exported.pkl')

    # set it to empty list
    api.file_obj_list = []

    # load the file in pkl format
    api.load('tests/exported.pkl')

    # remove exported.pkl file
    remove('tests/exported.pkl')

    # check that the uploaded file was added to uploaded files list
    assert api.show_uploads()

    # check that our list is not empty
    assert api.file_obj_list


def test_show_uploads(api):
    """Testing show uploaded file functionality.

    :param api: Instance of fileio.API class.
    :type api: fileio.API
    """
    # checking that we have empty list if we haven't uploaded any files yet
    assert isinstance(api.show_uploads(), list)

    # upload the file
    uploaded_file = api.upload(
        tag='test_file',
        expiry='2d',
        path='tests/test_file.txt'
    )

    # check that we have our uploaded file in file_obj_list
    assert 1, len(api.show_upload())
    print(uploaded_file)
    print(api.show_uploads())

    # upload one more file for testing the key and tag searching
    another_uploaded_file = api.upload(
        tag='another_tag',
        expiry='1d',
        path='tests/test_file.txt'
    )

    # check that sorting by tags works
    assert api.show_uploads(tag='test_file')[0] == uploaded_file

    # check that sorting by keys works
    assert api.show_uploads(key=uploaded_file.key)[0] == uploaded_file

    # check that sorting by tag and key works
    assert api.show_uploads(
        tag='test_file', key=uploaded_file.key
    )[0] == uploaded_file

    uploads = api.show_uploads()

    # check that show uploads returns us our 2 uploaded files
    assert 2, len(uploads)

    # check that all uploaded files are in 'uploads' list
    assert another_uploaded_file and uploaded_file in uploads
