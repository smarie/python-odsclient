# Changelog

### 0.2.0 - datasets as pandas dataframes + misc.

New method `get_whole_dataframe` to directly retrieve a dataset as a pandas dataframe. It works in streaming mode so as to correctly handle large datasets. Fixes [#1](https://github.com/smarie/python-odsclient/issues/1) 

Added `csv_separator` option to `get_whole_dataset` methods. Set default value of `use_labels_for_header` to `True` to mimic what is available in the ODS website.

Now parsing the ODS errors correctly to raise `ODSException`. Fixes [#2](https://github.com/smarie/python-odsclient/issues/2) 

### 0.1.0 - First public version

Extracted from internal sources. Ability to download a whole dataset from any of the ODS platform using the "download flat dataset" API.
