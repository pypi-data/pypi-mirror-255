# -*- coding: utf-8 -*-
# @Time    : 24/03/2023
# @Author  : Ing. Jorge Lara
# @Email   : jlara@iee.unsj.edu.ar
# @File    : ------------
# @Software: PyCharm

import logging
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from ..utilities.Utils import Utils

log_py = logging.getLogger(__name__)


class utils_view:

    def density_true_missing(
            self,
            df_miss: pd.DataFrame = None,
            dict_mdls: dict = None,
            view: bool = False,
            cumulative=False
    ):

        col_miss = Utils(df_miss).list_column_missing()
        list_x = []
        list_y = []
        aux = 0
        for i in range(0, len(col_miss), 2):
            list_x.append(aux)
            list_x.append(aux)
            list_y.append(0)
            list_y.append(1)
            aux += 1

        sns.set(style='darkgrid')
        fig, ax = plt.subplots(figsize=(29, 12), nrows=int(round(len(col_miss) / 2, 1)), ncols=2)
        for col, i, j in zip(col_miss, list_x, list_y):
            if len(col_miss) <= 2:
                for key, value in dict_mdls.items():
                    sns.kdeplot(
                        x=value[col][df_miss.isnull().any(axis=1)], label=key, ax=ax[j], cumulative=cumulative
                    )
                ax[j].legend()
            else:
                for key, value in dict_mdls.items():
                    sns.kdeplot(
                        x=value[col][df_miss.isnull().any(axis=1)], label=key, ax=ax[i][j], cumulative=cumulative
                    )
                ax[i][j].legend()
        if view:
            plt.show()

    def data_correlation_heatmap(self, df):
        sns.heatmap(
            data=df.corr(),
            cmap=sns.diverging_palette(20, 230, as_cmap=True),
            center=0,
            vmin=-1,
            vmax=1,
            linewidths=0.5,
            annot=True
        )
