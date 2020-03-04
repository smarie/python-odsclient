# Changelog

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
