import io
from json import loads
try:
    # python 3
    from urllib.parse import quote
except ImportError:
    # python 2
    from urllib import quote

try:
    from typing import Dict
except ImportError:
    pass
from requests import Session, HTTPError


ODS_BASE_URL_TEMPLATE = "https://%s.opendatasoft.com/explore/dataset"


def get_whole_dataframe(dataset_id,                  # type: str
                        use_labels_for_header=True,  # type: bool
                        platform_id='public',        # type: str
                        base_url=None,               # type: str
                        apikey=None,                 # type: str
                        apikeyfile_path=None,        # type: str
                        requests_session=None,       # type: Session
                        **other_opts
                        ):
    """
    Shortcut method for DatalibClient(...).get_whole_dataframe(...)
    Returns a dataset as a pandas dataframe. pandas must be installed.

    :param dataset_id:
    :param platform_id:
    :param base_url:
    :param apikey:
    :param apikeyfile_path:
    :param requests_session:
    :param other_opts:
    :return:
    """
    client = DatalibClient(platform_id=platform_id, base_url=base_url, apikey=apikey, apikeyfile_path=apikeyfile_path,
                           requests_session=requests_session)
    return client.get_whole_dataframe(dataset_id=dataset_id, use_labels_for_header=use_labels_for_header, **other_opts)


def get_whole_dataset(dataset_id,                  # type: str
                      format='csv',                # type: str
                      timezone=None,               # type: str
                      use_labels_for_header=True,  # type: bool
                      csv_separator=';',           # type: str
                      platform_id='public',        # type: str
                      base_url=None,               # type: str
                      apikey=None,                 # type: str
                      apikeyfile_path=None,        # type: str
                      requests_session=None,       # type: Session
                      **other_opts
                      ):
    """
    Shortcut method for DatalibClient(...).get_whole_dataset(...)

    :param dataset_id:
    :param format:
    :param timezone:
    :param use_labels_for_header:
    :param platform_id: the ods platform id to use. This id is used to construct the base URL based on the pattern
            https://<platform_id>.opendatasoft.com/explore/dataset/. Default is `'public'` which leads to the base url
            https://public.opendatasoft.com/explore/dataset/
    :param base_url: an explicit base url to use instead of the one generated from `platform_id`
    :param apikey: an explicit api key as a string.
    :param apikeyfile_path: a path to a file containing an api key. Only one of `apikey` and `apikeyfile` should be
        provided.
    :param requests_session: an optional `Session` object to use (from `requests` lib)
    :param other_opts:
    :return:
    """
    client = DatalibClient(platform_id=platform_id, base_url=base_url, apikey=apikey, apikeyfile_path=apikeyfile_path,
                           requests_session=requests_session)
    return client.get_whole_dataset(dataset_id=dataset_id, format=format,
                                    timezone=timezone, use_labels_for_header=use_labels_for_header,
                                    csv_separator=csv_separator, **other_opts)


