"""Pytest configuration file."""
import pytest

from fileio import API


@pytest.fixture(scope='session')
def api():
    """Retuns API object."""
    return API(debug=True)
