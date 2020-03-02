import os

import pytest
import requests

from odsclient import get_whole_dataset, ODSException, NoODSAPIKeyFoundError, InsufficientRightsForODSResourceError


def test_error_bad_dataset_id():
    """Tests that an error associated with bad dataset id is correctly parsed and raised as an ODSException"""
    with pytest.raises(ODSException) as exc_info:
        get_whole_dataset("unknwn", platform_id='public')

    # see https://github.com/psf/requests/blob/master/requests/status_codes.py
    assert exc_info.value.status_code == requests.codes.NOT_FOUND  # not found
    assert exc_info.value.error_msg == "Unknown dataset: unknwn"


def test_no_apikey_provided():
    """Tests that enforce_apikey works correctly"""
    with pytest.raises(NoODSAPIKeyFoundError):
        get_whole_dataset("world-growth-since-the-industrial-revolution0", enforce_apikey=True)


def test_apikey_not_granting_rights():
    """Tests that if rights are not sufficient the proper error is raised"""
    with pytest.raises(InsufficientRightsForODSResourceError):
        get_whole_dataset("employment-by-sector-in-france-and-the-united-states-1800-2012",
                          base_url="https://data.exchange.se.com/")


def test_bad_apikey():
    """Tests that an error associated with bad api key is correctly parsed and raised as an ODSException"""
    with pytest.raises(ODSException) as exc_info:
        get_whole_dataset("world-growth-since-the-industrial-revolution0",
                          apikey="my_non_working_api_key")

    assert exc_info.value.status_code == requests.codes.UNAUTHORIZED  # not authorized
    assert exc_info.value.error_msg == "API key is not valid"


# @pytest.mark.skipif('TRAVIS_PYTHON_VERSION' in os.environ, reason="Does not work yet on travis")
def test_keyring_unit():
    """Small unit test for keyring"""
    import keyring
    print(keyring.get_keyring())
    base_url = "https://data.exchange.se.com/"
    keyring.set_password(base_url, 'apikey', 'blah')
    assert keyring.get_password(base_url, 'apikey') == 'blah'
