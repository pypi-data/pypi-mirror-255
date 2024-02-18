# -*- coding: utf-8 -*-
# @Time    : 24/03/2023
# @Author  : Ing. Jorge Lara
# @Email   : jlara@iee.unsj.edu.ar
# @File    : ------------
# @Software: PyCharm

import logging
import pandas as pd
import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error, mean_absolute_percentage_error, r2_score
from openpy_fxts.models.imputation.base_lib import init_class
from openpy_fxts.error_handling_logging import update_logg_file

log_py = logging.getLogger(__name__)


class Metrics:

    def add_dict_metrics(
            self,
            df_true,
            df_imp,
            dict_perf,
            method
    ):
        df_aux = pd.DataFrame()
        for x in range(df_true.shape[1]):
            y_true = np.reshape(np.array(df_true.iloc[:, x]), ((df_true.iloc[:, x].shape[0], 1)))
            y_imp = np.reshape(np.array(df_imp.iloc[:, x]), ((df_imp.iloc[:, x].shape[0], 1)))
            dict_metrics = self._metrics(y_true, y_imp)
            row_to_append = pd.DataFrame([dict(zip(list(dict_metrics.keys()), list(dict_metrics.values())))])
            df_aux = pd.concat([df_aux, row_to_append])
        df_aux.insert(0, 'Index', list(df_true.columns))
        df_aux.set_index('Index', inplace=True)
        dict_perf[method] = df_aux
        return dict_perf

    def _metrics(self, y_true, y_imp):
        metrics = dict()
        metrics['MAE'] = mean_absolute_error(y_true, y_imp)
        metrics['MSE'] = mean_squared_error(y_true, y_imp)
        metrics['MAPE'] = mean_absolute_percentage_error(y_true, y_imp)
        metrics['R2'] = r2_score(y_true, y_imp)
        return metrics


class Utils(init_class):
    def __init__(self, dataframe=None):
        super().__init__(dataframe)
        self.dataframe = dataframe

    def list_column_missing(self):
        data_NaN = pd.DataFrame(self.dataframe.isnull().sum(), columns=['number'])
        return list(data_NaN[data_NaN['number'] > 0].index)

    def check_missing(self):
        # summarize the number of rows with missing values for each column
        aux = self.dataframe.isnull().values.any()
        return aux

    def missing_values_table(self):
        # Total missing values
        mis_val = self.dataframe.isnull().sum()

        # Percentage of missing values
        mis_val_percent = 100 * self.dataframe.isnull().sum() / len(self.dataframe)

        # Make a table with the results
        mis_val_table = pd.concat([mis_val, mis_val_percent], axis=1)

        # Rename the columns
        mis_val_table_ren_columns = mis_val_table.rename(
            columns={0: 'Missing Values', 1: '% of Total Values'})

        # Sort the table by percentage of missing descending
        mis_val_table_ren_columns = mis_val_table_ren_columns[mis_val_table_ren_columns.iloc[:, 1] != 0].sort_values(
            '% of Total Values', ascending=False).round(1)

        # Print some summary information
        update_logg_file(
            "Your selected DataFrame has " + str(self.dataframe.shape[1]) + " columns.\n"
            "There are " + str(mis_val_table_ren_columns.shape[0]) +
            " columns that have missing values.", 0, log_py
        )

        # Return the dfframe with missing information
        return mis_val_table_ren_columns

    def total_days_range(self):
        print('Start date: ', self.dataframe.index.min())
        print('Final date: ', self.dataframe.index.max())
        print('Total number of Days: ', self.dataframe.index.max() - self.dataframe.index.min())

    def duplicate(self):
        pass


class ft_eng(init_class):

    def __init(self, dataframe):
        super().__init__(dataframe)
        self.dataframe = dataframe

    def add_datetime(self):
        self.dataframe['Year'] = self.dataframe.index.year
        self.dataframe['Month'] = self.dataframe.index.month
        self.dataframe['Day'] = self.dataframe.index.day
        self.dataframe['nDay'] = self.dataframe.index.weekday
        self.dataframe['Hour'] = self.dataframe.index.hour
        self.dataframe['Minute'] = self.dataframe.index.minute

    def add_seasons(self):
        self.dataframe.loc[
            ((self.dataframe["Month"] == 12) & (self.dataframe["Day"] >= 21)) | (self.dataframe["Month"] == 1) | (
                        self.dataframe["Month"] == 2) | (
                    (self.dataframe["Month"] == 3) & (self.dataframe["Day"] <= 20)), 'Season'] = 'Summer'
        self.dataframe.loc[
            ((self.dataframe["Month"] == 3) & (self.dataframe["Day"] >= 21)) | (self.dataframe["Month"] == 4) | (
                        self.dataframe["Month"] == 5) | (
                    (self.dataframe["Month"] == 6) & (self.dataframe["Day"] <= 20)), 'Season'] = 'Fall'
        self.dataframe.loc[
            ((self.dataframe["Month"] == 6) & (self.dataframe["Day"] >= 21)) | (self.dataframe["Month"] == 7) | (
                        self.dataframe["Month"] == 8) | (
                    (self.dataframe["Month"] == 9) & (self.dataframe["Day"] <= 20)), 'Season'] = 'Winter'
        self.dataframe.loc[
            ((self.dataframe["Month"] == 9) & (self.dataframe["Day"] >= 21)) | (self.dataframe["Month"] == 10) | (
                        self.dataframe["Month"] == 11) | (
                    (self.dataframe["Month"] == 12) & (self.dataframe["Day"] <= 20)), 'Season'] = 'Spring'

    def add_working_day(self):
        self.dataframe.loc[self.dataframe["nDay"] >= 5, 'Day type'] = 'non-working'
        self.dataframe.loc[(self.dataframe["nDay"] < 5), 'Day type'] = 'working'


class Preprocessing:

    def LabelEncoder(self, df):
        transform_dict = {}
        for col in df.iloc[:, :].select_dtypes(include=['object']).columns:
            cats = pd.Categorical(df[col]).categories
            d = {}
            for i, cat in enumerate(cats):
                d[cat] = i
            transform_dict[col] = d

        return df.replace(transform_dict), transform_dict

    def inverse_LabelEncoder(self, df, transform_dict):
        inverse_transform_dict = {}
        for col, d in transform_dict.items():
            inverse_transform_dict[col] = {v: k for k, v in d.items()}

        return df.replace(inverse_transform_dict)

    def index_column(self, df):
        dict = {}
        aux = 0
        for i in df.columns:
            dict[i] = aux
            aux += 1
        list_aux = list()
        for col in df.iloc[:, :].select_dtypes(include=['object']).columns:
            list_aux.append(col)
        list_index = list()
        for m in list_aux:
            list_index.append(dict[m])
        return list_index
