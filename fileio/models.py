"""."""
from datetime import datetime
from dateutil.relativedelta import relativedelta


class FileIO(object):
    """."""

    def __init__(self, key, alias, link, expiry):
        """."""
        self.key = key
        self.alias = alias
        self.link = link
        self.expiry = expiry

        duration, period = expiry.split()[1]

        time_now = datetime.utcnow()
        if period == 'days':
            self.expire_at = time_now + relativedelta(days=duration)
        elif period == 'weeks':
            self.expire_at = time_now + relativedelta(weeks=duration)
        elif period == 'months':
            self.expire_at = time_now + relativedelta(months=duration)
        elif period == 'years':
            self.expire_at = time_now + relativedelta(years=duration)

    def __getattr__(self, key):
        """."""
        return None

    def __repr__(self):
        """."""
        return '<%s key=%s alias=%s expiry=%s expire_at=%s>' % (
            self.__class__.__name__,
            self.key,
            self.alias,
            self.expiry,
            self.expire_at
        )
