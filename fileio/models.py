"""."""
import datetime


class FileIO(object):
    """."""

    def __init__(self, key, alias, link, expiry):
        """."""
        self.key = key
        self.alias = alias
        self.link = link
        self.expiry = expiry

    def __getattr__(self, key):
        """."""
        return None

    def __repr__(self):
        """."""
        return '<%s key=%s alias=%s expiry=%s>' % (self.__class__.__name__,
                                                   self.key,
                                                   self.alias,
                                                   self.expiry)
