"""."""


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
        return ''
