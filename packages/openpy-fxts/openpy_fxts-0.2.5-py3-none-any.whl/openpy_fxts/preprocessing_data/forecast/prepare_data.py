# -*- coding: utf-8 -*-
# @Time    : 06/07/2023
# @Author  : Ing. Jorge Lara
# @Email   : jlara@iee.unsj.edu.ar
# @File    : ------------
# @Software: PyCharm


import pandas as pd
import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.preprocessing import MinMaxScaler

from openpy_fxts.preprocessing_data.forecast.utils_data import sin_transformer, cos_transformer, _filter_y_features, \
    _series_to_supervised, _scaler_data

pd.options.mode.chained_assignment = None


class feature_engineering:

    def __init__(self, df: pd.DataFrame):
        self.df = df

    def add_season(self, ):
        return self.df

    def add_temporaly(self, ):
        return self.df

    def trigonometric_features(self, categorical_columns: list[str] = None):
        one_hot_encoder = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
        cyclic_cossin_transformer = ColumnTransformer(
            transformers=[
                ("categorical", one_hot_encoder, categorical_columns),
                ("month_sin", sin_transformer(12), ["month"]),
                ("month_cos", cos_transformer(12), ["month"]),
                ("weekday_sin", sin_transformer(7), ["weekday"]),
                ("weekday_cos", cos_transformer(7), ["weekday"]),
                ("hour_sin", sin_transformer(24), ["hour"]),
                ("hour_cos", cos_transformer(24), ["hour"]),
            ],
            remainder=MinMaxScaler(),
        )
        return cyclic_cossin_transformer

    def periodic_spline_features(self, categorical_columns):
        from sklearn.preprocessing import SplineTransformer
        one_hot_encoder = OneHotEncoder(handle_unknown="ignore", sparse_output=False)

        def periodic_spline_transformer(period, n_splines=None, degree=3):
            if n_splines is None:
                n_splines = period
            n_knots = n_splines + 1  # periodic and include_bias is True
            return SplineTransformer(
                degree=degree,
                n_knots=n_knots,
                knots=np.linspace(0, period, n_knots).reshape(n_knots, 1),
                extrapolation="periodic",
                include_bias=True,
            )

        cyclic_spline_transformer = ColumnTransformer(
            transformers=[
                ("categorical", one_hot_encoder, categorical_columns),
                ("cyclic_month", periodic_spline_transformer(12, n_splines=6), ["month"]),
                ("cyclic_weekday", periodic_spline_transformer(7, n_splines=3), ["weekday"]),
                ("cyclic_hour", periodic_spline_transformer(24, n_splines=12), ["hour"]),
            ],
            remainder=MinMaxScaler(),
        )
        return cyclic_spline_transformer


