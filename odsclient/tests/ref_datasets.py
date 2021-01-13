# coding: utf-8
import pandas as pd

from odsclient.utils import create_reading_buffer


def ref_dataset_public_platform():
    """Return a reference dataset for the public ODS platform """

    dataset_id = "respect-des-delais-dacheminement-courrier"

    ref_csv = """Catégorie;Objectif ou Réalisation;Pourcentage;Annee
Lettre prioritaire J + 1;réalisation;0.867;2014
Colissimo guichet J + 2;objectif;0.88;2014
Courrier industriel J + 2;réalisation;0.965;2009
Lettre prioritaire J + 1;réalisation;0.847;2009
Lettre prioritaire J + 1;objectif;0.85;2014
Lettre recommandée J + 2;objectif;0.9400000000000001;2014
Lettre recommandée J + 2;réalisation;0.887;2009
Courrier industriel J + 2;réalisation;0.969;2014
Colissimo guichet J + 2;réalisation;0.91;2014
Courrier industriel J + 2;objectif;0.9500000000000001;2009
Colissimo guichet J + 2;réalisation;0.877;2009
Lettre verte J + 2;objectif;0.9400000000000001;2014
Lettre prioritaire J + 1;objectif;0.84;2009
Lettre recommandée J + 2;réalisation;0.9460000000000001;2014
Lettre verte J + 2;réalisation;0.932;2014
Courrier industriel J + 2;objectif;0.9500000000000001;2014
Colissimo guichet J + 2;objectif;0.86;2009
""".replace("\n", "\r\n")

    # we keep this explicit just in case the ref_df reading does not work as expected
    ref_shape = (17, 1)

    ref_df = pd.read_csv(create_reading_buffer(ref_csv, is_literal=True), sep=';')
    ref_df = ref_df.set_index(['Catégorie', 'Objectif ou Réalisation', 'Annee']).sort_index()

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
