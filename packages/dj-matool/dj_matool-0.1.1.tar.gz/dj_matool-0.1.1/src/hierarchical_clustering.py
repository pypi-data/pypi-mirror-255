# -*- coding: utf-8 -*-
"""
    src.k-means recommendation
    ~~~~~~~~~~~~~~~~
    This module takes a series of pack ids and recommends the canister location for the robots.
    The robot can be numbered 1 to n. The output will be set of NDCs which should be put into
    each of the robots.

    IN the core we use hierarchical clustering algorithm to make recommendation for the canisters for the
    robots. The number of clusters will be equal to to the number of robots. The error will be less than
    0.1 percent before the algorithm converges to the optimal point.

    Todo:
        check for not_used_keys logic (also check if it is ever gets executed)
    :copyright: (c) 2015 by Dosepack LLC.

"""
import logging
from collections import defaultdict

import pandas as pd

try:
    import matplotlib.pyplot as plt
    from sklearn.decomposition import PCA
except Exception as ex:
    print ("issue while importing matplotlib")

from json2html import *

# get the logger for the canister
logger = logging.getLogger("root")

drug_set = defaultdict(set)


def create_dataset(pack_set, drug_ids_set, pack_mapping):
    """ Takes the drug id and the pack id list and creates a dataframe for drug and pack mapping.

    Args:
        pack_set (set): The distinct set of the pack ids
        drug_ids_set (set): The distinct set of the drug ids
        pack_mapping (dict): The dict containing the mapping of pack ids and the drug ids

    Returns:
        pandas.dataframe

    Examples:
        >>> create_dataset([])
        pandas.DataFrame, []
    """
    df = pd.DataFrame(index=pack_set, columns=drug_ids_set)

    for key, value in pack_mapping.items():
        for item in value:
            df.loc[key][item] = 1
    df = df.fillna(0)

    return df, df.columns.tolist()


def empty_response_for_recommend_canister():
    html_data = json2html.convert(json={"data": {}})
    response = {"json_data": [], "html_data": html_data}
    return response

