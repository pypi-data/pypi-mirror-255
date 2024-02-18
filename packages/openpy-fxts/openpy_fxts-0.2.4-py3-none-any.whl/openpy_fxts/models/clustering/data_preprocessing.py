# -*- coding: utf-8 -*-
# @Time    : 04/09/2023
# @Author  : Ing. Jorge Lara
# @Email   : jlara@iee.unsj.edu.ar
# @File    : data_preprocessing.py
# @Software: PyCharm
import os
import glob
import pandas as pd
import numpy as np
from openpy_fxts.preprocessing_data.utils import add_time_features
from openpy_fxts.models.clustering.prepare_data import get_scenarios_for_time_features
from openpy_fxts.error_handling_logging import update_logg_file

import seaborn as sns
import matplotlib.pyplot as plt


def _user_id(data):
    return data['Unnamed: 1'][1]


def _clean_file(df):
    df = df.drop([0, 1, 2, 3, 4, 5, 6])
    df = df.dropna(how='all', axis=1)
    df.columns = list(df.iloc[:1].values[0])
    df = df.drop([df.index[0]], axis=0)
    df.set_index(df.columns[0], inplace=True)
    df = df.loc[pd.notnull(df.index)]
    df = df[[x for x in list(df.columns) if str(x) != 'nan']]
    df['W'] = df['Wh'] / 0.25
    return df[list(df.columns)[-2:]]


def dimensionality_reduction(df):
    df_clean = pd.DataFrame()  # datasets frame vacío.
    for h in range(0, 24):  # h va a ieterar 24 veces representando las 24 horas del día.
        df_clean = pd.DataFrame()
        k = [h]
        Hora_Dia = df[df['hour'].isin(k)]  # filtramos por hora del dia
        Hora_Dia_Acumu = Hora_Dia.groupby(['year', 'mount', 'Dia_M', 'hour'])[
            'E_Activa(Wh)'].sum()  # Sumar las mediciones de los periodos de 15 min entre horas
        Hora_Dia_Acum_ = pd.DataFrame(pd.DataFrame(Hora_Dia_Acumu))  # convertir a datasets frame a dataframe
        Hora_Dia_Acum_ = Hora_Dia_Acum_.reset_index(drop=True)  # se elimina niveles de índices
        vector = Hora_Dia_Acum_['E_Activa(Wh)']
        name_colum = '$%d$' % h  # nombre de la columna
        df_clean = df_clean.copy()
        df_clean[name_colum] = vector  # coloca el vector hora h en la columna h de df_celan
        df_clean = pd.concat([df_clean, df_clean], axis=1)  # adjuntos el nuevo vector de las horas Al dataframe
        df_clean = df_clean.dropna(how='any')  # Elimino datos null de df
        df_clean.columns = range(
            df_clean.shape[1])  # cambiamos el tipo de datos de los nombres de las columnas para redireccionar luego

    return df_clean


class read_BBDD:

    def multiple_user_files(
            self,
            file_folder_path: str = None,
            save_folder_path: str = None
    ):
        os.chdir(file_folder_path)
        filelist = glob.glob('*.xlsx')  # Muestra una lista de todos los archivos excel dentro del directorio
        i = 0
        df_user_Max_W = pd.DataFrame()
        df_user_W = pd.DataFrame()
        for filename in filelist:
            print(filename)
            data_user = pd.read_excel(filename)
            user = _user_id(data_user)
            data_user = _clean_file(data_user)
            df_aux1, df_aux2 = pd.DataFrame(), pd.DataFrame()
            df_aux1[user] = data_user[data_user.columns[0]]
            df_aux2[user] = data_user[data_user.columns[1]]
            df_user_Max_W = pd.concat([df_user_Max_W, df_aux1], axis=1)
            df_user_W = pd.concat([df_user_W, df_aux2], axis=1)
        df_user_Max_W.to_csv(f'{save_folder_path}\\alluser_Max_W.csv')
        df_user_W.to_csv(f'{save_folder_path}\\alluser_W.csv')


