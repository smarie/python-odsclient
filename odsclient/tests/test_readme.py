from __future__ import print_function

import os

import pytest
import sys
import pandas as pd
import keyring

from io import BytesIO   # to handle byte strings
from io import StringIO  # to handle unicode strings

if sys.version_info >= (3, 0):
    def create_reading_buffer(value, is_literal):
        return StringIO(value)
else:
    def create_reading_buffer(value, is_literal):
        if is_literal:
            return BytesIO(value)
        else:
            return StringIO(value)

from odsclient import get_whole_dataset, get_whole_dataframe, store_apikey_in_keyring, \
    remove_apikey_from_keyring, get_apikey


def test_example():
    """basic test: retrieve an example dataset """

    # with debug_requests():
    csv_str = get_whole_dataset("world-growth-since-the-industrial-revolution0",
                                platform_id='public')
#     csv_str = csv_str.replace('\r\n', '\n').replace('\r', '\n')
    print(csv_str)

    ref_csv = """Year Ending;World output;World population;Per capita output
2012-12-31;3.03783837;1.39292748;1.62231324
1700-12-31;0.07352168;0.05783974;0.01567288
1820-12-31;0.51654477;0.44594248;0.07028884
1913-12-31;1.48929571;0.58556427;0.89847031
"""
    # this does not work as returned order may change
    # assert csv_str == ref_csv

    # move to pandas
    df = pd.read_csv(create_reading_buffer(csv_str, is_literal=False), sep=';')

    # compare with ref
    ref_df = pd.read_csv(create_reading_buffer(ref_csv, is_literal=True), sep=';')
    df = df.set_index('Year Ending').sort_index()
    ref_df = ref_df.set_index('Year Ending').sort_index()
    pd.testing.assert_frame_equal(df, ref_df)
    assert df.shape == (4, 3)

    # test the pandas direct streaming API
    df2 = get_whole_dataframe("world-growth-since-the-industrial-revolution0")
    df2 = df2.set_index('Year Ending').sort_index()
    pd.testing.assert_frame_equal(df, df2)


@pytest.mark.parametrize("apikey_method", ['direct', 'file_default', 'file_custom',
                                           # 'multi_env_pfid', not available on this ODS target
                                           'single_env', 'multi_env_baseurl', 'multi_env_default',
                                           'keyring1', 'keyring2'])
def test_other_platform(apikey_method):
    """Tests that the lib can connect to a different ODS platform with api key and custom url"""

    # shared info
    dataset_id = "employment-by-sector-in-france-and-the-united-states-1800-2012"
    base_url = "https://data.exchange.se.com/"
    test_apikey = os.environ['EXCH_AKEY']  # <-- travis

    # various methods to get the api key
    if apikey_method == 'direct':
        csv_str = get_whole_dataset(dataset_id=dataset_id, base_url=base_url, apikey=test_apikey)

    elif apikey_method == 'file_default':
        f_name = 'ods.apikey'
        assert not os.path.exists(f_name)
        with open(f_name, 'w+') as f:
            f.write(test_apikey)

        assert get_apikey(base_url=base_url) == test_apikey
        try:
            csv_str = get_whole_dataset(dataset_id=dataset_id, base_url=base_url)
        finally:
            os.remove(f_name)

    elif apikey_method == 'file_custom':
        f_name = 'tmp.tmp'
        assert not os.path.exists(f_name), "File '%s' already exists, please delete it first" % f_name
        with open(f_name, 'w+') as f:
            f.write(test_apikey)
        assert get_apikey(base_url=base_url, apikey_filepath=f_name) == test_apikey
        try:
            csv_str = get_whole_dataset(dataset_id=dataset_id, base_url=base_url, apikey_filepath=f_name)
        finally:
            os.remove(f_name)

    elif apikey_method == 'single_env':
        os.environ['ODS_APIKEY'] = test_apikey
        assert get_apikey(base_url=base_url) == test_apikey
        csv_str = get_whole_dataset(dataset_id=dataset_id, base_url=base_url)
        del os.environ['ODS_APIKEY']

    elif apikey_method == 'multi_env_baseurl':
        os.environ['ODS_APIKEY'] = "{'default': 'blah', '%s': '%s'}" % (base_url, test_apikey)
        assert get_apikey(base_url=base_url) == test_apikey
        csv_str = get_whole_dataset(dataset_id=dataset_id, base_url=base_url)
        del os.environ['ODS_APIKEY']

    elif apikey_method == 'multi_env_default':
        os.environ['ODS_APIKEY'] = "{'default': '%s', 'other_id': 'blah'}" % (test_apikey)
        assert get_apikey(base_url=base_url) == test_apikey
        csv_str = get_whole_dataset(dataset_id=dataset_id, base_url=base_url)
        del os.environ['ODS_APIKEY']

    elif apikey_method == 'keyring1':
        # if 'TRAVIS_PYTHON_VERSION' in os.environ:
        #     pytest.skip("Does not work yet on travis")
        keyring.set_password(base_url, 'apikey', test_apikey)
        assert get_apikey(base_url=base_url, keyring_entries_username='apikey') == test_apikey
        csv_str = get_whole_dataset(dataset_id=dataset_id, base_url=base_url, keyring_entries_username='apikey')
        keyring.delete_password(base_url, 'apikey')
        assert keyring.get_password(base_url, 'apikey') is None

    elif apikey_method == 'keyring2':
        # if 'TRAVIS_PYTHON_VERSION' in os.environ:
        #     pytest.skip("Does not work yet on travis")
        store_apikey_in_keyring(base_url=base_url, keyring_entries_username='apikey', apikey=test_apikey)
        assert get_apikey(base_url=base_url, keyring_entries_username='apikey') == test_apikey
        csv_str = get_whole_dataset(dataset_id=dataset_id, base_url=base_url, keyring_entries_username='apikey')
        remove_apikey_from_keyring(base_url=base_url, keyring_entries_username='apikey')
        assert keyring.get_password(base_url, 'apikey') is None
        
    else:
        raise ValueError('wrong apikey_method: %s' % apikey_method)

    ref_csv = """Year;France: Agriculture;France: Manufacturing;France: Services;USA: Agriculture;USA: Manufacturing;USA: Services
1950-12-31;31.5;33.3;35.2;13.5;33.2;50.3
1800-12-31;64.03737;21.58231;14.38032;68.42105;18.42105;13.15789
2012-12-31;2.9;20.9;76.2;1.6;18.3;80.1
1900-12-31;43.2;29.0;27.8;40.5;28.2;31.3
"""

    # move to pandas
    df = pd.read_csv(create_reading_buffer(csv_str, is_literal=False), sep=';')

    # compare with ref
    ref_df = pd.read_csv(create_reading_buffer(ref_csv, is_literal=True), sep=';')
    df = df.set_index('Year').sort_index()
    ref_df = ref_df.set_index('Year').sort_index()
    pd.testing.assert_frame_equal(df, ref_df)
    assert df.shape == (4, 6)
