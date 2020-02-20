try:
    from typing import Dict
except ImportError:
    pass
from requests import Session, HTTPError


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
    Helper method to configure the request package to use the proxy fo your choice and adapt the SSL certificate
    validation accordingly

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

    # ----- old with urllib
    # # fiddler is a localhost:8888 proxy
    # proxy = request.ProxyHandler({'http': '127.0.0.1:8888', 'https': '127.0.0.1:8888'})
    #
    # # don't verify SSL certificate, fiddler replaces the ones from outside with its own.
    # ctx = ssl.create_default_context()
    # ctx.check_hostname = False
    # ctx.verify_mode = ssl.CERT_NONE
    # https = request.HTTPSHandler(context=ctx)
    #
    # # chain the two options and install them
    # opener = request.build_opener(proxy, https)
    # request.install_opener(opener)

    https_proxyhost = https_proxyhost or http_proxyhost
    https_proxyport = https_proxyport or http_proxyport
    https_proxy_protocol = 'http' if use_http_for_https_proxy else 'https'

    s = Session()
    s.proxies = {
                    'http': 'http://' + http_proxyhost + ':' + str(http_proxyport),
                    'https': https_proxy_protocol + '://' + https_proxyhost + ':' + str(https_proxyport),
                }
    if not (ssl_verify is None):
        s.verify = ssl_verify

    # IMPORTANT : otherwise the environment variables will always have precedence over user settings
    s.trust_env = False

    return s


def url_encode(**kwargs):
    """
    Returns a url-encoded string such as 'format=csv&timezone=Europe/Paris&use_labels_for_header=true'

    :param kwargs: key-value options
    :return:
    """
    return '&'.join(['{}={}'.format(k, v) for k,v in kwargs.items()])


ODS_BASE_URL_TEMPLATE = "https://%s.opendatasoft.com/explore/dataset/"


def get_whole_dataset(dataset_id,                  # type: str
                      format='csv',                # type: str
                      timezone=None,               # type: str
                      use_labels_for_header=None,  # type: bool
                      platform_id='public',        # type: str
                      base_url=None,               # type: str
                      apikey=None,                 # type: str
                      apikeyfile_path=None,        # type: str
                      requests_session=None,       # type: Session
                      **other_opts
                      ):
    """
    Shortcut metho

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
                                    **other_opts)


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

    def get_whole_dataset(self,
                          dataset_id,                  # type: str
                          format='csv',                # type: str
                          timezone=None,               # type: str
                          use_labels_for_header=None,  # type: bool
                          **other_opts
                          ):
        """

        :param dataset_id:
        :param format:
        :param timezone:
        :param use_labels_for_header:
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

        # The URL to call
        url = "{base_url}/{dataset_id}/download/".format(base_url=self.base_url, dataset_id=dataset_id)

        # Execute call
        result = self._http_call(url, params=opts)

        return result

    def _http_call(self,
                   url,           # type: str
                   body=None,     # type: bytes
                   headers=None,  # type: Dict[str, str]
                   method='get',  # type: str
                   params=None    # type: Dict[str, str]
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
            # Send the request
            response = self.session.request(method, url, headers=headers, data=body, params=params)

            # Parse the response
            status = int(response.status_code)

            # raise an HTTPError if status is error
            response.raise_for_status()

            # headers not useful : encoding is automatically used to read the body when calling response.text
            result = response.text

            return result

        except HTTPError as error:

            print("The request failed with status code: " + str(error.response.status_code))

            # Print the headers - they may include some useful debugging info
            print(error.response.headers)

            raise  # ODSException(error)
