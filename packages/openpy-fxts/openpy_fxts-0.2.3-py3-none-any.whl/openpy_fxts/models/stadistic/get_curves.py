# -*- coding: utf-8 -*-
# @Time    : 31/08/2023
# @Author  : Ing. Jorge Lara
# @Email   : jlara@iee.unsj.edu.ar
# @File    : ------------
# @Software: PyCharm

import pandas as pd
import matplotlib.pyplot as plt
from datetime import time


def get_curves_typical(
        data: pd.DataFrame,
        colums_load: list,
        name_sce: str,
        plot: bool = False,
        path_save: str = None,
        view: bool = True
):
    data['aux2'] = data.hour.astype(str) + ':' + data.minute.astype(str)
    data['mean'] = data[colums_load].mean(axis=1)
    data['std'] = data[colums_load].std(axis=1)
    data['aux'] = data.index
    data['aux'] = data.aux.dt.strftime('%H:%M')
    df_curve_typical = data.pivot_table(index=['hour', 'minute'], values=['mean', 'std'])
    df_curve_typical['aux2'] = data.index.strftime('%H:%M').unique()
    df_curve_typical.set_index('aux2', inplace=True)
    if plot:
        df_AllUsers = data.pivot_table(index=['hour', 'minute'], values=colums_load)
        df_AllUsers['aux2'] = data.index.strftime('%H:%M').unique()
        df_AllUsers.set_index('aux2', inplace=True)
        df_summary = pd.concat([df_curve_typical, df_AllUsers], axis=1)
        df_summary['aux2'] = data.index.strftime('%H:%M').unique()
        df_summary.set_index('aux2', inplace=True)
        fig = plt.figure()
        plt.figure().clear()
        for col in df_summary.columns:
            if col == 'mean':
                plt.plot(
                    df_summary[col],
                    "r-",
                    label='mean'
                )
            if col == 'std':
                plt.plot(
                    df_summary[col],
                    "g-",
                    label='std'
                )
            else:
                plt.plot(
                    df_summary[col],
                    "k-",
                    alpha=.15,
                    #label=str(col)
                )
        plt.xticks(rotation=90)
        plt.legend(loc='lower right')
        plt.title(name_sce)
        if view:
            plt.show()
        if path_save is not None:
            plt.savefig(f'{path_save}\\{name_sce}.png')
    return df_curve_typical


