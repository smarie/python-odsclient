from __future__ import print_function

import sys
import pandas as pd

from io import BytesIO   # to handle byte strings
from io import StringIO  # to handle unicode strings

if sys.version_info >= (3, 0):
    def create_reading_buffer(value, is_literal):
        return StringIO(value)
else:
    def create_reading_buffer(value, is_literal):
        if is_literal:
            return BytesIO(value)
        else:
            return StringIO(value)

from odsclient import get_whole_dataset, get_whole_dataframe


def test_example():
    """basic test: retrieve an example dataset """

    # with debug_requests():
    csv_str = get_whole_dataset("world-growth-since-the-industrial-revolution0",
                                platform_id='public')
#     csv_str = csv_str.replace('\r\n', '\n').replace('\r', '\n')
    print(csv_str)

    ref_csv = """Year Ending;World output;World population;Per capita output
2012-12-31;3.03783837;1.39292748;1.62231324
1700-12-31;0.07352168;0.05783974;0.01567288
1820-12-31;0.51654477;0.44594248;0.07028884
1913-12-31;1.48929571;0.58556427;0.89847031
"""
    # this does not work as returned order may change
    # assert csv_str == ref_csv

    # move to pandas
    df = pd.read_csv(create_reading_buffer(csv_str, is_literal=False), sep=';')

    # compare with ref
    ref_df = pd.read_csv(create_reading_buffer(ref_csv, is_literal=True), sep=';')
    df = df.set_index('Year Ending').sort_index()
    ref_df = ref_df.set_index('Year Ending').sort_index()
    pd.testing.assert_frame_equal(df, ref_df)
    assert df.shape == (4, 3)

    # test the pandas direct streaming API
    df2 = get_whole_dataframe("world-growth-since-the-industrial-revolution0")
    df2 = df2.set_index('Year Ending').sort_index()
    pd.testing.assert_frame_equal(df, df2)