class pre_processing_data:

    def __init__(
            self,
            config: dict = None,
            train: bool = None,
            valid: bool = None,
            test: bool = None,
    ):

        self.config = config
        self.train = train
        self.valid = valid
        self.test = test

        self.pct_valid = config['pct_valid']
        self.pct_test = config['pct_test']
        self.dataset = config['dataset']

    def split_ts_Train_Valid_Test(
            self
    ):
        print('separate dataset in train, validation and test')
        if self.pct_valid is None:
            aux_valid = 0
        else:
            aux_valid = self.pct_valid
        if self.pct_test is None:
            aux_test = 0
        else:
            aux_test = self.pct_test
        p_train = 1 - aux_valid - aux_test
        n_train = int(self.dataset.shape[0] * p_train)
        n_valid = int(self.dataset.shape[0] * aux_valid)
        n_test = n_train + n_valid
        df_train = self.dataset.iloc[:n_train, :]
        print(f'Train: {df_train.shape}')
        if aux_valid != 0:
            df_valid = self.dataset.iloc[n_train: n_train + n_valid, :]
            print(f'Valid: {df_valid.shape}')
        else:
            df_valid = None
        if aux_test != 0:
            df_test = self.dataset.iloc[n_test:, :]
            print(f'Test: {df_test.shape}')
        else:
            df_test = None
        return df_train, df_valid, df_test

    def _pre_processed_data_pipeline(
            self,
            df_data=None,
            seasonal_features=True,
            diff_trend=True,
            exog=True,
            fourier_terms=True,
            dropnan=None
    ):

        df_scaler, scaler = _scaler_data(df_data)
        ###CALCULATE SEASONAL MEANS
        if seasonal_features:
            pass

        if diff_trend:
            pass

        if exog:
            pass

        if fourier_terms:
            pass

        ts_sequence = _series_to_supervised(
            data=df_scaler,
            dropnan=dropnan,
            n_in=self.config['n_past'],
            n_out=self.config['n_future'],
            feat_str_at_end=True,
            feat_lag_str='IP',
            feat_lead_str='OP'
        )
        # cambiar el monento de incluir al agregar informacion de la fecha y transformaciones.
        n_past = self.config['n_past'] * len(self.config['x_colname'])
        n_future = self.config['n_future'] * len(self.config['x_colname'])
        df_X, df_y = ts_sequence.iloc[:, :n_past], ts_sequence.iloc[:, -n_future:]
        df_y = _filter_y_features(df_y, self.config['y_colname'], self.config['n_future'])
        return df_X, df_y, scaler

    def transformer_data(
            self,
            view: bool = True,
            dropnan: bool = None
    ):
        if view:
            print(f'Dataset -> {self.dataset.shape}')
        class_data = pre_processing_data(self.config, self.train, self.valid, self.test)
        df_train, df_valid, df_test, = class_data.split_ts_Train_Valid_Test()
        ts_pre_process = {}
        dict_train = {}
        train_X, train_y, scaler_train = class_data._pre_processed_data_pipeline(
            df_data=df_train,
            dropnan=dropnan
        )
        # reshape input to be 3D [samples, timesteps, features]
        # Training
        train_X = train_X.values.reshape(train_X.shape[0], self.config['n_past'], self.config['n_inp_ft'])
        train_y = train_y.values.reshape(train_y.shape[0], self.config['n_future'], self.config['n_out_ft'])
        if view:
            print(f'Train -> X: {train_X.shape} - y:{train_y.shape}')
        dict_train['X'], dict_train['y'], dict_train['scaler'] = train_X, train_y, scaler_train
        ts_pre_process['train'] = dict_train

        if df_valid is not None:
            dict_valid = {}
            valid_X, valid_y, scaler_valid = class_data._pre_processed_data_pipeline(
                df_data=df_valid,
                dropnan=dropnan
            )
            # validation
            valid_X = valid_X.values.reshape(valid_X.shape[0], self.config['n_past'], self.config['n_inp_ft'])
            valid_y = valid_y.values.reshape(valid_y.shape[0], self.config['n_future'], self.config['n_out_ft'])
            if view:
                print(f'Valid -> X: {valid_X.shape} - y:{valid_y.shape}')
            dict_valid['X'], dict_valid['y'], dict_valid['scaler'] = valid_X, valid_y, scaler_valid
            ts_pre_process['valid'] = dict_valid
        if df_test is not None:
            dict_test = {}
            test_X, test_y, scaler_test = class_data._pre_processed_data_pipeline(
                df_data=df_test,
                dropnan=dropnan
            )
            # Testing
            test_X = test_X.values.reshape(test_X.shape[0], self.config['n_past'], self.config['n_inp_ft'])
            test_y = test_y.values.reshape(test_y.shape[0], self.config['n_future'], self.config['n_out_ft'])
            if view:
                print(f'Test -> X: {test_X.shape} - y:{test_y.shape}')
            dict_test['X'], dict_test['y'], dict_test['scaler'] = test_X, test_y, scaler_test
            ts_pre_process['test'] = dict_test
        return ts_pre_process