import warnings
from ast import literal_eval
from getpass import getpass
import io
import os
from shutil import copyfile
from threading import Lock

try:
    # Python 3
    from urllib.parse import urlparse, parse_qs
except ImportError:
    # Python 2
    from urlparse import urlparse, parse_qs

try:
    from pathlib import Path
except ImportError:
    from pathlib2 import Path  # python 2

import sys

if sys.version_info < (3,):
    # py2: we need a version of open that supports encoding and nline endings
    # See https://stackoverflow.com/a/10975371/7262247
    from io import open
    from StringIO import StringIO
    string_types = (str, bytes)
else:
    from io import StringIO
    string_types = (str,)

try:
    from json import loads, JSONDecodeError, dumps
except ImportError:
    # python 2
    from json import loads, dumps
    JSONDecodeError = ValueError
try:
    FileNotFoundError
except NameError:
    # python 2
    FileNotFoundError = IOError

from requests import Session, HTTPError

try:
    # python 3
    # noinspection PyCompatibility
    from urllib.parse import quote
except ImportError:
    # python 2
    # noinspection PyUnresolvedReferences
    from urllib import quote

try:
    # noinspection PyUnresolvedReferences
    from typing import Dict, Union, Iterable
except ImportError:
    pass

CACHE_ROOT_FOLDER = ".odsclient"
CACHE_ENCODING = "utf-8"
ODS_BASE_URL_TEMPLATE = "https://%s.opendatasoft.com"
ENV_ODS_APIKEY = 'ODS_APIKEY'
KR_DEFAULT_USERNAME = 'apikey_user'


