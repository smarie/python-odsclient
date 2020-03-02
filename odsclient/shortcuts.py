from requests import Session

from odsclient.core import KR_DEFAULT_USERNAME, ODSClient


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
                        platform_id='public',                          # type: str
                        base_url=None,                                 # type: str
                        enforce_apikey=False,                          # type: bool
                        apikey=None,                                   # type: str
                        apikey_filepath='ods.apikey',                  # type: str
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
    return client.get_whole_dataframe(dataset_id=dataset_id, use_labels_for_header=use_labels_for_header, **other_opts)


# noinspection PyShadowingBuiltins
def get_whole_dataset(dataset_id,                                    # type: str
                      format='csv',                                  # type: str
                      timezone=None,                                 # type: str
                      use_labels_for_header=True,                    # type: bool
                      csv_separator=';',                             # type: str
                      platform_id='public',                          # type: str
                      base_url=None,                                 # type: str
                      enforce_apikey=False,                          # type: bool
                      apikey=None,                                   # type: str
                      apikey_filepath='ods.apikey',                  # type: str
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
    client = ODSClient(platform_id=platform_id, base_url=base_url,enforce_apikey=enforce_apikey, apikey=apikey,
                       apikey_filepath=apikey_filepath, use_keyring=use_keyring,
                       keyring_entries_username=keyring_entries_username, requests_session=requests_session)
    return client.get_whole_dataset(dataset_id=dataset_id, format=format,
                                    timezone=timezone, use_labels_for_header=use_labels_for_header,
                                    csv_separator=csv_separator, **other_opts)
