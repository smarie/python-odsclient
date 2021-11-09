# coding: utf-8
import pandas as pd

from odsclient.utils import create_reading_buffer


def ref_dataset_public_platform():
    """Return a reference dataset for the public ODS platform """

    dataset_id = "opendatasoft-offices"

    ref_csv = """Geo Point;Geo Shape;Office Name;Address
48.8416126212,2.28492558002;"{""type"": ""Point"", ""coordinates"": [2.2849255800247192, 48.841612621157495]}";Paris HQ;"Opendatasoft
130, rue de Lourmel
75015 Paris, France"
47.2176789432,-1.5440967679;"{""type"": ""Point"", ""coordinates"": [-1.5440967679023743, 47.217678943247684]}";Nantes Office;"Opendatasoft
4 rue Voltaire
44000 Nantes"
42.3568473029,-71.0575962067;"{""type"": ""Point"", ""coordinates"": [-71.05759620666502, 42.356847302874996]}";Boston HQ;"Opendatasoft LLC
50 Milk St, 16th floor
Boston MA 02109, U.S.A."
""" #.replace("\n", "\r\n")

    # we keep this hardcoded just in case the ref_df reading does not work as expected
    ref_shape = (3, 3)

    ref_df = pd.read_csv(create_reading_buffer(ref_csv, is_literal=True), sep=';')
    ref_df = ref_df.set_index(['Office Name']).sort_index()

    return dataset_id, ref_csv, ref_df, ref_shape


def ref_dataset_other_platform():
    """ Return a reference dataset for the uat-data.exchange.se.com ODS platform """

    # shared info
    # dataset_id = "employment-by-sector-in-france-and-the-united-states-1800-2012"
    # base_url = "https://data.exchange.se.com/"
    dataset_id = "odsclient-reference-dataset"
    base_url = "https://uat-data.exchange.se.com/"

    ref_csv = """Transport;Année;Millions de Voyageurs
SNCF - Trains/RER (y compris T4);;
RATP - RER;;
RATP - RER;2011;7575
RATP - Métro;;
RATP - RER;2014;7722
RATP - Métro;2014;5194
SNCF - Trains/RER (y compris T4);2011;11583
RATP - RER;2010;7486
RATP - RER;2013;7605
SNCF - Trains/RER (y compris T4);2013;12103
RATP - Métro;2012;5130
RATP - RER;2012;7675
SNCF - Trains/RER (y compris T4);2014;12148
SNCF - Trains/RER (y compris T4);2010;11221
RATP - Métro;2013;5044
RATP - Métro;2010;4892
SNCF - Trains/RER (y compris T4);2012;11816
RATP - Métro;2011;5022
""".replace("\n", "\r\n")
    ref_df = pd.read_csv(create_reading_buffer(ref_csv, is_literal=True), sep=';')
    ref_df = ref_df.set_index(['Transport', 'Année']).sort_index()

    ref_shape = (18, 1)

    return base_url, dataset_id, ref_csv, ref_df, ref_shape
