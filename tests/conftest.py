"""Pytest configuration file."""
import pytest

from fileio import API


@pytest.fixture(scope='function')
def api():
    """Retuns API object."""
    return API(debug=True)
