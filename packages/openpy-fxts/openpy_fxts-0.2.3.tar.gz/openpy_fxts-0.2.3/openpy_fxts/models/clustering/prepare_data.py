# -*- coding: utf-8 -*-
# @Time    : 29/08/2023
# @Author  : Ing. Jorge Lara
# @Email   : jlara@iee.unsj.edu.ar
# @File    : ------------
# @Software: PyCharm

import pandas as pd
import numpy as np


def get_scenarios_for_time_features(
        data,
        seasons: bool = False,
        month: bool = False,
        day_name: bool = False,
        day_type: bool = False,
):
    scenarios = dict()
    aux = 0
    if not seasons and not month and not day_name and not day_type:
        return None

    if not seasons and month and not day_name and not day_type:
        for month in list(data['month'].unique()):
            data_filter = data[data['month'] == month].copy()
            if not data_filter.empty:
                data_filter['sce'] = aux
                scenarios[month] = data_filter
                aux += 1
        return scenarios

    if not seasons and month and day_name and not day_type:
        for month in list(data['month'].unique()):
            for day_name in list(data['day_name'].unique()):
                data_filter = data[(data['month'] == month) & (data['day_name'] == day_name)].copy()
                if not data_filter.empty:
                    data_filter['sce'] = aux
                    scenarios[f'{month}_{day_name}'] = data_filter
                    aux += 1
        return scenarios

    if not seasons and month and day_name and day_type:
        for month in list(data['month'].unique()):
            for day_name in list(data['day_name'].unique()):
                df_aux = pd.DataFrame()
                for day_type in list(data['day_type'].unique()):
                    data_filter = data[(data['month'] == month) & (data['day_name'] == day_name) & (data['day_type'] == day_type)].copy()
                    if not data_filter.empty:
                        data_filter['sce'] = aux
                        df_aux = pd.concat([df_aux, data_filter])
                        aux += 1
                        scenarios[f'{month}_{day_name}_{day_type}'] = df_aux
        return scenarios

    if not seasons and not month and day_name and not day_type:
        for day_name in list(data['day_name'].unique()):
            data_filter = data[data['day_name'] == day_name].copy()
            if not data_filter.empty:
                data_filter['sce'] = aux
                scenarios[day_name] = data_filter
                aux += 1
        return scenarios

    if not seasons and not month and day_name and day_type:
        for day_name in list(data['day_name'].unique()):
            df_aux = pd.DataFrame()
            for day_type in list(data['day_type'].unique()):
                data_filter = data[(data['day_name'] == day_name) & (data['day_type'] == day_type)].copy()
                if not data_filter.empty:
                    data_filter['sce'] = aux
                    df_aux = pd.concat([df_aux, data_filter])
                    aux += 1
                    scenarios[f'{day_name}_{day_type}'] = df_aux
        return scenarios

    if not seasons and not month and not day_name and day_type:
        for day_type in list(data['day_type'].unique()):
            data_filter = data[data['day_type'] == day_type].copy()
            if not data_filter.empty:
                data_filter['sce'] = aux
                scenarios[day_type] = data_filter
                aux += 1
        return scenarios

    if seasons and not month and not day_name and not day_type:
        for season in list(data['seasons'].unique()):
            data_filter = data[data['seasons'] == season].copy()
            if not data_filter.empty:
                data_filter['sce'] = aux
                scenarios[season] = data_filter
                aux += 1
        return scenarios

    if seasons and month and not day_name and not day_type:
        for season in list(data['seasons'].unique()):
            for month in list(data['month'].unique()):
                data_filter = data[(data['seasons'] == season) & (data['month'] == month)].copy()
                if not data_filter.empty:
                    data_filter['sce'] = aux
                    scenarios[f'{season}_{month}'] = data_filter
                    aux += 1
        return scenarios

    if seasons and month and day_name and not day_type:
        for season in list(data['seasons'].unique()):
            for month in list(data['month'].unique()):
                for day_name in list(data['day_name'].unique()):
                    data_filter = data[(data['seasons'] == season) & (data['month'] == month) & (data['day_name'] == day_name)].copy()
                    if not data_filter.empty:
                        data_filter['sce'] = aux
                        scenarios[f'{season}_{month}_{day_name}'] = data_filter
                        aux += 1
        return scenarios

    if seasons and month and day_name and day_type:
        for season in list(data['seasons'].unique()):
            for month in list(data['month'].unique()):
                for day_name in list(data['day_name'].unique()):
                    df_aux = pd.DataFrame()
                    for day_type in list(data['day_type'].unique()):
                        data_filter = data[
                            (data['seasons'] == season) & (data['month'] == month) & (data['day_name'] == day_name) & (data['day_type'] == day_type)].copy()
                        if not data_filter.empty:
                            data_filter['sce'] = aux
                            df_aux = pd.concat([df_aux, data_filter])
                            aux += 1
                            scenarios[f'{season}_{month}_{day_name}_{day_type}'] = df_aux
        return scenarios

def get_mean(array):
    array = np.asarray(array)
    array = np.reshape(array, (-1, 24))
    array = np.mean(array, axis=0)
    return array


def get_std_dev(array):
    array = np.asarray(array)
    array = np.reshape(array, (-1, 24))
    array = np.std(array, axis=0)
    return array