# -*- coding: utf-8 -*-
# @Time    : 25/03/2023
# @Author  : Ing. Jorge Lara
# @Email   : jlara@iee.unsj.edu.ar
# @File    : ------------
# @Software: PyCharm

import numpy as np
import pandas as pd
import sklearn.compose
import sklearn.impute
import sklearn.preprocessing

from sklearn.linear_model import BayesianRidge
from fancyimpute import IterativeSVD
from openpy_fxts.models.imputation.base_lib import init_models


from openpy_fxts.models.imputation.utilities.Utils import Preprocessing, Metrics, Utils

prepro = Preprocessing()
metrics = Metrics()


class iterative(init_models):

    def __init__(self, df_miss: pd.DataFrame = None, df_true: pd.DataFrame = None):
        super().__init__(df_miss, df_true)
        self.df_miss = df_miss
        self.df_true = df_true

    def MICE(
            self,
            estimator=BayesianRidge(),
            missing_values=np.nan,
            sample_posterior=False,
            max_iter=10,
            tol=1e-3,
            n_nearest_features=None,
            initial_strategy="mean",
            imputation_order="ascending",
            skip_complete=False,
            min_value=-np.inf,
            max_value=np.inf,
            verbose=0,
            random_state=None,
            add_indicator=False,
            keep_empty_features=False
    ):
        list_aux = Utils(self.df_miss).list_column_missing()
        df_miss, transf = prepro.LabelEncoder(self.df_miss)

        model_mice = sklearn.impute.IterativeImputer(
            estimator=estimator,
            missing_values=missing_values,
            sample_posterior=sample_posterior,
            max_iter=max_iter,
            tol=tol,
            n_nearest_features=n_nearest_features,
            initial_strategy=initial_strategy,
            imputation_order=imputation_order,
            skip_complete=skip_complete,
            min_value=min_value,
            max_value=max_value,
            verbose=verbose,
            random_state=random_state,
            add_indicator=add_indicator,
            keep_empty_features=keep_empty_features
        )
        df_mice = df_miss.copy(deep=True)
        df_mice.iloc[:, :] = model_mice.fit_transform(df_mice).round()
        if self.df_true is None:
            return df_mice
        else:
            dict_aux = dict()
            dict_aux = metrics.add_dict_metrics(self.df_true[list_aux], df_mice[list_aux], dict_aux, 'mice_forest')
            return df_mice, dict_aux['mice_forest']

    def iter_SVD(
            self,
            rank=10,
            convergence_threshold=0.00001,
            max_iters=200,
            gradual_rank_increase=True,
            svd_algorithm="arpack",
            init_fill_method="zero",
            min_value=None,
            max_value=None,
            verbose=True
    ):
        list_aux = Utils(self.df_miss).list_column_missing()
        self.df_miss, transf = prepro.LabelEncoder(self.df_miss)
        model_svd = IterativeSVD(
            rank,
            convergence_threshold,
            max_iters,
            gradual_rank_increase,
            svd_algorithm,
            init_fill_method,
            min_value,
            max_value,
            verbose
        )

        X_miss = self.df_miss.to_numpy()
        svd_imp = model_svd.fit_transform(X_miss)
        svd_imp = pd.DataFrame(svd_imp, columns=self.df_miss.columns)
        svd_imp['datetime'] = self.df_miss.index
        svd_imp.set_index('datetime', inplace=True)

        if self.df_true is None:
            return svd_imp
        else:
            dict_aux = dict()
            dict_aux = metrics.add_dict_metrics(self.df_true[list_aux], svd_imp[list_aux], dict_aux, 'IterativeSVD')
            return svd_imp, dict_aux['IterativeSVD']
