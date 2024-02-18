# -*- coding: utf-8 -*-
# @Time    : 06/07/2023
# @Author  : Ing. Jorge Lara
# @Email   : jlara@iee.unsj.edu.ar
# @File    : ------------
# @Software: PyCharm

import pandas as pd

value_miss = -1
seed_lab = 44


class init_class:

    def __init__(self, dataframe=None):
        self.dataframe = dataframe


class init_models:

    def __init__(
            self,
            df_miss: pd.DataFrame = None,
            df_true: pd.DataFrame = None
    ):
        self.df_miss = df_miss
        self.df_true = df_true
