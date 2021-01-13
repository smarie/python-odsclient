# API reference

In general, `help(symbol)` will provide the latest up-to-date documentation.

## `ODSClient`

An `ODSClient` is a client for a given OpenDataSoft (ODS) platform. By default the target platform base url is
`https://<platform_id>.opendatasoft.com` with `platform_id='public'`. One can change either customize the platform
id through the `platform_id` constructor argument, or the whole base url with `base_url`.

A client instance offers methods to interact with the various ODS API. Currently three high-level methods are provided:
 * `<client>.get_whole_dataset(dataset_id, ...)`
 * `<client>.get_whole_dataframe(dataset_id, ...)`
 * `<client>.push_dataset_realtime(dataset_id, ...)`

A file cache can be activated for the two `get` methods by setting `file_cache` to `True` or to a path-like (string or `Path`) indicating a custom cache root path. `True` will use the default cache root folder `.odsclient`. `<client>.get_cached_dataset_entry` can be used to get a `CacheEntry` object representing the (possibly non-existing) cache entry for a given dataset.

You can customize the `requests.Session` object used for the HTTPS transport using `requests_session`.

A client is meant to use a single api key at a time, or none. You can force the api key to be mandatory using
`enforce_apikey=True`. There are 4 ways to pass an api key, they are used in the following order:

 - explicitly with the `apikey` argument

 - through a text file containing the key. This file if present should be named `ods.apikey` (name can be changed
   using `apikey_filepath`, it does not make the file mandatory)

 - if `keyring` is installed (`pip install keyring`), an apikey can be created as an entry in it for service
   `<base_url>` and username `'apikey_user'`. `keyring` leverages your OS' vault (Windows Credential Locker,
   macOS Keychain, etc. This is the **most secure** method available. You can override the default keyring entry
   username with the `keyring_entries_username=...` argument. You can easily add or remove an entry in the keyring
   through the OS interface, with the [`odskeys` commandline utility](odskey.md) or with the
   `<client>.store_apikey_in_keyring` / `<client>.get_apikey_from_keyring` / `<client>.remove_apikey_from_keyring`
   methods.

 - through the `'ODS_APIKEY'` OS environment variable. It should either contain the key without quotes or a
   dict-like structure where keys can either be `platform_id`, `base_url`, or the special fallback key `'default'`

For debugging purposes, you may wish to use `<client>.get_apikey()` to check if the api key that is actually used 
is the one you think you have configured through one of the above methods.

Keep in mind that when you push a dataset to ODS the push API doesn't use the API keys provided. Instead, it uses a dataset-specific
_pushkey_, which you can retrieve from the _Sources_ tab of the ODS data management page.

```python
ODSClient(
          platform_id='public',                          # type: str
          base_url=None,                                 # type: str
          enforce_apikey=False,                          # type: bool
          apikey=None,                                   # type: str
          apikey_filepath='ods.apikey',                  # type: Union[str, Path]
          use_keyring=True,                              # type: bool
          keyring_entries_username=KR_DEFAULT_USERNAME,  # type: str
          requests_session=None                          # type: Session
          ):
```

**Parameters**:

 * `platform_id`: the ods platform id to use. This id is used to construct the base URL based on the pattern
    https://<platform_id>.opendatasoft.com. Default is `'public'` which leads to the base url
    https://public.opendatasoft.com
 * `base_url`: an explicit base url to use instead of the one generated from `platform_id`
 * `enforce_apikey`: an optional boolean indicating if an error should be raised if no apikey is found at all
    (not in the explicit argument, not in a file, environment variable, nor keyring) (default `False`)
 * `apikey`: an explicit api key as a string.
 * `apikey_filepath`: the path that should be used to look for api keys on the file system. Such files are
    optional, other (safer) methods exist to pass the api key, see documentation for details.
 * `use_keyring`: an optional boolean (default `True`) specifying whether the `keyring` library should be
    used to lookup existing api keys. Keys should be stored using `store_apikey_in_keyring()`.
 * `keyring_entries_username`: keyring stores secrets with a key made of a service id and a username. We use
    the base url for the service id, however the user name can be anything. By default we use a string:
    'apikey_user'.
 * `requests_session`: an optional `Session` object to use (from `requests` lib)

## Shortcuts

The following shortcut functions provide the same level of functionality than `ODSClient(...).<function_name>(...)`. They can be handy if only one call to ODS is needed.

```python
from odsclient.shortcuts import (get_whole_dataset, 
                                 get_whole_dataframe, 
                                 get_apikey,
                                 store_apikey_in_keyring,
                                 get_apikey_from_keyring, 
                                 remove_apikey_from_keyring,
                                 push_dataset_realtime,
                                 get_cached_dataset_entry
)
```

### `clean_cache`

TODO

## `CacheEntry`

TODO
