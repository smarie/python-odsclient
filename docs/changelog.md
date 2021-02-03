# Changelog

### 0.8.1 - `file_cache` on `get_whole_dataframe`

 - `file_cache` is now available on package-level `get_whole_dataframe`. Fixes [#24](https://github.com/smarie/python-odsclient/issues/24)

### 0.8.0 - New cache feature

 - New cache functionality: a `file_cache` argument is available on most methods. The cache is by default located under `.odsclient/` and contains `utf-8`-encoded versions of the dataset files. New util methods `clean_cache` and `get_cached_dataset_entry`. Fixes [#20](https://github.com/smarie/python-odsclient/issues/20)

### 0.7.0 - New streaming-related features

 - You can now display a progress bar using `tqdm=True`. Note that this requires the `tqdm` package to be installed, and since some ODS platforms do not return the `Content-Length` HTTP header, only the size and download rate might be displayed. Fixed [#9](https://github.com/smarie/python-odsclient/issues/9)
 - You can now stream a dataset directly to a file using `to_path`. Fixed [#9](https://github.com/smarie/python-odsclient/issues/9)
 - `apikey_filepath` can now be a `pathlib.Path`.

### 0.6.0 - New feature: push dataset

 - New `push_dataset_realtime` client method and shortcut, to push a CSV string or a `pandas` dataframe to an ODS server through the Realtime API. PR [#21](https://github.com/smarie/python-odsclient/pull/21) by [`@zoltanctoth`](https://github.com/zoltanctoth), thanks !

### 0.5.1 - better packaging

 - packaging improvements: set the "universal wheel" flag to 1, and cleaned up the `setup.py`. In particular removed dependency to `six` for setup and added `py.typed` file. Removed tests folder from package. Fixes [#19](https://github.com/smarie/python-odsclient/issues/19)

### 0.5.0 - odskeys improvements

 - New `odskeys show` command to open the OS GUI for keyring management. Fixed [#18](https://github.com/smarie/python-odsclient/issues/18)
 - `odskeys get/set/remove` now always print the complete url used for the keyring entry. Fixes [#17](https://github.com/smarie/python-odsclient/issues/17)
 - Improved documentation about api keys management. Fixed [#15](https://github.com/smarie/python-odsclient/issues/15)

### 0.4.0 - odskeys commandline

 - New `odskeys` commandline utility to ease registration of api keys in `keyring`. Fixes [#16](https://github.com/smarie/python-odsclient/issues/16). Added a dedicated documentation page.
 - Documentation improvements, in particular concerning api key registration.
 - Filled the API reference documentation section

### 0.3.0 -  api keys

**API Keys:**

 - New documentation section on api keys. Fixes [#11](https://github.com/smarie/python-odsclient/issues/11)
 - New methods `get_apikey()` and `<ODSClient>.get_apikey()` for debugging purposes
 - API keys can now be provided through OS Environment Variables. Fixes [#6](https://github.com/smarie/python-odsclient/issues/6). New method `<ODSClient>.get_apikey_from_envvar()` for debugging.
 - API keys can now be provided through `keyring`. Fixes [#8](https://github.com/smarie/python-odsclient/issues/8)
 - API key files: `apikeyfile_path` argument renamed `apikey_filepath`. Now tolerating new lines or blanks at the end of api key files. Fixes [#12](https://github.com/smarie/python-odsclient/issues/12). `apikey_filepath` now has a default value `'ods.apikey'` and file check is now optional. Fixes [#13](https://github.com/smarie/python-odsclient/issues/13)
 - Now correctly raising an error (`InsufficientRightsForODSResourceError`) when rights are not sufficient for a resource. Fixed [#7](https://github.com/smarie/python-odsclient/issues/7).
 - `enforce_apikey` controls if an api key is mandatory before calling (whatever way it is provided: explicit, file, env variable, or keyring). A `NoODSAPIKeyFoundError` is raised in case none is found.

**Misc:**

 - Added documentation on target platform customization. Fixes [#14](https://github.com/smarie/python-odsclient/issues/14)
 - Now tolerating trailing slashs at the end of custom `base_url` (they are removed automatically).
 - Init: now exposing `ODSClient` and `ODSException` at the root package level.
 - new method `get_apikey()` on `ODSClient`

### 0.2.0 - datasets as pandas dataframes + misc.

New method `get_whole_dataframe` to directly retrieve a dataset as a pandas dataframe. It works in streaming mode so as to correctly handle large datasets. Fixes [#1](https://github.com/smarie/python-odsclient/issues/1) 

Added `csv_separator` option to `get_whole_dataset` methods. Set default value of `use_labels_for_header` to `True` to mimic what is available in the ODS website.

Now parsing the ODS errors correctly to raise `ODSException`. Fixes [#2](https://github.com/smarie/python-odsclient/issues/2) 

### 0.1.0 - First public version

Extracted from internal sources. Ability to download a whole dataset from any of the ODS platform using the "download flat dataset" API.
