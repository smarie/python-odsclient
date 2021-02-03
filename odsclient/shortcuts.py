import os
from glob import glob
from shutil import rmtree

try:
    # noinspection PyUnresolvedReferences
    from typing import Union
except ImportError:
    pass

try:
    from pathlib import Path
except ImportError:
    # do not care: only used for type hinting
    pass

from requests import Session

from odsclient.core import KR_DEFAULT_USERNAME, ODSClient, CACHE_ROOT_FOLDER, baseurl_to_id_str, CacheEntry


def store_apikey_in_keyring(platform_id='public',                          # type: str
                            base_url=None,                                 # type: str
                            keyring_entries_username=KR_DEFAULT_USERNAME,  # type: str
                            apikey=None,                                   # type: str
                            ):
    """
    Convenience method to store a password in the OS keyring using `keyring` lib.
    It is equivalent to `ODSClient(...).store_apikey_in_keyring(apikey)`

    :param platform_id: the ods platform id to use. This id is used to construct the base URL based on the pattern
        https://<platform_id>.opendatasoft.com. Default is `'public'` which leads to the base url
        https://public.opendatasoft.com
    :param base_url: an explicit base url to use instead of the one generated from `platform_id`
    :param keyring_entries_username: keyring stores secrets with a key made of a service id and a username. We use
        the base url for the service id, however the user name can be anything. By default we use a string:
        'apikey_user'.
    :param apikey: an explicit apikey string. If not provided, `getpass()` will be used to prompt the user for the
            api key
    :return:
    """
    client = ODSClient(platform_id=platform_id, base_url=base_url, keyring_entries_username=keyring_entries_username)
    client.store_apikey_in_keyring(apikey=apikey)


def get_apikey_from_keyring(platform_id='public',                          # type: str
                            base_url=None,                                 # type: str
                            keyring_entries_username=KR_DEFAULT_USERNAME,  # type: str
                            ):
    """
    Convenience method to get a previously stored password in the OS keyring using `keyring` lib.
    It is equivalent to `ODSClient(...).get_apikey_from_keyring()`

    :return:
    """
    client = ODSClient(platform_id=platform_id, base_url=base_url, keyring_entries_username=keyring_entries_username)
    return client.get_apikey_from_keyring()


def remove_apikey_from_keyring(platform_id='public',                          # type: str
                               base_url=None,                                 # type: str
                               keyring_entries_username=KR_DEFAULT_USERNAME,  # type: str
                               ):
    """
    Convenience method to remove a previously stored password in the OS keyring using `keyring` lib.
    It is equivalent to `ODSClient(...).remove_apikey_from_keyring()`

    :param platform_id: the ods platform id to use. This id is used to construct the base URL based on the pattern
        https://<platform_id>.opendatasoft.com. Default is `'public'` which leads to the base url
        https://public.opendatasoft.com
    :param base_url: an explicit base url to use instead of the one generated from `platform_id`
    :param keyring_entries_username: keyring stores secrets with a key made of a service id and a username. We use
        the base url for the service id, however the user name can be anything. By default we use a string:
        'apikey_user'.
    :return:
    """
    client = ODSClient(platform_id=platform_id, base_url=base_url, keyring_entries_username=keyring_entries_username)
    client.remove_apikey_from_keyring()


def get_apikey(platform_id='public',                          # type: str
               base_url=None,                                 # type: str
               apikey_filepath='ods.apikey',                  # type: str
               use_keyring=True,                              # type: bool
               keyring_entries_username=KR_DEFAULT_USERNAME,  # type: str
               ):
    # type: (...) -> str
    """
    Convenience method to check what is the api key used by ods clients.
    It is equivalent to `ODSClient(...).get_apikey()`

    :param platform_id: the ods platform id to use. This id is used to construct the base URL based on the pattern
        https://<platform_id>.opendatasoft.com. Default is `'public'` which leads to the base url
        https://public.opendatasoft.com
    :param base_url: an explicit base url to use instead of the one generated from `platform_id`
    :param apikey_filepath: the path that should be used to look for api keys on the file system. Such files are
        optional, other (safer) methods exist to pass the api key, see documentation for details.
    :param use_keyring: an optional boolean specifying whether the `keyring` library should be used to lookup
        existing api keys. Keys should be stored as `keyring.set_password(<base_url>, 'apikey', <apikey>)` where
        `<base_url>` should not contain any trailing slash.
    :param keyring_entries_username: keyring stores secrets with a key made of a service id and a username. We use
        the base url for the service id, however the user name can be anything. By default we use a string:
        'apikey_user'.
    :return:
    """
    client = ODSClient(platform_id=platform_id, base_url=base_url, apikey_filepath=apikey_filepath,
                       use_keyring=use_keyring, keyring_entries_username=keyring_entries_username)
    return client.get_apikey()


