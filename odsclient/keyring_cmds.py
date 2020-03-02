import click

from odsclient.core import KR_DEFAULT_USERNAME
from odsclient.shortcuts import store_apikey_in_keyring, get_apikey_from_keyring, remove_apikey_from_keyring


@click.group()
def odskeys():
    """
    Commandline utility to get/set/remove api keys from the OS keyring using the `keyring` library.
    To get help on each command use:

        odskeys <cmd> --help

    """
    pass


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

    if base_url is None:
        if apikey is not None:
            click.echo("Api key found for platform id '%s': %s" % (platform_id, apikey))
        else:
            click.echo("No api key registered for platform id '%s'" % (platform_id, ))
    else:
        if apikey is not None:
            click.echo("Api key found for platform url '%s': %s" % (base_url, apikey))
        else:
            click.echo("No api key registered for platform url '%s'" % (base_url, ))


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
    if apikey is None:
        if base_url is None:
            click.echo("No api key registered for platform id '%s'" % (platform_id,))
        else:
            click.echo("No api key registered for platform url '%s'" % (base_url,))
        return

    remove_apikey_from_keyring(platform_id=platform_id,
                               base_url=base_url,
                               keyring_entries_username=username,
                               )
    apikey = get_apikey_from_keyring(platform_id=platform_id,
                                     base_url=base_url,
                                     keyring_entries_username=username,
                                     )
    assert apikey is None
    if base_url is None:
        click.echo("Api key removed successfully for platform id '%s'" % (platform_id,))
    else:
        click.echo("Api key removed successfully for platform url '%s'" % (base_url,))


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
    if base_url is None:
        click.echo("Api key defined successfully for platform id '%s'" % (platform_id,))
    else:
        click.echo("Api key defined successfully for platform url '%s'" % (base_url,))


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
