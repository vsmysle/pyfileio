"""Models module."""
from datetime import datetime
from dateutil.relativedelta import relativedelta


class FileIO(object):
    """FileIO class."""

    def __init__(self, **kwargs):
        """FileIO initialization method."""
        self.__dict__.update(kwargs)
        duration, period = self.expiry.split()

        duration = int(duration)
        time_now = datetime.utcnow()
        if period == 'days':
            self.expire_at = time_now + relativedelta(days=duration)
        elif period == 'weeks':
            self.expire_at = time_now + relativedelta(weeks=duration)
        elif period == 'months':
            self.expire_at = time_now + relativedelta(months=duration)
        elif period == 'years':
            self.expire_at = time_now + relativedelta(years=duration)

        self.expire_at = self.expire_at.isoformat()

    def __getattr__(self, key):
        """Get attribute method.

        :return: None if class instanse doens't have provided attribute
        """
        return None

    def __repr__(self):
        """Object representation in string."""
        return '<%s key=%s, link=%s, location=%s, tag=%s, expire_at=%s>' % (
            self.__class__.__name__,
            self.key,
            self.link,
            self.path,
            self.tag,
            self.expire_at
        )