def get_whole_dataframe(dataset_id,                                    # type: str
                        use_labels_for_header=True,                    # type: bool
                        tqdm=False,                                    # type: bool
                        block_size=1024,                               # type: int
                        file_cache=False,                              # type: bool
                        platform_id='public',                          # type: str
                        base_url=None,                                 # type: str
                        enforce_apikey=False,                          # type: bool
                        apikey=None,                                   # type: str
                        apikey_filepath='ods.apikey',                  # type: Union[str, Path]
                        use_keyring=True,                              # type: bool
                        keyring_entries_username=KR_DEFAULT_USERNAME,  # type: str
                        requests_session=None,                         # type: Session
                        **other_opts
                        ):
    """
    Shortcut method for ODSClient(...).get_whole_dataframe(...)
    Returns a dataset as a pandas dataframe. pandas must be installed.

    :param dataset_id:
    :param use_labels_for_header:
    :param tqdm: a boolean indicating if a progress bar using tqdm should be displayed. tqdm should be installed
    :param block_size: an int block size used in streaming mode when to_csv or tqdm is used
    :param platform_id: the ods platform id to use. This id is used to construct the base URL based on the pattern
        https://<platform_id>.opendatasoft.com. Default is `'public'` which leads to the base url
        https://public.opendatasoft.com
    :param base_url: an explicit base url to use instead of the one generated from `platform_id`
    :param enforce_apikey: an optional boolean indicating if an error should be raised if no apikey is found at all
        (not in the explicit argument, not in a file, environment variable, nor keyring) (default `False`)
    :param apikey: an explicit api key as a string.
    :param apikey_filepath: the path that should be used to look for api keys on the file system. Such files are
        optional, other (safer) methods exist to pass the api key, see documentation for details.
    :param use_keyring: an optional boolean  (default `True`) specifying whether the `keyring` library should be used
        to lookup existing api keys. Keys should be stored using `store_apikey_in_keyring()`.
    :param keyring_entries_username: keyring stores secrets with a key made of a service id and a username. We use
        the base url for the service id, however the user name can be anything. By default we use a string:
        'apikey_user'.
    :param requests_session:
    :param other_opts:
    :return:
    """
    client = ODSClient(platform_id=platform_id, base_url=base_url, enforce_apikey=enforce_apikey, apikey=apikey,
                       apikey_filepath=apikey_filepath, use_keyring=use_keyring,
                       keyring_entries_username=keyring_entries_username, requests_session=requests_session)
    return client.get_whole_dataframe(dataset_id=dataset_id, use_labels_for_header=use_labels_for_header,
                                      tqdm=tqdm, block_size=block_size, file_cache=file_cache, **other_opts)


def clean_cache(dataset_id=None,   # type: str
                # format='csv',    # type: str
                platform_id=None,  # type: str
                base_url=None,     # type: str
                cache_root=None    # type: Union[str, Path]
                ):
    """
    Cleans the file cache

    :param dataset_id:
    :param platform_id:
    :param base_url:
    :return:
    """
    if dataset_id is not None:
        # clean a specific dataset on a specific platform
        path_pattern = get_cached_dataset_entry(dataset_id, format="*", platform_id=platform_id, base_url=base_url,
                                                cache_root=cache_root)
        for cached_file in glob(str(path_pattern.file_path)):
            print("[odsclient] Removing cached dataset entry for %r: %r" % (dataset_id, cached_file))
            os.remove(cached_file)
    else:
        if cache_root is None:
            cache_root = CACHE_ROOT_FOLDER
        else:
            cache_root = str(cache_root)

        if platform_id is not None:
            p = platform_id
        elif base_url is not None:
            p = baseurl_to_id_str(base_url)
        else:
            p = None

        if p is None:
            # clean the whole cache
            print("[odsclient] Removing entire cache folder %r" % cache_root)
            rmtree(cache_root, ignore_errors=True)
        else:
            # clean an entire platform cache
            path_to_delete = "%s/%s/" % (cache_root, p)
            print("[odsclient] Removing cache for platform %r: folder %r" % (p, path_to_delete))
            rmtree(path_to_delete, ignore_errors=True)


def get_cached_dataset_entry(dataset_id,            # type: str
                             format='csv',          # type: str
                             platform_id='public',  # type: str
                             base_url=None,         # type: str
                             cache_root=None        # type: Union[str, Path]
                             ):
    # type: (...) -> CacheEntry
    """
    Shortcut method for ODSClient(...).get_cached_dataset_entry(...)

    :param dataset_id:
    :param format:
    :param platform_id:
    :param base_url:
    :param cache_root:
    :return:
    """
    client = ODSClient(platform_id=platform_id, base_url=base_url)
    return client.get_cached_dataset_entry(dataset_id=dataset_id, format=format, cache_root=cache_root)


