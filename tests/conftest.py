"""Pytest configuration file."""
import time
import pytest

from fileio import API


@pytest.fixture(scope='function')
def api():
    """Retuns API object."""
    time.sleep(60)
    return API(debug=True)
