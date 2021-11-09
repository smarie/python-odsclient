#  Authors: Sylvain MARIE <sylvain.marie@se.com>
#            + All contributors to <https://github.com/smarie/python-odsclient>
#
#  License: 3-clause BSD, <https://github.com/smarie/python-odsclient/blob/master/LICENSE>
from odsclient.core import ODSClient, ODSException, NoODSAPIKeyFoundError, InsufficientRightsForODSResourceError, \
    ENV_ODS_APIKEY, KR_DEFAULT_USERNAME, CacheEntry
from odsclient.shortcuts import get_whole_dataset, get_whole_dataframe, store_apikey_in_keyring, \
    get_apikey_from_keyring, remove_apikey_from_keyring, get_apikey, clean_cache, get_cached_dataset_entry

__all__ = [
    # submodules
    'core', 'shortcuts',
    # symbols
    'ODSClient', 'ODSException', 'NoODSAPIKeyFoundError', 'InsufficientRightsForODSResourceError',
    'ENV_ODS_APIKEY', 'KR_DEFAULT_USERNAME',
    'get_whole_dataset', 'get_whole_dataframe', 'store_apikey_in_keyring', 'get_apikey_from_keyring',
    'remove_apikey_from_keyring', 'get_apikey', 'clean_cache', 'get_cached_dataset_entry', 'CacheEntry'
]