class scenarios:

    def multiple_users(
            self,
            file_path,
            index_col: int = 0,
            parse_dates: bool = True,
            dict_scenario: dict = None,
            id_col_users:  str = 'nroserie',
            variable: str = 'kW',
            col_user: str = None,
            col_meas: list = None
    ):
        data = pd.read_csv(
            file_path,
            index_col=index_col,
            parse_dates=parse_dates
        )

        data = pd.pivot_table(
            data=data,
            index=data.index,
            columns=id_col_users,
            values=variable
        )
        data.index.name = 'index'
        if data.isnull().sum().sum() > 0:
            moving_window_replace(data.values, n_days=7)
        data = add_time_features(data)
        if dict_scenario is None:
            scenarios = get_scenarios_for_time_features(
                data,
                seasons=True,
                month=True,
                day_name=True,
                day_type=True
            )
            return scenarios
        else:
            for key, value in dict_scenario.items():
                if value is None:
                    dict_scenario[key] = list(data[key].unique())
            data_filter = data[
                (data.seasons.isin(dict_scenario['seasons'])) &
                (data.month.isin(dict_scenario['month'])) &
                (data.year.isin(dict_scenario['year'])) &
                (data.day_name.isin(dict_scenario['day_name'])) &
                (data.day_type.isin(dict_scenario['day_type']))
                ]
            if data_filter.empty:
                print('Modify the scenario filtering dictionary')
                return None
            else:
                data_filter
                return data_filter

    def single_user(
            self,
            file_path,
            dict_scenario: dict = None,
            id_user: str = None,
            only_df: bool = None,
            index_col: int = 0,
            parse_dates: bool = True

    ):
        if dict_scenario is not None:
            only_df = False
        data = pd.read_csv(
            file_path,
            index_col=index_col,
            parse_dates=parse_dates
        )
        if data.isnull().sum().sum() > 0:
            moving_window_replace(data.values, n_days=7)
        if id_user is None:
            col_init = list(data.columns)[0]
            data = data[[col_init]]
        else:
            #col_init = id_user
            data = data[[id_user]]
        data = add_time_features(data)
        if dict_scenario is None:
            if only_df:
                return data
            else:
                return get_scenarios_for_time_features(
                    data,
                    seasons=True,
                    month=True,
                    day_name=True,
                    day_type=True
                )
        else:
            for key, value in dict_scenario.items():
                if value is None:
                    dict_scenario[key] = list(data[key].unique())
            data_filter = data[
                (data.seasons.isin(dict_scenario['seasons'])) &
                (data.month.isin(dict_scenario['month'])) &
                (data.year.isin(dict_scenario['year'])) &
                (data.day_name.isin(dict_scenario['day_name'])) &
                (data.day_type.isin(dict_scenario['day_type']))
            ]
            if data_filter.empty:
                print('Modify the scenario filtering dictionary')
                return None
            else:
                data_filter
                return data_filter

    def filter_scenario(self):
        pass


def moving_window_replace(
        data: np.array = None,
        res_min: int = 15,
        n_days: int = None,
        previous: bool = None,
        back: bool = None
):
    if previous is None and back is None:
        previous = True
    window = (24 * 60) / res_min
    if n_days is not None:
        window = window * n_days
    n = 0
    window = int(window)
    while len(data[np.isnan(data)]) > 0:
        print(f'iter:{n}, n_NaN:{len(data[np.isnan(data)])}')
        for row in range(data.shape[0]):
            for col in range(data.shape[1]):
                if np.isnan(data[row, col]):
                    if previous:
                        try:
                            data[row, col] = data[row - window, col]
                        except IndexError:
                            try:
                                data[row, col] = data[row + window, col]
                            except IndexError:
                                pass
                    if back:
                        try:
                            data[row, col] = data[row + window, col]
                        except IndexError:
                            try:
                                data[row, col] = data[row - window, col]
                            except IndexError:
                                pass
        n += 1


def moving_window_mean(
        data: np.array = None,
        n_hours: int = None,
        res_min: int = None,
        n_past: bool = None,
        n_future: bool = None,
):
    aux = 0
    if n_hours is None:
        n = 1
        n_hours = n * 60
    while len(data[np.isnan(data)]) > 0:
        print(f'iter:{aux}, n_NaN:{len(data[np.isnan(data)])}')
        if n_past is None and n_future is None and res_min is not None:
            n_past, n_future = n_hours / res_min, n_hours / res_min
        elif n_past is None and n_future is None and res_min is None:
            n_past, n_future = 4, 4
        for row in range(data.shape[0]):
            for col in range(data.shape[1]):
                if np.isnan(data[row, col]):
                    data[row, col] = np.concatenate(
                        (
                            data[row - n_past: row, col],
                            data[row: row + n_future, col]
                        )
                    ).mean()
                    if np.isnan(data[row, col]):
                        data[row, col] = data[row - n_past: row, col].mean()
                        if np.isnan(data[row, col]):
                            data[row, col] = data[row: row + n_future, col].mean()
        aux += 1


class segmentation_analysis:

    def add_discrete_variables(self, season, mount, type, ):
        pass


class dimensionality_reduction:
    pass