class ODSClient(object):
    """
    An `ODSClient` is a client for a given OpenDataSoft (ODS) platform. By default the target platform base url is
    `https://<platform_id>.opendatasoft.com` with `platform_id='public'`. One can change either customize the platform
    id through the `platform_id` constructor argument, or the whole base url with `base_url`.

    A client instance offers methods to interact with the various ODS API. Currently three high-level methods are
    provided: `<client>.get_whole_dataset(dataset_id, ...)`, `<client>.get_whole_dataframe(dataset_id, ...)`
    and `<client>.push_dataset_realtime(dataset_id, ...)`.

    A file cache can be activated for the two `get` methods by setting `file_cache` to `True` or to a path-like (string
    or `Path`) indicating a custom cache root path. `True` will use the default cache root folder `.odsclient`.
    `<client>.get_cached_dataset_entry` can be used to get a `CacheEntry` object representing the (possibly
    non-existing) cache entry for a given dataset.

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
       through the OS interface, with the `odskeys` commandline utility (`odskeys --help`) or with the
       `<client>.store_apikey_in_keyring` / `<client>.get_apikey_from_keyring` / `<client>.remove_apikey_from_keyring`
       methods.

     - through the `'ODS_APIKEY'` OS environment variable. It should either contain the key without quotes or a
       dict-like structure where keys can either be `platform_id`, `base_url`, or the special fallback key `'default'`

    For debugging purposes, you may wish to use `<client>.get_apikey()` to check if the api key that is actually used
    is the one you think you have configured through one of the above methods.

    """

    def __init__(self,
                 platform_id='public',                          # type: str
                 base_url=None,                                 # type: str
                 enforce_apikey=False,                          # type: bool
                 apikey=None,                                   # type: str
                 apikey_filepath='ods.apikey',                  # type: Union[str, Path]
                 use_keyring=True,                              # type: bool
                 keyring_entries_username=KR_DEFAULT_USERNAME,  # type: str
                 requests_session=None                          # type: Session
                 ):
        """
        Constructor for `ODSClient`s

        :param platform_id: the ods platform id to use. This id is used to construct the base URL based on the pattern
            https://<platform_id>.opendatasoft.com. Default is `'public'` which leads to the base url
            https://public.opendatasoft.com
        :param base_url: an explicit base url to use instead of the one generated from `platform_id`
        :param enforce_apikey: an optional boolean indicating if an error should be raised if no apikey is found at all
            (not in the explicit argument, not in a file, environment variable, nor keyring) (default `False`)
        :param apikey: an explicit api key as a string.
        :param apikey_filepath: the path that should be used to look for api keys on the file system. Such files are
            optional, other (safer) methods exist to pass the api key, see documentation for details.
        :param use_keyring: an optional boolean (default `True`) specifying whether the `keyring` library should be
            used to lookup existing api keys. Keys should be stored using `store_apikey_in_keyring()`.
        :param keyring_entries_username: keyring stores secrets with a key made of a service id and a username. We use
            the base url for the service id, however the user name can be anything. By default we use a string:
            'apikey_user'.
        :param requests_session: an optional `Session` object to use (from `requests` lib)
        """
        # keyring option
        self.use_keyring = use_keyring
        self.keyring_entries_username = keyring_entries_username

        # Construct the base url
        if base_url is not None:
            if platform_id != 'public' and platform_id is not None:
                raise ValueError("Only one of `platform_id` and `base_url` should be provided. Received "
                                 "platform_id='%s' and base_url='%s'" % (platform_id, base_url))
            # remove trailing slashes
            while base_url.endswith('/'):
                base_url = base_url[:-1]
            self.base_url = base_url
            self.platform_id = None
        else:
            self.platform_id = platform_id
            self.base_url = ODS_BASE_URL_TEMPLATE % platform_id

        # Load apikey from file and validate it
        self.apikey_filepath = apikey_filepath
        if apikey is not None:
            # api key passed as argument
            if apikey_filepath != 'ods.apikey':
                raise ValueError("Only one of `apikey` and custom `apikey_filepath` should be provided.")
            self.apikey = apikey

        elif apikey_filepath is not None:
            try:
                # read the api key from the file
                with open(str(apikey_filepath)) as f:
                    self.apikey = f.read()
            except FileNotFoundError:
                self.apikey = None
            else:
                # remove trailing new lines or blanks if any
                self.apikey = self.apikey.rstrip()
        else:
            # no explicit api key. Environment variable will apply
            self.apikey = None

        if self.apikey is not None and len(self.apikey) == 0:
            raise ValueError('The provided api key is empty!')

        # checker flag
        self.enforce_apikey = enforce_apikey

        # create and store a session
        self.session = requests_session or Session()

    def get_whole_dataframe(self,
                            dataset_id,                  # type: str
                            use_labels_for_header=True,  # type: bool
                            tqdm=False,                  # type: bool
                            block_size=1024,             # type: int
                            file_cache=False,            # type: bool
                            **other_opts
                            ):
        """
        Returns a dataset as a pandas dataframe. pandas must be installed.

        :param dataset_id:
        :param use_labels_for_header:
        :param tqdm: a boolean indicating if a progress bar using tqdm should be displayed. tqdm should be installed
        :param block_size: an int block size used in streaming mode when tqdm is used
        :param file_cache: a boolean (default False) indicating whether the file should be written to a local cache
            `.odsclient/<base_url>_<dataset_id>.<format>`. Or a path-like object with the custom cache root folder.
        :param other_opts:
        :return:
        """
        try:
            import pandas as pd
        except ImportError as e:
            raise Exception("`get_whole_dataframe` requires `pandas` to be installed. [%s] %s" % (e.__class__, e))

        # Combine all the options
        opts = other_opts
        apikey = self.get_apikey()
        if apikey is not None:
            opts['apikey'] = apikey
        if use_labels_for_header is not None:
            opts['use_labels_for_header'] = use_labels_for_header

        # hardcoded
        if 'timezone' in opts:
            raise ValueError("'timezone' should not be specified with this method")
        if 'format' in opts:
            raise ValueError("'format' should not be specified with this method")
        opts['format'] = format = 'csv'
        if 'csv_separator' in opts:
            raise ValueError("'csv_separator' should not be specified with this method")
        opts['csv_separator'] = ';'

        # Cache usage
        if file_cache:
            # it can be a boolean or a path
            if file_cache is True:
                file_cache = CACHE_ROOT_FOLDER
            cached_file = self.get_cached_dataset_entry(dataset_id=dataset_id, format=format, cache_root=file_cache)
            try:
                # try to read the cached file in a thread-safe operation
                with cached_file.rw_lock:
                    cached_file.assert_exists()
                    df = pd.read_csv(str(cached_file.file_path), sep=';')
                    return df
            except CacheFileNotFoundError:
                pass  # does not exist. continue to query
        else:
            cached_file = None
        del file_cache

        # The URL to call
        url = self.get_download_url(dataset_id)

        # Execute call in stream mode with automatic content-type decoding
        result = self._http_call(url, params=opts, stream=True, decode=True)
        # print(iterable_to_stream(result.iter_content()).read())
        # noinspection PyTypeChecker

        if tqdm:
            from tqdm import tqdm as _tqdm

            total_size = int(result.headers.get('Content-Length', 0))
            with _tqdm(desc=url, total=total_size,
                       unit='B' if block_size == 1024 else 'it',
                       unit_scale=True,
                       unit_divisor=block_size
                       ) as bar:
                if not cached_file:
                    # Directly stream to memory with updates of the progress bar
                    df = pd.read_csv(iterable_to_stream(result.iter_content(), buffer_size=block_size, progressbar=bar),
                                     sep=';')
                else:
                    # stream to cache file and read the dataframe from the cache (use the lock to make sure it is here)
                    with cached_file.rw_lock:
                        cached_file.fill_from_iterable(result.iter_content(block_size), it_encoding=result.encoding,
                                                       progress_bar=bar, lock=False)
                        df = pd.read_csv(str(cached_file.file_path), sep=';')
        else:
            if not cached_file:
                # directly stream to memory dataframe
                df = pd.read_csv(iterable_to_stream(result.iter_content(block_size)), sep=';')
            else:
                # stream to cache file and read the dataframe from the cache (use the lock to make sure it is here)
                with cached_file.rw_lock:
                    cached_file.fill_from_iterable(result.iter_content(block_size), it_encoding=result.encoding,
                                                   lock=False)
                    df = pd.read_csv(str(cached_file.file_path), sep=';')

        return df

    # noinspection PyShadowingBuiltins
    def get_whole_dataset(self,
                          dataset_id,                  # type: str
                          format='csv',                # type: str
                          timezone=None,               # type: str
                          use_labels_for_header=True,  # type: bool
                          csv_separator=';',           # type: str
                          tqdm=False,                  # type: bool
                          to_path=None,                # type: Union[str, Path]
                          file_cache=False,            # type: bool
                          block_size=1024,             # type: int
                          **other_opts
                          ):
        """
        Returns a dataset as a csv string.

        :param dataset_id:
        :param format:
        :param timezone:
        :param use_labels_for_header:
        :param csv_separator: ';', ','...
        :param tqdm: a boolean indicating if a progress bar using tqdm should be displayed. tqdm should be installed
        :param to_path: a string indicating the file path where to write the csv. In that case None is returned
        :param file_cache: a boolean (default False) indicating whether the file should be written to a local cache
            `.odsclient/<base_url>_<dataset_id>.<format>`. Or a path-like object with the custom cache root folder.
        :param block_size: an int block size used in streaming mode when to_csv or tqdm is used
        :param other_opts:
        :return:
        """

        # ------- To uncomment one day if headers and/or body are needed
        # headers = {'Authorization': ('Bearer ' + api_key)}
        #
        # if not (requestJsonBodyStr is None):
        #     # first encode the string as bytes using the charset
        #     charset = 'utf-8'
        #     json_body_encoded_with_charset = str.encode(requestJsonBodyStr, encoding=charset)
        #     headers['Content-Type'] = 'application/json; charset=' + charset
        # else:
        #     json_body_encoded_with_charset = None
        # ------------------

        # Combine all the options
        opts = other_opts
        apikey = self.get_apikey()
        if apikey is not None:
            opts['apikey'] = apikey
        if format is not None:
            opts['format'] = format
        if timezone is not None:
            opts['timezone'] = timezone
        if use_labels_for_header is not None:
            opts['use_labels_for_header'] = use_labels_for_header
        if csv_separator is not None:
            opts['csv_separator'] = csv_separator

        # The URL to call
        url = self.get_download_url(dataset_id)

        # Should we write anything to disk ?
        # -- Because it is the target
        if to_path is not None:
            if isinstance(to_path, string_types):
                to_path = Path(to_path)
            to_path.parent.mkdir(parents=True, exist_ok=True)  # make sure the parents exist

        # -- Because the cache is used
        if file_cache:
            # it can be a boolean or a path
            if file_cache is True:
                file_cache = CACHE_ROOT_FOLDER
            cached_file = self.get_cached_dataset_entry(dataset_id=dataset_id, format=format, cache_root=file_cache)
            try:
                # Do NOT call cached_file.exists(): not thread-safe
                if to_path is None:
                    return cached_file.read()          # this is atomic: thread-safe
                else:
                    cached_file.copy_to_file(to_path)  # this is atomic: thread-safe
                    return None
            except CacheFileNotFoundError:
                # does not exist. continue to query
                pass
        else:
            cached_file = None
        del file_cache

        # Execute call, since no cache was used
        result = None
        if not tqdm:
            if to_path is None:
                # We need to return a csv string, so load everything in memory
                result, content_type = self._http_call(url, params=opts, stream=False, decode=True)

                if cached_file:  # cache it in local cache if needed
                    cached_file.fill_from_str(txt_initial_encoding=content_type, decoded_txt=result)
            else:
                # No need to return a csv string: stream directly to csv file (no decoding/encoding)
                r = self._http_call(url, params=opts, stream=True, decode=False)
                with open(str(to_path), mode='wb') as f:
                    for data in r.iter_content(block_size):
                        f.write(data)

                if cached_file:  # cache it in local cache if needed
                    cached_file.fill_from_file(file_path=to_path, file_encoding=r.encoding)
        else:
            # Progress bar is needed: we need streaming mode
            r = self._http_call(url, params=opts, stream=True, decode=False)
            total_size = int(r.headers.get('Content-Length', 0))

            from tqdm import tqdm as _tqdm
            with _tqdm(desc=url, total=total_size,
                       unit='B' if block_size == 1024 else 'it',
                       unit_scale=True,
                       unit_divisor=block_size
                       ) as bar:
                if to_path is None:
                    result = io.StringIO()                     # stream to a string in memory
                    for data in r.iter_content(block_size):    # block by block
                        bar.update(len(data))                  # - update progress bar
                        result.write(data.decode(r.encoding))  # - decode with proper encoding
                    result = result.getvalue()

                    if cached_file:                            # cache it in local cache if needed
                        cached_file.fill_from_str(txt_initial_encoding=r.encoding, decoded_txt=result)
                else:
                    with open(str(to_path), 'wb') as f:          # stream to csv file in binary mode
                        for data in r.iter_content(block_size):  # block by block
                            bar.update(len(data))                # - update progress bar
                            f.write(data)                        # - direct copy (no decoding/encoding)

                    if cached_file:                              # cache it in local cache if needed
                        cached_file.fill_from_file(file_path=to_path, file_encoding=r.encoding)

            if total_size != 0 and bar.n != total_size:
                raise ValueError("ERROR, something went wrong")

        return result

    # noinspection PyShadowingBuiltins
    def push_dataset_realtime(self,
                              dataset_id,         # type: str
                              dataset,            # type: Union[str, pandas.DataFrame]
                              push_key,           # type: str
                              format='csv',       # type: str
                              csv_separator=';',  # type: str
                              **other_opts
                              ):
        """
        Pushes a Dataset. This functions accepts either a Pandas Dataframe or a CSV string with header included.

        :param dataset_id:
        :param dataset: The dataset to push as a list of dicts, where the dict keys are the column names
        :param push_key: The Push Key provided by the API for pushing this dataset. Warning: This key is independent
                         from the API key. It can be acquired from the Realtime Push API URL section in ODS.
        :param format: The format of the dataset to be pushed. Can be `pandas` or `csv`.
        :param csv_separator: CSV separator character in case of a csv dataset input.
        :returns: HTTP Response status
        """

        if format == 'pandas':
            try:
                import pandas as pd
            except ImportError as e:
                raise Exception("`push_dataset_realtime` with the `pandas` format requires `pandas` to be installed. [%s] %s" % (e.__class__, e))
            # noinspection PyStatementEffect
            dataset  # type:pandas.DataFrame
            request_body = dataset.to_json(orient='records')
        elif format == 'csv':
            try:
                import csv
            except ImportError as e:
                raise Exception("`push_dataset_realtime` with the `csv` format requires `csv` to be installed. [%s] %s" % (e.__class__, e))
            # noinspection PyStatementEffect
            dataset  # type:str
            csv_reader = csv.DictReader(StringIO(dataset), delimiter=csv_separator)
            request_body = dumps([r for r in csv_reader])
        else:
            raise ValueError("Dataset format must be either `pandas` or `csv`")

        # Combine all the options
        opts = other_opts
        opts['pushkey'] = push_key

        # The URL to call
        url = self.get_realtime_push_url(dataset_id)

        # Execute call
        return self._http_call(url, method='post', body=request_body, params=opts, decode=False)

    def store_apikey_in_keyring(self,
                                apikey=None  # type: str
                                ):
        """
        Convenience method to store a password in the OS keyring using `keyring` lib.

        This method is a shortcut for `keyring.set_password(<base_url>, <keyring_entries_username>, <apikey>)`.

        :param apikey: an explicit apikey string. If not provided, `getpass()` will be used to prompt the user for the
            api key
        :return:
        """
        import keyring
        if apikey is None:
            apikey = getpass(prompt="Please enter your api key: ")

        if apikey is None or len(apikey) == 0:
            raise ValueError("Empty api key provided.")

        keyring.set_password(self.base_url, self.keyring_entries_username, apikey)

    def remove_apikey_from_keyring(self):
        """
        Convenience method to remove a previously stored password in the OS keyring using `keyring` lib.

        :return:
        """
        import keyring
        keyring.delete_password(self.base_url, self.keyring_entries_username)

    def get_apikey_from_keyring(self):
        """
        Looks for a keyring entry containing the api key and returns it.
        If not found, returns `None`
        :return:
        """
        import keyring
        for _url in (self.base_url, self.base_url + '/'):
            apikey = keyring.get_password(_url, self.keyring_entries_username)
            if apikey is not None:
                return apikey

    def get_apikey_from_envvar(self):
        """
        Looks for the 'ODS_APIKEY' environment variable.

         - if it does not exist return None
         - otherwise if the env variable does not begin with '{', consider it as the key
         - if it begins with '{', loads it as a dict and find a match in it, in the following order:
           platform_id, base_url, 'default'

        If the found key is an empty string, a ValueError is raised.

        :return: the api key found in the 'ODS_APIKEY' env variable (possibly for this platform_id /
            base_url), or None if it does not exist.
        """
        try:
            env_api_key = os.environ[ENV_ODS_APIKEY]
        except KeyError:
            # no env var - return None
            return None

        if len(env_api_key) > 0 and env_api_key[0] == '{':
            # a dictionary: use ast.literal_eval: more permissive than json and as safe.
            apikeys_dct = literal_eval(env_api_key)
            if not isinstance(apikeys_dct, dict):
                raise TypeError("Environment variable contains something that is neither a str not a dict")

            # remove trailing slash in keys
            def _remove_trailing_slash(k):
                while k.endswith('/'):
                    k = k[:-1]
                return k

            apikeys_dct = {_remove_trailing_slash(k): v for k, v in apikeys_dct.items()}

            # Try to get a match in the dict: first platform id, then base url, then default
            if self.platform_id in apikeys_dct:
                env_api_key = apikeys_dct[self.platform_id]
            elif self.base_url in apikeys_dct:
                env_api_key = apikeys_dct[self.base_url]
            elif 'default' in apikeys_dct:
                env_api_key = apikeys_dct['default']
            else:
                return None

        if len(env_api_key) == 0:
            raise ValueError("Empty api key found in '%s' environment variable." % ENV_ODS_APIKEY)

        return env_api_key

    def get_apikey(self):
        """
        Returns the api key that this client currently uses.

        :return:
        """
        # 1- if there is an overridden api key, use it
        if self.apikey is not None:
            return self.apikey

        # 2- if keyring service contains an entry, use it
        if self.use_keyring:
            apikey = self.get_apikey_from_keyring()
            if apikey is not None:
                return apikey

        # 3- check existence of the reference environment variable
        apikey = self.get_apikey_from_envvar()
        if apikey is not None:
            return apikey

        # 4- finally if no key was found, raise an exception if a key was required
        if self.enforce_apikey:
            raise NoODSAPIKeyFoundError(self)

    def get_download_url(self,
                         dataset_id  # type: str
                         ):
        # type: (...) -> str
        """

        :param dataset_id:
        :return:
        """
        return "%s/explore/dataset/%s/download/" % (self.base_url, dataset_id)

    def get_cached_dataset_entry(self,
                                 dataset_id,       # type: str
                                 format,           # type: str
                                 cache_root=None   # type: Union[str, Path]
                                 ):
        # type: (...) -> CacheEntry
        """
        Returns a `CacheEntry` for the given dataset
        :param dataset_id:
        :param format:
        :param cache_root:
        :return:
        """
        if self.platform_id is not None:
            p = self.platform_id
        else:
            p = baseurl_to_id_str(self.base_url)
        return CacheEntry(dataset_id=dataset_id, dataset_format=format, platform_pseudo_id=p, cache_root=cache_root)

    def get_realtime_push_url(self,
                              dataset_id,  # type: str
                              ):
        # type: (...) -> str
        """

        :param dataset_id:
        :return:
        """
        return "%s/api/push/1.0/%s/realtime/push/" % (self.base_url, dataset_id)

    def _http_call(self,
                   url,           # type: str
                   body=None,     # type: bytes
                   headers=None,  # type: Dict[str, str]
                   method='get',  # type: str
                   params=None,   # type: Dict[str, str]
                   decode=True,   # type: bool
                   stream=False   # type: bool
                   ):
        """
        Sub-routine for HTTP web service call. If Body is None, a GET is performed

        :param url:
        :param body:
        :param headers:
        :param method:
        :param params:
        :param decode: a boolean (default True) indicating if the contents should be automatically decoded following
            the content-type encoding received in the HTTP response. If this is True and stream=False (default), the
            function returns a tuple (body, content type)
        :param stream:
        :return: either a tuple (text, encoding) (if stream=False and decode=True), or the response object
        """
        try:
            # Send the request (DO NOT encode the params, this is done automatically)
            response = self.session.request(method, url, headers=headers, data=body, params=params, stream=stream)

            # Success ? Read status code, raise an HTTPError if status is error
            # status = int(response.status_code)
            response.raise_for_status()

            # detect a "wrong 200 but true 401" (unauthorized)
            if 'html' in response.headers['Content-Type']:
                raise InsufficientRightsForODSResourceError(response.headers, response.text)

            if not stream:
                if decode:
                    # Contents (encoding is automatically used to read the body when calling response.text)
                    result = response.text
                    return result, response.encoding
                else:
                    return response
            else:
                response.raw.decode_content = decode
                return response

        except HTTPError as error:
            try:
                body = error.response.text
                # {
                #   "errorcode": 10002,
                #   "reset_time": "2017-10-17T00:00:00Z",
                #   "limit_time_unit": "day",
                #   "call_limit": 10000,
                #   "error": "Too many requests on the domain. Please contact the domain administrator."
                # }
                details = loads(body)
            except JSONDecodeError:
                # error parsing the json payload?
                pass
            else:
                raise ODSException(error.response.status_code, error.response.headers, **details)

            raise error


