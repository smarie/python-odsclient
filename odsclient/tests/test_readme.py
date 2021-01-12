# coding: utf-8
from __future__ import print_function

import os
import pytest
import pandas as pd
import keyring

from .ref_datasets import ref_dataset_public_platform, create_reading_buffer, ref_dataset_other_platform

from odsclient import get_whole_dataset, get_whole_dataframe, store_apikey_in_keyring, \
    remove_apikey_from_keyring, get_apikey


@pytest.mark.parametrize("save_to_file", [False, True], ids="save_to_file={}".format)
@pytest.mark.parametrize("progress_bar", [False, True], ids="progress_bar={}".format)
def test_example(save_to_file, progress_bar, tmp_path):
    """basic test: retrieve an example dataset """

    dataset_id, ref_csv, ref_df, ref_shape = ref_dataset_public_platform()

    # with debug_requests():
    to_path = tmp_path / "tmp.csv" if save_to_file else None
    csv_str = get_whole_dataset(dataset_id,
                                platform_id='public', to_path=to_path, tqdm=progress_bar)
#     csv_str = csv_str.replace('\r\n', '\n').replace('\r', '\n')
    if save_to_file:
        assert csv_str is None
        csv_str = to_path.read_text(encoding="utf-8")
        os.remove(str(to_path))

    # for debug
    # if sys.version_info < (3, 0):
    #     print(csv_str.encode("utf-8"))  # note: we encode ourselves so that the ascii terminal on travis works.
    # else:
    #     print(csv_str)

    # this does not work as returned order may change
    # assert csv_str == ref_csv

    # move to pandas
    df = pd.read_csv(create_reading_buffer(csv_str, is_literal=False), sep=';')

    # compare with ref
    # df = df.set_index(['Transport', 'Année']).sort_index()
    pd.testing.assert_frame_equal(df, ref_df)
    assert df.shape == ref_shape

    # test the pandas direct streaming API
    df2 = get_whole_dataframe(dataset_id)
    # df2 = df2.set_index(['Transport', 'Année']).sort_index()
    pd.testing.assert_frame_equal(df, df2)


@pytest.mark.parametrize("apikey_method", ['direct', 'file_default', 'file_custom',
                                           # 'multi_env_pfid', not available on this ODS target
                                           'single_env', 'multi_env_baseurl', 'multi_env_default',
                                           'keyring1', 'keyring2'])
def test_other_platform(apikey_method):
    """Tests that the lib can connect to a different ODS platform with api key and custom url"""

    base_url, dataset_id, ref_csv, ref_df, ref_shape = ref_dataset_other_platform()

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

    # move to pandas
    df = pd.read_csv(create_reading_buffer(csv_str, is_literal=False), sep=';')

    # compare with ref
    df = df.set_index(['Transport', 'Année']).sort_index()
    pd.testing.assert_frame_equal(df, ref_df)
    assert df.shape == ref_shape
