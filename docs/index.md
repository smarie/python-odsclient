# odsclient

*A nonofficial client for OpenDataSoft API.*

[![Python versions](https://img.shields.io/pypi/pyversions/odsclient.svg)](https://pypi.python.org/pypi/odsclient/) [![Build Status](https://travis-ci.org/smarie/python-odsclient.svg?branch=master)](https://travis-ci.org/smarie/python-odsclient) [![Tests Status](https://smarie.github.io/python-odsclient/junit/junit-badge.svg?dummy=8484744)](https://smarie.github.io/python-odsclient/junit/report.html) [![codecov](https://codecov.io/gh/smarie/python-odsclient/branch/master/graph/badge.svg)](https://codecov.io/gh/smarie/python-odsclient)

[![Documentation](https://img.shields.io/badge/doc-latest-blue.svg)](https://smarie.github.io/python-odsclient/) [![PyPI](https://img.shields.io/pypi/v/odsclient.svg)](https://pypi.python.org/pypi/odsclient/) [![Downloads](https://pepy.tech/badge/odsclient)](https://pepy.tech/project/odsclient) [![Downloads per week](https://pepy.tech/badge/odsclient/week)](https://pepy.tech/project/odsclient) [![GitHub stars](https://img.shields.io/github/stars/smarie/python-odsclient.svg)](https://github.com/smarie/python-odsclient/stargazers)

`odsclient` provides a minimal set of functions to grab a dataset or a collection of datasets from an OpenDataSoft (ODS) platform. 

Its initial purpose is not to cover the [full set of APIs available](https://help.opendatasoft.com/en/apis/) but to get a minimum viable set of features to work easily with the datasets.

## Installing

```bash
> pip install odsclient
```

If you wish to download datasets as dataframes, you should also install `pandas`. This is not mandatory, though.

Finally, if you plan to use api keys, we recommend that you install `keyring` as it will help you store the critical api keys in your operating system's password vault.

```bash
> pip install keyring
```

## Usage

### 1. Basics

#### a- Downloading a "flat" dataset

The most basic thing that you can do is to download a whole dataset, similarly to what you can get when clicking on the links with your browser on a dataset's ["Export" page](https://public.opendatasoft.com/explore/dataset/world-growth-since-the-industrial-revolution0/export/):

```python
from odsclient import get_whole_dataset

csv_str = get_whole_dataset("world-growth-since-the-industrial-revolution0", 
                            platform_id='public')
print(csv_str)
```

yields

```
Year Ending;World output;World population;Per capita output
2012-12-31;3.03783837;1.39292748;1.62231324
1700-12-31;0.07352168;0.05783974;0.01567288
1820-12-31;0.51654477;0.44594248;0.07028884
1913-12-31;1.48929571;0.58556427;0.89847031
```

If you have `pandas` installed, you can get the dataset directly as a dataframe:

```python
from odsclient import get_whole_dataframe

df = get_whole_dataframe("world-growth-since-the-industrial-revolution0", 
                         platform_id='public')
print(df)
```

yields

```
  Year Ending  World output  World population  Per capita output
0  1820-12-31      0.516545          0.445942           0.070289
1  1913-12-31      1.489296          0.585564           0.898470
2  2012-12-31      3.037838          1.392927           1.622313
3  1700-12-31      0.073522          0.057840           0.015673
```

#### b- Using another ODS platform

By default the base url used to access the OpenDataSoft platform is `https://<platform_id>.opendatasoft.com`, with `platform_id='public'`. In the methods above, you can change either the platform id with `platform_id=...` if your target ODS platform has a standard host name, or the entire base url with `base_url=...`.

If you wish to check the result without executing the method, you can create an `ODSClient` object with the same parameters and inspect its `<client>.base_url` :

```python
from odsclient import ODSClient

default_client = ODSClient()
print("Default:               %s" % default_client.base_url)

client_with_custom_pfid = ODSClient(platform_id='my_ods')
print("Custom `platform_id`:  %s" % client_with_custom_pfid.base_url)

client_with_custom_baseurl = ODSClient(base_url="https://my_ods_server.com/")
print("Custom `base_url`:     %s" % client_with_custom_baseurl.base_url)
```

yields

```
Default:               https://public.opendatasoft.com
Custom `platform_id`:  https://my_ods.opendatasoft.com
Custom `base_url`:     https://my_ods_server.com
```

Note that any trailing slash is automatically removed from custom base urls.

#### c- Declaring an API key

Most ODS servers require some sort of authentication to access some of their contents. `odsclient` supports authentication through API keys (see [ODS API Documentation](https://help.opendatasoft.com/en/apis/)). There are several ways that you can use to specify an api key to use for your ODS interactions.

##### explicit, temporary

If your need is a "quick and dirty" test, you can use direct `apikey=...` argument passing. This is the **most insecure** way of all, since your code will contain the key as a readable string. It should only be used as a temporary workaround, and should never be committed with the source code.
 
```python 
csv_str = get_whole_dataset("world-growth-since-the-industrial-revolution0", 
                            apikey="my_non_working_api_key")
```

##### interactive

If your application tolerates user interaction through the terminal, you can make the above more secure by using [`getpass()`](https://docs.python.org/3/library/getpass.html) so that users are prompted for the api key at runtime:
 
```python
from getpass import getpass
csv_str = get_whole_dataset("world-growth-since-the-industrial-revolution0", 
                            apikey=getpass())
```

##### permanent

In all other cases, we recommend that you write apikey-agnostic code such as the one below:

```python
csv_str = get_whole_dataset("world-growth-since-the-industrial-revolution0")
```

In that case, `odsclient` will try several strategies to find an api key:

 - first it will look for an `ods.apikey` text file containing the api key. The file should obviously not be committed with the source code (use `.gitignore` !). This is not the most secure solution, as malicious programs on your computer may have access to the file, and moreover you may commit it by accident (human error prone). You can override the default file path with the `apikey_filepath=...` argument.

 - then if `keyring` is installed (`pip install keyring`), it will check if there is an entry in it for service `<base_url>` and username `'apikey_user'`. `keyring` leverages your OS' vault ([Windows Credential Locker, macOS Keychain, Ubuntu SecretService, GNOME Keyring, etc.](https://keyring.readthedocs.io/en/latest/?badge=latest#what-is-python-keyring-lib)). **This is the most secure method available, it is therefore highly recommended**. You can override the default keyring entry username with the `keyring_entries_username=...` argument. You can easily add or remove an entry in the keyring with the [`odskeys` commandline utility](./odskey.md), through the OS interface, or with the `store_apikey_in_keyring` / `get_apikey_from_keyring` / `remove_apikey_from_keyring` python API provided in `odsclient`.
  
 - finally it looks for an `ODS_APIKEY` OS environment variable. This environment variable should either contain a single api key without quotes (e.g. `aef46reohln48`), or a dict-like structure where keys can either be `<platform_id>`, `<base_url>`, or the special fallback key `'default'` (e.g. `{'public': 'key2', 'https://myods.com': 'key3', 'default': 'key1'}`). This method is not the most secure solution because malicious programs can access the OS environment variables ; however it should be preferred over the file-based method as it is not human error-prone. Besides it can be handy for continuous integration jobs.

If you wish to **force** usage of an api key (and prevent any ODS query to be made if none is found), you may wish to set `enforce_apikey=True`:

```python
csv_str = get_whole_dataset("world-growth-since-the-industrial-revolution0",
                            enforce_apikey=True  # raise if no apikey is found
                            )
```

If no api key is found, the above yields:

```
odsclient.core.NoODSAPIKeyFoundError: ODS API key file not found, while it is 
    marked as mandatory for this call (`enforce_apikey=True`). It should either 
    be put in a text file at path 'ods.apikey', or in the `ODS_APIKEY` OS 
    environment variable, or (recommended, most secure) in the local `keyring`.
    See documentation for details: 
    https://smarie.github.io/python-odsclient/#c-declaring-an-api-key. 
    Note that you can generate an API key on this web page: [...].
```

This can be handy if you wish your users to see a quick help at first call reminding them on the various ways to provide an api key.

Finally, for debugging purposes, you may wish to use `get_apikey()` to check if the api key that is actually used is the one you think you have configured (through a file, env variable, or keyring):

```python
from odsclient import get_apikey
print("api key used: %s" % get_apikey(base_url="https://my_ods_server.com/"))
```

See [API reference](api_reference.md) for details.


### 2. Advanced

**TODO**

## Main features / benefits

 - Simple access to ODS API to retrive a whole dataset as text (csv) or dataframe
 - Support for many methods to define an api key, independently of the source code: different users may use different methods (env variable, api key file, keyring) while using the same odsclient code.

## See Also

This library was inspired by:

 * [`azmlclient`](https://smarie.github.io/python-azureml-client/)
 * [`keyring`](https://pypi.org/project/keyring/)
 * Work in progress: using KeePass as a `keyring` backend. [Here](https://github.com/brettviren/python-keepass) and [here](https://github.com/jaraco/keyring/issues/14)

### Others

*Do you like this library ? You might also like [my other python libraries](https://github.com/smarie/OVERVIEW#python)* 

## Want to contribute ?

Details on the github page: [https://github.com/smarie/python-odsclient](https://github.com/smarie/python-odsclient)