class NoODSAPIKeyFoundError(Exception):
    """
    Raised when no api key was found (no explicit api key provided, no api key file, no env variable entry, no keyring
    entry)
    """

    def __init__(self,
                 odsclient  # type: ODSClient
                 ):
        self.odsclient = odsclient

    def __str__(self):
        return "ODS API key file not found, while it is marked as mandatory for this call (`enforce_apikey=True`). " \
               "It should either be put in a text file at path '%s', or in the `ODS_APIKEY` OS environment variable, " \
               "or (recommended, most secure) in the local `keyring`. " \
               "See documentation for details: %s. Note that you can generate an API key on this web page: " \
               "%s/account/my-api-keys/." \
               % (self.odsclient.apikey_filepath, "https://smarie.github.io/python-odsclient/#c-declaring-an-api-key",
                  self.odsclient.base_url)


class InsufficientRightsForODSResourceError(Exception):
    """
    Raised when a HTTP 200 is received from ODS together with an HTML page as body. This happens when api key is
    missing or does not grant the appropriate rights for the required resource.
    """

    def __init__(self, headers, contents):
        self.headers = headers
        self.contents = contents

    def __str__(self):
        return "An ODS query returned a HTTP 200 (OK) but with a html content-type. This is probably an " \
               "authentication problem, please check your api key using `get_apikey()`. " \
               "Headers:\n%s\nResponse:\n%s\n" % (self.headers, self.contents)


