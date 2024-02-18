# -*- coding: utf-8 -*-
# @Time    : 27/07/2023
# @Author  : Ing. Jorge Lara
# @Email   : jlara@iee.unsj.edu.ar
# @File    : ------------
# @Software: PyCharm

import pandas as pd


def date_init_final(config: dict = None):
    init = config['dataset'].index[0]
    final = config['dataset'].index[-1]
    date1 = f"{init.year}{init.month}{init.day}"
    date2 = f"{final.year}{final.month}{final.day}"
    n_in_out = f"int{config['n_past']}_out{config['n_future']}"
    fts = ""
    for i in config['y_colname']:
        fts += f"_{i}"
    name_folder = date1 + '_' + date2 + fts + '_' + n_in_out
    mttr_upd = 'mttr_' + config['MTTR'] + '_upd_' + config['Act']

    return name_folder, mttr_upd


def get_numeric_categorical(dataset: pd.DataFrame = None):
    col_type = dataset.dtypes
    numeric = col_type[col_type != object].index
    categorical = col_type[col_type == object].index
    return numeric, categorical
