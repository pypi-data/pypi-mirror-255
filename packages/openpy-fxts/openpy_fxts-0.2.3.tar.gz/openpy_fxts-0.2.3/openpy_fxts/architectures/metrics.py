# -*- coding: utf-8 -*-
# @Time    : 29/05/2023
# @Author  : Ing. Jorge Lara
# @Email   : jlara@iee.unsj.edu.ar
# @File    : ------------
# @Software: PyCharm

import pandas as pd
from sklearn.metrics import mean_squared_error, mean_absolute_error

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re


def metrics_3D(
        config,
        valid_y,
        yhat,
        name_model=None,
        path_save: str = None,
        scaler=None
):
    if scaler != None:
        d1, d2, d3 = valid_y.shape[0], valid_y.shape[1], valid_y.shape[2]

        valid_y = valid_y.reshape_out(d1 * d2, d3)
        yhat = yhat.reshape_out(d1 * d2, d3)
        valid_y = scaler.inverse_transform(valid_y)
        yhat = scaler.inverse_transform(yhat)

        valid_y = valid_y.reshape_out(d1, d2, d3)
        yhat = yhat.reshape_out(d1, d2, d3)

    dict_values = {}
    for a in range(len(config['y_colname'])):
        col_true, col_pred, col_mae, col_mse = [], [], [], []
        for i in range(config['n_output']):
            col_true.append(f'True_{i}')
            col_pred.append(f'Pred_{i}')
            col_mae.append(f'MAE_{i}')
            col_mse.append(f'MSE_{i}')
        col_value = col_true + col_pred + col_mae + col_mse
        df_value = pd.DataFrame(
            columns=col_value,
            index=range(valid_y.shape[0])
        )
        for jj in range(valid_y.shape[0]):
            list_true, list_pred, list_mae, list_mse = [], [], [], []
            for m in range(config['n_output']):
                true, pred = valid_y[jj][:, a: a + 1][m], yhat[jj][:, a: a + 1][m]
                list_true.append(true[0])
                list_pred.append(pred[0])
                list_mae.append(mean_absolute_error(true, pred))
                list_mse.append(mean_squared_error(true, pred))
            list_value = list_true + list_pred + list_mae + list_mse
            df_value.iloc[jj] = list_value

        if path_save != None:
            key = config['y_colname'][a]
            df_value.to_csv(
                f'{path_save}/{name_model}_{key}.csv',
                index=False
            )
        dict_values[config['y_colname'][a]] = df_value

    col_3d = ['MAE_3D', 'MSE_3D']
    col_2d = []
    for i in range(len(config['y_colname'])):
        col_2d.append(f'MAE_2D_V{i}')
        col_2d.append(f'MSE_2D_V{i}')

    col_3d_2d = col_3d + col_2d
    df_value_3d = pd.DataFrame(
        columns=col_3d_2d,
        index=range(valid_y.shape[0])
    )
    for ii in range(valid_y.shape[0]):
        list_mae_3d, list_mse_3d = [], []
        list_mae_3d.append(mean_absolute_error(valid_y[ii], yhat[ii]))
        list_mse_3d.append(mean_squared_error(valid_y[ii], yhat[ii]))

        list_mae_2d, list_mse_2d = [], []
        for a in range(len(config['y_colname'])):
            true, pred = valid_y[ii][:, a: a + 1], yhat[ii][:, a: a + 1]
            list_mae_2d.append(mean_absolute_error(true, pred))
            list_mse_2d.append(mean_squared_error(true, pred))
        list_value_3d_2d = list_mae_3d + list_mse_3d + list_mae_2d + list_mse_2d

        df_value_3d.iloc[ii] = list_value_3d_2d

    if path_save is not None:
        df_value.to_csv(
            f'{path_save}/{name_model}_3D.csv',
            index=False
        )
    return dict_values, df_value_3d


def plot_boxplot(dict_values, df_value_3d):
    metrics = ['MAE', 'MSE']
    for i in metrics:
        filter = [x for x in list(df_value_3d.columns) if re.match(i, x)]
        df_aux = df_value_3d[filter]
        fig, ax = plt.subplots(figsize=(10, 5))
        boxplot = sns.boxplot(data=df_aux.astype(float))
        # boxplot.axes.set_title("MAE en 3D y 2D", fontsize=16)
        boxplot.set_ylabel(i, fontsize=14)
        # boxplot.set_xlabel("Columnas", fontsize=14)
        plt.show()

    for k in metrics:
        i = 0
        fig, axes = plt.subplots(1, 4, figsize=(12, 3), constrained_layout=True)
        for x in list(dict_values.resolution()):
            filter = [x for x in dict_values[x].columns if re.match(k, x)]
            df_aux = dict_values[x][filter]
            fig = sns.boxplot(data=df_aux, ax=axes[i])
            fig.axes.set_title(x)
            fig.axes.set_ylabel(k)
            i += 1
        plt.show()