class ODSException(Exception):
    """
    An error returned by the ODS API
    """

    def __init__(self, status_code, headers, **details):
        """

        :param status_code:
        :param headers:
        :param details:
        """
        super(ODSException, self).__init__()
        self.status_code = status_code
        self.headers = headers
        self.error_msg = details['error']
        self.details = details

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return "Request failed (%s): %s\nDetails: %s\nHeaders: %s" % (self.status_code, self.error_msg,
                                                                      self.details, self.headers)


def create_session_for_fiddler():
    # type: (...) -> Session
    return create_session_for_proxy(http_proxyhost='localhost', http_proxyport=8888,
                                    use_http_for_https_proxy=True, ssl_verify=False)


def create_session_for_proxy(http_proxyhost,                  # type: str
                             http_proxyport,                  # type: int
                             https_proxyhost=None,            # type: str
                             https_proxyport=None,            # type: int
                             use_http_for_https_proxy=False,  # type: bool
                             ssl_verify=None
                             ):
    # type: (...) -> Session
    """
    Helper method to configure the `requests` package to use the proxy fo your choice and adapt the SSL certificate
    validation accordingly. Note that this is only if you do not with to use the default configuration (inherited
    from environment variables, so you can use https://smarie.github.io/develop-behind-proxy/switching/#envswitcher)

    :param http_proxyhost: mandatory proxy host for http
    :param http_proxyport: mandatory proxy port for http
    :param https_proxyhost: optional proxy host for https. If none is provided, http_proxyhost will be used
    :param https_proxyport: optional proxy port for https. If none is provided, http_proxyport will be used
    :param use_http_for_https_proxy: optional, if set to true the http protocol will be used to initiate communications
        with the proxy even for https calls (then calls will be done in https as usual).
    :param ssl_verify: optional ssl verification parameter. It may either be the path to an additional certificate
        to trust (recommended), or a boolean to enable (default)/disable (not recommended ! use only in debug mode !)
        certificate validation.
        See here for details : http://docs.python-requests.org/en/master/user/advanced/#ssl-cert-verification
    :return: a requests.Session object that you may use with the rest of the library
    """
    # config and fallback
    https_proxyhost = https_proxyhost if https_proxyhost is not None else http_proxyhost
    https_proxyport = https_proxyport if https_proxyport is not None else http_proxyport
    https_proxy_protocol = 'http' if use_http_for_https_proxy else 'https'

    s = Session()
    s.proxies = {
        'http': 'http://%s:%s' % (http_proxyhost, http_proxyport),
        'https': '%s://%s:%s' % (https_proxy_protocol, https_proxyhost, https_proxyport),
    }
    if not (ssl_verify is None):
        s.verify = ssl_verify

    # IMPORTANT : otherwise the environment variables will always have precedence over user settings
    s.trust_env = False

    return s


