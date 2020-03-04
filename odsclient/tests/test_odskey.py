import pytest
from click.testing import CliRunner

from odsclient.keyring_cmds import odskeys


@pytest.mark.parametrize('platform_id, base_url', [(None, None),
                                                   ('hello', None),
                                                   (None, 'http://blouh/')])
def test_odskey(platform_id, base_url):
    """Basic tests for the CLI """

    other_args = []
    if platform_id is not None:
        assert base_url is None
        other_args += ['-p', platform_id]
        url_used = "https://%s.opendatasoft.com" % platform_id
    elif base_url is not None:
        other_args += ['-b', base_url]
        url_used = base_url[0:-1] if base_url.endswith('/') else base_url
    else:
        url_used = "https://public.opendatasoft.com"
    msg = "platform url '%s'" % url_used

    runner = CliRunner()

    result = runner.invoke(odskeys, ['remove'] + other_args)
    assert result.exit_code == 0
    assert result.output == "No api key registered for %s\n" % msg

    result = runner.invoke(odskeys, ['get'] + other_args)
    assert result.exit_code == 0
    assert result.output == "No api key registered for %s\n" % msg

    result = runner.invoke(odskeys, ['set', '-k', 'blah'] + other_args)
    assert result.exit_code == 0
    assert result.output == "Api key defined successfully for %s\n" % msg

    result = runner.invoke(odskeys, ['get'] + other_args)
    assert result.exit_code == 0
    assert result.output == "Api key found for %s: blah\n" % msg

    result = runner.invoke(odskeys, ['remove'] + other_args)
    assert result.exit_code == 0
    assert result.output == "Api key removed successfully for %s\n" % msg

    result = runner.invoke(odskeys, ['get'] + other_args)
    assert result.exit_code == 0
    assert result.output == "No api key registered for %s\n" % msg