# noinspection PyShadowingBuiltins
def get_whole_dataset(dataset_id,                                    # type: str
                      format='csv',                                  # type: str
                      timezone=None,                                 # type: str
                      use_labels_for_header=True,                    # type: bool
                      csv_separator=';',                             # type: str
                      tqdm=False,                                    # type: bool
                      to_path=None,                                  # type: Union[str, Path]
                      file_cache=False,                              # type: bool
                      block_size=1024,                               # type: int
                      platform_id='public',                          # type: str
                      base_url=None,                                 # type: str
                      enforce_apikey=False,                          # type: bool
                      apikey=None,                                   # type: str
                      apikey_filepath='ods.apikey',                  # type: Union[str, Path]
                      use_keyring=True,                              # type: bool
                      keyring_entries_username=KR_DEFAULT_USERNAME,  # type: str
                      requests_session=None,                         # type: Session
                      **other_opts
                      ):
    """
    Shortcut method for ODSClient(...).get_whole_dataset(...)

    :param dataset_id:
    :param format:
    :param timezone:
    :param use_labels_for_header:
    :param csv_separator:
    :param tqdm: a boolean indicating if a progress bar using tqdm should be displayed. tqdm should be installed
    :param to_path: a string indicating the file path where to write the dataset (csv or other format). In that case
        nothing is returned
    :param file_cache: a boolean (default False) indicating whether the file should be written to a local cache
        `.odsclient/<pseudo_platform_id>_<dataset_id>.<format>`. See `get_cached_datasset_entry` for details.
    :param block_size: an int block size used in streaming mode when to_csv or tqdm is used
    :param platform_id: the ods platform id to use. This id is used to construct the base URL based on the pattern
        https://<platform_id>.opendatasoft.com. Default is `'public'` which leads to the base url
        https://public.opendatasoft.com
    :param base_url: an explicit base url to use instead of the one generated from `platform_id`
    :param enforce_apikey: an optional boolean indicating if an error should be raised if no apikey is found at all
        (not in the explicit argument, not in a file, environment variable, nor keyring) (default `False`)
    :param apikey: an explicit api key as a string.
    :param apikey_filepath: the path that should be used to look for api keys on the file system. Such files are
        optional, other (safer) methods exist to pass the api key, see documentation for details.
    :param use_keyring: an optional boolean  (default `True`) specifying whether the `keyring` library should be used
        to lookup existing api keys. Keys should be stored using `store_apikey_in_keyring()`.
    :param keyring_entries_username: keyring stores secrets with a key made of a service id and a username. We use
        the base url for the service id, however the user name can be anything. By default we use a string:
        'apikey_user'.
    :param requests_session: an optional `Session` object to use (from `requests` lib)
    :param other_opts:
    :return:
    """
    client = ODSClient(platform_id=platform_id, base_url=base_url, enforce_apikey=enforce_apikey, apikey=apikey,
                       apikey_filepath=apikey_filepath, use_keyring=use_keyring,
                       keyring_entries_username=keyring_entries_username, requests_session=requests_session)
    return client.get_whole_dataset(dataset_id=dataset_id, format=format, file_cache=file_cache,
                                    timezone=timezone, use_labels_for_header=use_labels_for_header,
                                    csv_separator=csv_separator, tqdm=tqdm, to_path=to_path, block_size=block_size,
                                    **other_opts)


def push_dataset_realtime(platform_id,        # type: str
                          dataset_id,         # type: str
                          dataset,            # type: Union[str, pandas.DataFrame]
                          push_key,           # type: str
                          format='csv',       # type: str
                          csv_separator=';',  # type: str
                          **other_opts
                          ):
    """
    Pushes a Dataset. This functions accepts either a Pandas Dataframe or a CSV string with header included.

    :param platform_id: the ods platform id to use. This id is used to construct the base URL based on the pattern
        https://<platform_id>.opendatasoft.com. Default is `'public'` which leads to the base url
        https://public.opendatasoft.com
    :param dataset_id:
    :param dataset: The dataset to push as a list of dicts, where the dict keys are the column names
    :param push_key: The Push Key provided by the API for pushing this dataset. Warning: This key is independent
                     from the API key. It can be acquired from the Realtime Push API URL section in ODS.
    :param format: The format of the dataset to be pushed. Can be `pandas` or `csv`.
    :param csv_separator: CSV separator character in case of a csv dataset input.
    :returns: HTTP Response status
    """

    client = ODSClient(platform_id=platform_id)
    return client.push_dataset_realtime(dataset_id=dataset_id,
                                        dataset=dataset,
                                        push_key=push_key,
                                        format=format,
                                        csv_separator=csv_separator,
                                        **other_opts)
