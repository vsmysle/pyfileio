"""Exceptions module."""


class InvalidFile(Exception):
    """InvalidFile exception.

    Raises when user provided path to incorrect file
    (file do not exist  or it is a link to another file).
    """
    pass


class NoFileOrTextProvided(Exception):
    """NoFileOrTextProvided.

    Raises when user didn't provide any text of file to upload.
    """
    pass
