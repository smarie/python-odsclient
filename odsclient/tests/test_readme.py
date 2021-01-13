# coding: utf-8
from __future__ import print_function

import os
import sys

import pytest
import pandas as pd
import keyring
from requests import Session
from requests.exceptions import ProxyError

try:
    from pathlib import Path
except ImportError:
    from pathlib2 import Path  # python 2

if sys.version_info < (3,):
    # We need a version of open that supports encoding and nline endings
    # See https://stackoverflow.com/a/10975371/7262247
    from io import open

from .ref_datasets import ref_dataset_public_platform, create_reading_buffer, ref_dataset_other_platform

from odsclient import get_whole_dataset, get_whole_dataframe, store_apikey_in_keyring, \
    remove_apikey_from_keyring, get_apikey, clean_cache, get_cached_dataset_entry


DEFAULT_CACHE_ROOT = ".odsclient"
clean_cache()

ALT_CACHE_ROOT = ".odscustcache"
clean_cache(cache_root=ALT_CACHE_ROOT)


def test_invalid_network_connection():
    """Tests that the make_invalid_network_session helper function works as expected"""
    with pytest.raises(ProxyError):
        get_whole_dataset(dataset_id="fake", requests_session=make_invalid_network_session())


@pytest.mark.parametrize("save_to_file", [False, True], ids="save_to_file={}".format)
@pytest.mark.parametrize("progress_bar", [False, True], ids="progress_bar={}".format)
@pytest.mark.parametrize("file_cache", [False, True, ALT_CACHE_ROOT], ids="file_cache={}".format)
def test_example(save_to_file, progress_bar, tmp_path, file_cache):
    """basic test: retrieve an example dataset """

    # get the reference dataset
    dataset_id, ref_csv, ref_df, ref_shape = ref_dataset_public_platform()

    # check the cache status
    cached_entry = None
    if file_cache:
        cache_root = DEFAULT_CACHE_ROOT if file_cache is True else file_cache
        cached_entry = get_cached_dataset_entry(dataset_id=dataset_id, platform_id="public",
                                                cache_root=None if file_cache is True else cache_root)
        assert cached_entry.file_path.as_posix() == "%s/public/%s.csv" % (cache_root, dataset_id)
        # the cache is supposed to be clean (cleaned at the end of this test)
        assert not cached_entry.exists()

    # with debug_requests():
    to_path = tmp_path / "blah" / "tmp.csv" if save_to_file else None
    csv_str = get_whole_dataset(dataset_id, platform_id='public', file_cache=file_cache, to_path=to_path,
                                tqdm=progress_bar)

    if save_to_file:
        assert csv_str is None
        # note: newline='' preserves line ending while opening. See https://stackoverflow.com/a/50996542/7262247
        with open(str(to_path), mode="rt", encoding="utf-8", newline='') as f:
            csv_str = f.read()
        os.remove(str(to_path))

    # compare the text string (if order does not change across queries...)
    # assert csv_str == ref_csv

    # move to pandas
    df = pd.read_csv(create_reading_buffer(csv_str, is_literal=False), sep=';')

    # compare with ref
    df = df.set_index(['Catégorie', 'Objectif ou Réalisation', 'Annee']).sort_index()
    pd.testing.assert_frame_equal(df, ref_df)
    assert df.shape == ref_shape

    # test the pandas direct streaming API without cache
    df2 = get_whole_dataframe(dataset_id, tqdm=progress_bar)
    df2 = df2.set_index(['Catégorie', 'Objectif ou Réalisation', 'Annee']).sort_index()
    pd.testing.assert_frame_equal(df, df2)

    # make sure the cached entry exists now and can be read without internet connection
    if cached_entry:
        # Make sure that the cache entry contains the dataset
        assert cached_entry.exists()
        # note: newline='' preserves line ending while opening. See https://stackoverflow.com/a/50996542/7262247
        with open(str(cached_entry.file_path), mode="rt", encoding="utf-8", newline='') as f:
            cached_csv_str = f.read()
        assert cached_csv_str == csv_str

        # New offline query: the cache should be hit even if the public platform is identified using its base_url here
        csv_str2 = get_whole_dataset(dataset_id=dataset_id, file_cache=file_cache,
                                     base_url="https://public.opendatasoft.com", tqdm=progress_bar,
                                     requests_session=make_invalid_network_session())
        assert csv_str2 == cached_csv_str

        # Same with the other method
        df3 = get_whole_dataframe(dataset_id, file_cache=file_cache, requests_session=make_invalid_network_session(),
                                  tqdm=progress_bar)
        df3 = df3.set_index(['Catégorie', 'Objectif ou Réalisation', 'Annee']).sort_index()
        pd.testing.assert_frame_equal(df, df3)

        # clean it for next time
        cached_entry.delete()
        assert not cached_entry.exists()

        # Make sure it is re-cached if we use the dataframe-getter method directly
        df4 = get_whole_dataframe(dataset_id, file_cache=file_cache, tqdm=progress_bar)
        df4 = df4.set_index(['Catégorie', 'Objectif ou Réalisation', 'Annee']).sort_index()
        assert cached_entry.exists()
        pd.testing.assert_frame_equal(df, df4)

        # clean it for next time
        cached_entry.delete()
        assert not cached_entry.exists()


