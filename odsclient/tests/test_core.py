import pytest

from odsclient import get_whole_dataset, ODSException


def test_error_bad_dataset_id():
    """Tests that an error associated with bad dataset id is correctly received"""
    with pytest.raises(ODSException)as exc_info:
        get_whole_dataset("unknwn", platform_id='public')

    assert exc_info.value.error_msg == "Unknown dataset: unknwn"
