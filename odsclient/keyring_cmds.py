from subprocess import call

import click

from odsclient.core import KR_DEFAULT_USERNAME, ODSClient
from odsclient.shortcuts import store_apikey_in_keyring, get_apikey_from_keyring, remove_apikey_from_keyring


@click.group()
def odskeys():
    """
    Commandline utility to get/set/remove api keys from the OS keyring using the `keyring` library.
    To get help on each command use:

        odskeys <cmd> --help

    """
    pass


def _get_url_used(platform_id,  # type: str
                  base_url,     # type: str
                  ):
    # type: (...) -> str
    """ returns the url actually used by the ODSClient """
    client = ODSClient(platform_id=platform_id, base_url=base_url)
    return client.base_url


@odskeys.command(name="get")
@click.option('-p', '--platform_id', default='public', help="Specific ODS platform id. Default 'public'")
@click.option('-b', '--base_url', default=None, help="Specific ODS base url. Default: "
                                                     "https://<platform_id>.opendatasoft.com/")
@click.option('-u', '--username', default=KR_DEFAULT_USERNAME, help='Custom username to use in the keyring entry. '
                                                                    'Default: %s' % KR_DEFAULT_USERNAME)
def get_ods_apikey(platform_id,                   # type: str
                   base_url,                      # type: str
                   username=KR_DEFAULT_USERNAME,  # type: str
                   ):
    """
    Looks up an ODS apikey entry in the keyring. Custom ODS platform id or base url can be provided through options.
    """
    apikey = get_apikey_from_keyring(platform_id=platform_id,
                                     base_url=base_url,
                                     keyring_entries_username=username,
                                     )
    # actual url used, for message prints
    url_used = _get_url_used(platform_id=platform_id, base_url=base_url)
    if apikey is not None:
        click.echo("Api key found for platform url '%s': %s" % (url_used, apikey))
    else:
        click.echo("No api key registered for platform url '%s'" % (url_used, ))


@odskeys.command(name="remove")
@click.option('-p', '--platform_id', default='public', help="Specific ODS platform id. Default 'public'")
@click.option('-b', '--base_url', default=None, help="Specific ODS base url. Default: "
                                                     "https://<platform_id>.opendatasoft.com/")
@click.option('-u', '--username', default=KR_DEFAULT_USERNAME, help='Custom username to use in the keyring entry. '
                                                                    'Default: %s' % KR_DEFAULT_USERNAME)
def remove_ods_apikey(platform_id='public',          # type: str
                      base_url=None,                 # type: str
                      username=KR_DEFAULT_USERNAME,  # type: str
                      ):
    """
    Removes an ODS apikey entry from the keyring. Custom ODS platform id or base url can be provided through options.
    """
    apikey = get_apikey_from_keyring(platform_id=platform_id,
                                     base_url=base_url,
                                     keyring_entries_username=username,
                                     )
    # actual url used, for message prints
    url_used = _get_url_used(platform_id=platform_id, base_url=base_url)
    if apikey is None:
        click.echo("No api key registered for platform url '%s'" % (url_used,))
    else:
        remove_apikey_from_keyring(platform_id=platform_id,
                                   base_url=base_url,
                                   keyring_entries_username=username,
                                   )
        apikey = get_apikey_from_keyring(platform_id=platform_id,
                                         base_url=base_url,
                                         keyring_entries_username=username,
                                         )
        assert apikey is None
        click.echo("Api key removed successfully for platform url '%s'" % (url_used,))


@odskeys.command(name="set")
@click.option('-p', '--platform_id', default='public', help="Specific ODS platform id. Default 'public'")
@click.option('-b', '--base_url', default=None, help="Specific ODS base url. Default: "
                                                     "https://<platform_id>.opendatasoft.com/")
@click.option('-u', '--username', default=KR_DEFAULT_USERNAME, help='Custom username to use in the keyring entry. '
                                                                    'Default: %s' % KR_DEFAULT_USERNAME)
@click.option('-k', '--apikey', help="apikey to register. If none is provided, you will be prompted for it.")
def set_ods_apikey(platform_id='public',          # type: str
                   base_url=None,                 # type: str
                   username=KR_DEFAULT_USERNAME,  # type: str
                   apikey=None                    # type: str
                   ):
    """
    Creates an ODS apikey entry in the keyring. Custom ODS platform id or base url can be provided through options.
    """
    store_apikey_in_keyring(platform_id=platform_id,
                            base_url=base_url,
                            keyring_entries_username=username,
                            apikey=apikey
                            )
    gotapikey = get_apikey_from_keyring(platform_id=platform_id,
                                        base_url=base_url,
                                        keyring_entries_username=username,
                                        )
    if apikey is not None:
        assert apikey == gotapikey
    else:
        # api key provided through getpass() - we do not have access to it
        assert gotapikey is not None
    # actual url used, for message print
    url_used = _get_url_used(platform_id=platform_id, base_url=base_url)
    click.echo("Api key defined successfully for platform url '%s'" % (url_used,))


@odskeys.command(name="show")
@click.option('-a', '--alt', default=0, help='Alternative #id (the number of available alternatives is '
                                             'platform dependent)')
def show_os_mgr(alt=0,  # type: int
                ):
    """
    Shows the OS credentials manager associated with current keyring backend.
    When several alternatives exist, the `--alt` option can be used to switch from 0 (default) to others.

    Currently supported backends and alternatives:

    Windows WinVaultKeyring:
     - (alt 0, default) control.exe /name Microsoft.CredentialManager
     - (alt 1) rundll32.exe keymgr.dll, KRShowKeyMgr

    """
    import keyring
    kr = keyring.get_keyring()
    if 'Windows WinVaultKeyring' in kr.name:
        alts = {
            0: ["control.exe", "/name", "Microsoft.CredentialManager"],
            1: ["cmd.exe", "/c", "start", "/B", "rundll32.exe", "keymgr.dll,KRShowKeyMgr"]
        }
    else:
        click.echo("This command is not supported for keyring backend '%s', please report it here:"
                   " https://github.com/smarie/python-odsclient/issues/" % (kr.name, ))
        return

    # execute the alternative
    try:
        cmd = alts[alt]
    except KeyError:
        click.echo("Invalid alternative #: %s. Only [0-%s] are supported with keyring backend %s"
                   % (alt, len(alts)-1, kr.name))
        return
    else:
        click.echo("Keyring backend is '%s'. Runnning command for alternative %s: '%s'" % (kr.name, alt, ' '.join(cmd)))
        call(cmd)


# @odskeys.command(name="list")
# @click.option('-p', '--platform_id', default='public', help='Filter on a specific ODS platform id.')
# @click.option('-b', '--base_url', default=1, help='Filter on a specific ODS base url')
# def list_ods_keys(platform_id,  # type: str
#                   base_url      # type: str
#                   ):
#     """
#     Lists the
#     """
#     click.echo('Filtering: %s, %s!' % (platform_id, base_url))
#     # list with https://github.com/jaraco/keyring/issues/151
#     # but this does not work with windows backend
#     for item in keyring.get_keyring().get_preferred_collection().get_all_items():
#         print(item.get_label(), item.get_attributes())


if __name__ == '__main__':
    odskeys()