apikey_methods = ['direct', 'file_default', 'file_custom',
                  # 'multi_env_pfid', not available on this ODS target
                  'single_env', 'multi_env_baseurl', 'multi_env_default',
                  'keyring1', 'keyring2']


@pytest.mark.parametrize("apikey_method", apikey_methods)
@pytest.mark.parametrize("file_cache", [False, True, ALT_CACHE_ROOT], ids="file_cache={}".format)
def test_other_platform(apikey_method, file_cache):
    """Tests that the lib can connect to a different ODS platform with api key and custom url"""

    # get the reference dataset
    base_url, dataset_id, ref_csv, ref_df, ref_shape = ref_dataset_other_platform()

    test_apikey = os.environ['EXCH_AKEY']  # <-- travis

    # check the cache status
    cached_entry = None
    if file_cache:
        cache_root = DEFAULT_CACHE_ROOT if file_cache is True else file_cache
        cached_entry = get_cached_dataset_entry(dataset_id=dataset_id, base_url=base_url,
                                                cache_root=None if file_cache is True else cache_root)
        assert cached_entry.file_path.as_posix() == "%s/uat-data.exchange.se.com/%s.csv" % (cache_root, dataset_id)
        # the cache is supposed to be clean (cleaned at the end of this test)
        assert not cached_entry.exists()

    # various methods to get the api key
    if apikey_method == 'direct':
        csv_str = get_whole_dataset(dataset_id=dataset_id, file_cache=file_cache, base_url=base_url, apikey=test_apikey)

    elif apikey_method == 'file_default':
        f_name = 'ods.apikey'
        assert not os.path.exists(f_name), "File '%s' already exists, please delete it first" % f_name
        with open(f_name, 'wb') as f:
            f.write(test_apikey.encode("utf-8"))

        assert get_apikey(base_url=base_url) == test_apikey
        try:
            csv_str = get_whole_dataset(dataset_id=dataset_id, file_cache=file_cache, base_url=base_url)
        finally:
            os.remove(f_name)

    elif apikey_method == 'file_custom':
        f_name = 'tmp.tmp'
        assert not os.path.exists(f_name), "File '%s' already exists, please delete it first" % f_name
        with open(f_name, 'wb') as f:
            f.write(test_apikey.encode("utf-8"))
        assert get_apikey(base_url=base_url, apikey_filepath=f_name) == test_apikey
        try:
            csv_str = get_whole_dataset(dataset_id=dataset_id, file_cache=file_cache, base_url=base_url,
                                        apikey_filepath=f_name)
        finally:
            os.remove(f_name)

    elif apikey_method == 'single_env':
        os.environ['ODS_APIKEY'] = test_apikey
        assert get_apikey(base_url=base_url) == test_apikey
        csv_str = get_whole_dataset(dataset_id=dataset_id, file_cache=file_cache, base_url=base_url)
        del os.environ['ODS_APIKEY']

    elif apikey_method == 'multi_env_baseurl':
        os.environ['ODS_APIKEY'] = "{'default': 'blah', '%s': '%s'}" % (base_url, test_apikey)
        assert get_apikey(base_url=base_url) == test_apikey
        csv_str = get_whole_dataset(dataset_id=dataset_id, file_cache=file_cache, base_url=base_url)
        del os.environ['ODS_APIKEY']

    elif apikey_method == 'multi_env_default':
        os.environ['ODS_APIKEY'] = "{'default': '%s', 'other_id': 'blah'}" % (test_apikey)
        assert get_apikey(base_url=base_url) == test_apikey
        csv_str = get_whole_dataset(dataset_id=dataset_id, file_cache=file_cache, base_url=base_url)
        del os.environ['ODS_APIKEY']

    elif apikey_method == 'keyring1':
        # if 'TRAVIS_PYTHON_VERSION' in os.environ:
        #     pytest.skip("Does not work yet on travis")
        keyring.set_password(base_url, 'apikey', test_apikey)
        assert get_apikey(base_url=base_url, keyring_entries_username='apikey') == test_apikey
        csv_str = get_whole_dataset(dataset_id=dataset_id, base_url=base_url, file_cache=file_cache,
                                    keyring_entries_username='apikey')
        keyring.delete_password(base_url, 'apikey')
        assert keyring.get_password(base_url, 'apikey') is None

    elif apikey_method == 'keyring2':
        # if 'TRAVIS_PYTHON_VERSION' in os.environ:
        #     pytest.skip("Does not work yet on travis")
        store_apikey_in_keyring(base_url=base_url, keyring_entries_username='apikey', apikey=test_apikey)
        assert get_apikey(base_url=base_url, keyring_entries_username='apikey') == test_apikey
        csv_str = get_whole_dataset(dataset_id=dataset_id, file_cache=file_cache, base_url=base_url,
                                    keyring_entries_username='apikey')
        remove_apikey_from_keyring(base_url=base_url, keyring_entries_username='apikey')
        assert keyring.get_password(base_url, 'apikey') is None
        
    else:
        raise ValueError('wrong apikey_method: %s' % apikey_method)

    # do not compare csv_str to ref_csv as order may change
    # assert csv_str == ref_csv

    # move to pandas
    df = pd.read_csv(create_reading_buffer(csv_str, is_literal=False), sep=';')

    # compare with ref
    df = df.set_index(['Transport', 'Année']).sort_index()
    pd.testing.assert_frame_equal(df, ref_df)
    assert df.shape == ref_shape

    # make sure the cached entry exists now and can be read without network connection
    if cached_entry:
        # make sure that the cache entry contains the dataset
        assert cached_entry.read() == csv_str

        # perform a second query offline and make sure the cache is hit
        csv_str2 = get_whole_dataset(dataset_id=dataset_id, file_cache=file_cache, base_url=base_url,
                                     requests_session=make_invalid_network_session())
        assert csv_str2 == csv_str

        # clean it for the next time
        # cached_entry.delete()
        clean_cache(dataset_id=dataset_id, base_url=base_url, cache_root=None if file_cache is True else cache_root)


def make_invalid_network_session():
    """Returns a session with an invalid proxy"""
    offline_session = Session()
    offline_session.proxies = {
        "http": "http://localhost:44445",
        "https": "http://localhost:44445"
    }
    offline_session.trust_env = False
    return offline_session
