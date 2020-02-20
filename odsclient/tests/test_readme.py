from odsclient import get_whole_dataset


def test_example():
    """basic test: retrieve an example dataset """

    csv_str = get_whole_dataset(dataset_id="world-growth-since-the-industrial-revolution0",
                                format="csv",
                                timezone="Europe/Berlin",
                                lang="fr",
                                use_labels_for_header=True,
                                csv_separator=';')
    csv_str = csv_str.replace('\r\n', '\n').replace('\r', '\n')
    assert csv_str == """Year Ending;World output;World population;Per capita output
2012-12-31;3.03783837;1.39292748;1.62231324
1700-12-31;0.07352168;0.05783974;0.01567288
1820-12-31;0.51654477;0.44594248;0.07028884
1913-12-31;1.48929571;0.58556427;0.89847031
"""
    print(csv_str)