class DatalibClient(object):
    """
    A client for the ODS datalib.
    """

    def __init__(self,
                 platform_id='public',   # type: str
                 base_url=None,          # type: str
                 apikey=None,            # type: str
                 apikeyfile_path=None,   # type: str
                 requests_session=None   # type: Session
                 ):
        """

        :param platform_id: the ods platform id to use. This id is used to construct the base URL based on the pattern
            https://<platform_id>.opendatasoft.com/explore/dataset/. Default is `'public'` which leads to the base url
            https://public.opendatasoft.com/explore/dataset/
        :param base_url: an explicit base url to use instead of the one generated from `platform_id`
        :param apikey: an explicit api key as a string.
        :param apikeyfile_path: a path to a file containing an api key. Only one of `apikey` and `apikeyfile` should be
            provided.
        :param requests_session: an optional `Session` object to use (from `requests` lib)
        """
        # Construct the base url
        if base_url is not None:
            if platform_id != 'public':
                raise ValueError("Only one of `platform_id` and `base_url` should be provided.")
            self.base_url = base_url
        else:
            self.base_url = ODS_BASE_URL_TEMPLATE % platform_id

        # Load apikey from file and validate it
        if apikey is not None:
            if apikeyfile_path is not None:
                raise ValueError("Only one of `apikey` and `apikeypath` should be provided.")
            self.apikey = apikey
        elif apikeyfile_path is not None:
            try:
                with open(apikeyfile_path) as f:
                    self.apikey = f.read()
            except FileNotFoundError as e:
                raise Exception("Please create a text file containing the ODS api key, and either name it 'apikey' or "
                                "specify its name/path in the apikeyfile_path argument. Note that you can generate an "
                                "API key on this web page: https://<name>.opendatasoft.com/account/my-api-keys/")
        else:
            self.apikey = None

        if self.apikey is not None and len(self.apikey) == 0:
            raise ValueError('The api key is empty!')

        # create and store a session
        self.session = requests_session or Session()

    def get_whole_dataframe(self,
                            dataset_id,                  # type: str
                            use_labels_for_header=True,  # type: bool
                            **other_opts
                            ):
        """
        Returns a dataset as a pandas dataframe. pandas must be installed.

        :param dataset_id:
        :param use_labels_for_header:
        :param other_opts:
        :return:
        """
        try:
            import pandas as pd
        except ImportError as e:
            raise Exception("`get_whole_dataframe` requires `pandas` to be installed. [%s] %s" % (e.__class__, e))

        # Combine all the options
        opts = other_opts
        if self.apikey is not None:
            opts['apikey'] = self.apikey
        if use_labels_for_header is not None:
            opts['use_labels_for_header'] = use_labels_for_header

        # hardcoded
        if 'timezone' in opts:
            raise ValueError("'timezone' should not be specified with this method")
        if 'format' in opts:
            raise ValueError("'format' should not be specified with this method")
        opts['format'] = 'csv'
        if 'csv_separator' in opts:
            raise ValueError("'csv_separator' should not be specified with this method")
        opts['csv_separator'] = ';'

        # The URL to call
        url = self.get_download_url(dataset_id)

        # Execute call in stream mode
        result = self._http_call(url, params=opts, stream=True)
        # print(iterable_to_stream(result.iter_content()).read())
        df = pd.read_csv(iterable_to_stream(result.iter_content()), sep=';')

        return df

    def get_download_url(self,
                         dataset_id  # type: str
                         ):
        # type: (...) -> str
        """

        :param dataset_id:
        :return:
        """
        return "%s/%s/download/" % (self.base_url, dataset_id)

    def get_whole_dataset(self,
                          dataset_id,                  # type: str
                          format='csv',                # type: str
                          timezone=None,               # type: str
                          use_labels_for_header=True,  # type: bool
                          csv_separator=';',           # type: str
                          **other_opts
                          ):
        """

        :param dataset_id:
        :param format:
        :param timezone:
        :param use_labels_for_header:
        :param csv_separator: ';', ','...
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
        if self.apikey is not None:
            opts['apikey'] = self.apikey
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

        # Execute call
        result = self._http_call(url, params=opts)

        return result

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

        :param body:
        :param headers:
        :param method
        :param url:
        :return:
        """
        try:
            # Send the request (DO NOT encode the params, this is done automatically)
            response = self.session.request(method, url, headers=headers, data=body, params=params, stream=stream)

            # Success ? Read status code, raise an HTTPError if status is error
            status = int(response.status_code)
            response.raise_for_status()

            if not stream:
                if decode:
                    # Contents (encoding is automatically used to read the body when calling response.text)
                    result = response.text
                    return result
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
            except Exception as e:
                # error parsing the json payload?
                pass
            else:
                raise ODSException(error.response.status_code, error.response.headers, **details)

            raise error


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
        'https': '%s://%s:%s' % (https_proxy_protocol, https_proxyhost,  https_proxyport),
    }
    if not (ssl_verify is None):
        s.verify = ssl_verify

    # IMPORTANT : otherwise the environment variables will always have precedence over user settings
    s.trust_env = False

    return s


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
        self.status_code = status_code
        self.headers = headers
        self.error_msg = details['error']
        self.details = details

    def __repr__(self):
        return "Request failed (%s): %s\nDetails: %s\nHeaders: %s" % (self.status_code, self.error_msg,
                                                                      self.details, self.headers)


def iterable_to_stream(iterable, buffer_size=io.DEFAULT_BUFFER_SIZE):
    """
    Lets you use an iterable (e.g. a generator) that yields bytestrings as a read-only
    input stream.

    The stream implements Python 3's newer I/O API (available in Python 2's io module).
    For efficiency, the stream is buffered.
    """
    class IterStream(io.RawIOBase):
        def __init__(self):
            self.leftover = None
        def readable(self):
            return True
        def readinto(self, b):
            try:
                l = len(b)  # We're supposed to return at most this much
                chunk = self.leftover or next(iterable)
                output, self.leftover = chunk[:l], chunk[l:]
                b[:len(output)] = output
                return len(output)
            except StopIteration:
                return 0    # indicate EOF
    return io.BufferedReader(IterStream(), buffer_size=buffer_size)