def iterable_to_stream(iterable, buffer_size=io.DEFAULT_BUFFER_SIZE, progressbar=None):
    """
    Lets you use an iterable (e.g. a generator) that yields bytestrings as a read-only
    input stream.

    The stream implements Python 3's newer I/O API (available in Python 2's io module).
    For efficiency, the stream is buffered.

    Source: https://stackoverflow.com/a/20260030/7262247
    """

    class IterStream(io.RawIOBase):
        def __init__(self):
            self.leftover = None

        def readable(self):
            return True

        def readinto(self, b):
            try:
                ln = len(b)  # We're supposed to return at most this much
                chunk = self.leftover or next(iterable)
                output, self.leftover = chunk[:ln], chunk[ln:]
                b[:len(output)] = output
                if progressbar:
                    progressbar.update(len(output))
                return len(output)
            except StopIteration:
                return 0  # indicate EOF

    return io.BufferedReader(IterStream(), buffer_size=buffer_size)


class CacheFileNotFoundError(FileNotFoundError):
    pass


class CacheEntry(object):
    """
    Represents a cache entry for a dataset, under `cache_root` (default CACHE_ROOT_FOLDER).
    It may not exist.

    Access to the file are thread-safe (atomic) to avoid collisions while the file is updated.
    """
    __slots__ = ('dataset_id', 'dataset_format', 'platform_pseudo_id', '_cache_root', 'rw_lock')

    def __init__(self,
                 dataset_id,          # type: str
                 dataset_format,      # type: str
                 platform_pseudo_id,  # type: str
                 cache_root=None      # type: Union[str, Path]
                 ):
        """Constructor from a dataset id and an optional root cache path"""
        self.dataset_id = dataset_id
        self.dataset_format = dataset_format
        self.platform_pseudo_id = platform_pseudo_id
        self.rw_lock = Lock()

        if cache_root is None:
            self._cache_root = None
        else:
            if isinstance(cache_root, string_types):
                cache_root = Path(cache_root)
            self._cache_root = cache_root

    def __repr__(self):
        return "CacheEntry(path='%s')" % self.file_path

    def exists(self):
        """Return True if there is a file for this cache entry, at self.file_path. Note that in multithread context
        this does not ensure that this will remain True at next python code step :) """
        return self.file_path.exists()

    @property
    def cache_root(self):
        # type: (...) -> Path
        """The root folder of the cache where this entry sits"""
        return self._cache_root if self._cache_root is not None else CACHE_ROOT_FOLDER

    @property
    def file_path(self):
        # type: (...) -> Path
        """The file where this entry sits (it may exist or not)"""
        return Path("%s/%s/%s.%s" % (self.cache_root, self.platform_pseudo_id, self.dataset_id, self.dataset_format))

    def assert_exists(self):
        """Raises an error if the file does not exist"""
        if not self.exists():
            raise CacheFileNotFoundError("Cached file entry can not be read as it does not exist: '%s'" % self.file_path)

    def read(self):
        # type: (...) -> str
        """
        Returns a string read from the cached file.
        Preserve line endings thanks to newline='' see See https://stackoverflow.com/a/50996542/7262247
        """
        with self.rw_lock:  # potentially wait for ongoing write/read to be completed, and prevent others to happen
            self.assert_exists()
            with self.file_path.open(mode="rt", newline='', encoding=CACHE_ENCODING) as f:
                result = f.read()
            return result

    def copy_to_file(self,
                     file_path  # type: Union[str, Path]
                     ):
        """
        Copy this cached file to to_path. Note that it will be encoded using CACHE_ENCODING
        but a warning was already issued at dataset retrieval time if original encoding was different
        """
        with self.rw_lock:  # potentially wait for ongoing write/read to be completed, and prevent others to happen
            self.assert_exists()
            copyfile(str(self.file_path), str(file_path))

    def delete(self):
        """
        Removes this cache entry with thread-safe protection
        """
        with self.rw_lock:
            if not self.exists():
                warnings.warn("Can not delete file entry: file does not exist: '%s'" % self.file_path)
            else:
                os.remove(str(self.file_path))

    def prepare_for_writing(self):
        """
        Makes all parent directories if needed
        Issues a warning if the file exists and is therefore overridden
        """
        if self.exists():
            warnings.warn("Cached file entry already exists and will be overridden: '%s'" % self.file_path)

        # make sure the parents exist
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

    def fill_from_str(self,
                      txt_initial_encoding,  # type: str
                      decoded_txt,           # type: str
                      ):
        """Writes a text string (already decoded) to the cache, according to the cache's encoding

        If the original encoding is not equal to the cache encoding, a warning is issued.
        """
        with self.rw_lock:  # potentially wait for ongoing write/read to be completed, and prevent others to happen
            self.prepare_for_writing()
            # Our cache uses utf-8 for all files, in order not to have to remember encodings to read back
            if txt_initial_encoding != CACHE_ENCODING:
                self.warn_encoding(original_encoding=txt_initial_encoding, cache_encoding=CACHE_ENCODING)

            # copy with the correct encoding
            self.file_path.write_bytes(decoded_txt.encode(CACHE_ENCODING))

    def _fill_from_it_no_lock(self,
                              it,                 # type: Iterable
                              it_encoding,        # type: str
                              progress_bar=None,
                              ):
        """The no-lock version of fill from iterable"""

        self.prepare_for_writing()
        if it_encoding == CACHE_ENCODING:
            # no encoding change: direct copy
            with open(str(self.file_path), 'wb') as f:  # stream to csv file in binary mode
                for data in it:  # block by block
                    if progress_bar:
                        progress_bar.update(len(data))  # - update progress bar
                    f.write(data)  # - direct copy (no decoding/encoding)
        else:
            # Our cache uses utf-8 for all files, in order not to have to remember encodings to read back
            self.warn_encoding(original_encoding=it_encoding, cache_encoding=CACHE_ENCODING)

            # we will need transcoding. Fully stream to memory string and dump to cache and datframe after
            csv_str_io = io.StringIO()  # stream to a string in memory
            for data in it:  # block by block
                if progress_bar:
                    progress_bar.update(len(data))  # - update progress bar
                csv_str_io.write(data.decode(it_encoding))  # - decode with proper encoding
            csv_str = csv_str_io.getvalue()

            # store in cache with proper encoding
            self.file_path.write_bytes(csv_str.encode(CACHE_ENCODING))

    def fill_from_iterable(self,
                           it,                # type: Iterable
                           it_encoding,       # type: str
                           progress_bar=None,
                           lock=True
                           ):
        """
        Fill this cache entry from an iterable of bytes
        :param it:
        :param it_encoding:
        :param progress_bar:
        :return: csv_str if it was streamed to memory in the process (if transcoding was needed)
        """
        if lock:
            with self.rw_lock:  # potentially wait for ongoing write/read to be completed, and prevent others to happen
                self._fill_from_it_no_lock(it=it, it_encoding=it_encoding, progress_bar=progress_bar)
        else:
            self._fill_from_it_no_lock(it=it, it_encoding=it_encoding, progress_bar=progress_bar)

    def fill_from_file(self,
                       file_path,      # type: Union[str, Path]
                       file_encoding,  # type: str
                       ):
        """Copies a file to the cache.

        If the original encoding is not equal to the cache encoding, conversion happens and a warning is issued.
        """
        with self.rw_lock:  # potentially wait for ongoing write/read to be completed, and prevent others to happen
            self.prepare_for_writing()
            if file_encoding == CACHE_ENCODING:
                # no encoding change: direct copy
                copyfile(str(file_path), str(self.file_path))
            else:
                # Our cache uses utf-8 for all files, in order not to have to remember encodings to read back
                self.warn_encoding(original_encoding=file_encoding, cache_encoding=CACHE_ENCODING)
                # read with newline-preserve and with original encoding
                with open(str(file_path), mode="rt", newline='', encoding=file_encoding) as f_src:
                    contents = f_src.read()
                # write with the cache encoding
                with open(str(self.file_path), mode='wt', encoding=CACHE_ENCODING) as f_dest:
                    f_dest.write(contents)

    def warn_encoding(self, original_encoding, cache_encoding):
        """
        Issues a warning when the original encoding was different from the one in the cache and a conversion occured
        """
        warnings.warn(
            "[odsclient-cache] Cached file for dataset %r will use %r encoding while original encoding on "
            " ODS was %r. This will most probably have no side effects except if your dataset"
            " contains characters that can not be encoded in utf-8 such as old/alternative"
            " forms of east asian kanji. See https://en.wikipedia.org/wiki/Unicode#Issues"
            % (self.dataset_id, cache_encoding, original_encoding))


def baseurl_to_id_str(base_url):
    """ Transform an ODS platform url into an identifier string usable for example as file/folder name"""

    o = urlparse(base_url)

    # start with host name
    result_str = o.netloc

    # simplify the public ODS site
    if result_str.endswith(".opendatasoft.com"):
        result_str = result_str.replace(".opendatasoft.com", "")

    # optionally add custom sub-path
    if o.path and o.path != "/":
        _path = o.path.replace("/", "_")

        # ensure trailing _
        if not _path.startswith("_"):
            _path = "_" + _path

        # ensure no ending _
        if _path.endswith("_"):
            _path = _path[:-1]

        result_str += _path

    return result_str
