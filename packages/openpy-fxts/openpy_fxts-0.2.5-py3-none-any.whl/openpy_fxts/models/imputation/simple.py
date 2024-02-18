# -*- coding: utf-8 -*-
# @Time    : 25/03/2023
# @Author  : Ing. Jorge Lara
# @Email   : jlara@iee.unsj.edu.ar
# @File    : ------------
# @Software: PyCharm

import pandas as pd
from sklearn.impute import SimpleImputer
from openpy_fxts.models.imputation.utilities.Utils import Metrics, Utils
from openpy_fxts.models.imputation.base_lib import init_models
from openpy_fxts.utils import get_numeric_categorical
import impyute as impy
import numpy as np



mt = Metrics()


class imp_basic(init_models):

    def __init__(
            self,
            df_miss: pd.DataFrame = None,
            df_true: pd.DataFrame = None,
            metrics: dict = None
    ):
        super().__init__(df_miss, df_true)
        self.df_miss = df_miss
        self.df_true = df_true
        self.metrics = metrics
        self.list_aux = Utils(self.df_miss).list_column_missing()

    def constant(
            self,
            method: list
    ):
        """
        
        :param method: 
        :return: 
        """
        # imputing with a constan
        df_imp = self.df_miss.copy(deep=True)
        df_imp.iloc[:, :] = SimpleImputer(strategy=method).fit_transform(df_imp)
        if self.df_true is None:
            return df_imp
        else:
            if self.metrics is None or len(self.metrics) == 0:
                self.metrics = dict()
            self.metrics = mt.add_dict_metrics(
                self.df_true[self.list_aux],
                df_imp[self.list_aux],
                self.metrics,
                f'const_{method}'
            )
            return df_imp, self.metrics

    def fillna(
            self,
            method: list = None,
            aux: str = 'mean'
    ):
        """
        :param list_fillna:
        :return:
        """
        df_imp = self.df_miss.copy(deep=True)
        df_imp.fillna(method=method, inplace=True)
        if Utils(df_imp).check_missing():
            df_imp.iloc[:, :] = SimpleImputer(strategy=aux).fit_transform(df_imp)
        if self.df_true is None:
            return df_imp
        else:
            if self.metrics is None or len(self.metrics) == 0:
                self.metrics = dict()
            self.metrics = mt.add_dict_metrics(
                self.df_true[self.list_aux],
                df_imp[self.list_aux],
                self.metrics,
                f'const_{method}'
            )
            return df_imp, self.metrics

    def moving_window_replace(
            self,
            res_min: int = 15,
            n_days: int = None,
            previous: bool = None,
            back: bool = None
    ):
        df_imp = self.df_miss.copy(deep=True)
        data = df_imp.values
        if previous is None and back is None:
            previous = True
        window = (24 * 60) / res_min
        if n_days is not None:
            n_days = 1
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
        df_imp.iloc[:, :] = data

        if self.df_true is None:
            return df_imp
        else:
            if self.metrics is None or len(self.metrics) == 0:
                self.metrics = dict()
            self.metrics = mt.add_dict_metrics(
                self.df_true[self.list_aux],
                df_imp[self.list_aux],
                self.metrics,
                'window_replace'
            )
            return df_imp, self.metrics

    def moving_window_mean(
            self,
            n_hours: int = None,
            res_min: int = None,
            n_past: bool = None,
            n_future: bool = None,
    ):
        df_imp = self.df_miss.copy(deep=True)
        data = df_imp.values
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
        df_imp.iloc[:, :] = data
        if self.df_true is None:
            return df_imp
        else:
            if self.metrics is None or len(self.metrics) == 0:
                self.metrics = dict()
            self.metrics = mt.add_dict_metrics(
                self.df_true[self.list_aux],
                df_imp[self.list_aux],
                self.metrics,
                'window_mean'
            )
            return df_imp, self.metrics

    def interpolate(
            self,
            method: str,
            axis=0,
            limit=None,
            inplace=True,
            limit_direction=None,
            limit_area=None,
            downcast=None,
            order=2,
            aux: str = 'mean'
    ):
        """
        :param method:
        :param axis:
        :param limit:
        :param inplace:
        :param limit_direction:
        :param limit_area:
        :param downcast:
        :param order:
        :param aux:
        :return:
        """
        df_imp = self.df_miss.copy(deep=True)
        df_imp.interpolate(
            method=method,
            axis=axis,
            limit=limit,
            inplace=inplace,
            limit_direction=limit_direction,
            limit_area=limit_area,
            downcast=downcast,
            order=order
        )
        if Utils(df_imp).check_missing():
            model = SimpleImputer(strategy=aux)
            df_imp.iloc[:, :] = model.fit_transform(df_imp)
        if self.df_true is None:
            return df_imp
        else:
            if self.metrics is None or len(self.metrics) == 0:
                self.metrics = dict()
            self.metrics = mt.add_dict_metrics(
                self.df_true[self.list_aux],
                df_imp[self.list_aux],
                self.metrics,
                f'const_{method}'
            )
            return df_imp, self.metrics
