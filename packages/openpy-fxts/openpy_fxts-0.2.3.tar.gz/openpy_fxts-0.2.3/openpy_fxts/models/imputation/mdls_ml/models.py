# -*- coding: utf-8 -*-
# @Time    : 25/03/2023
# @Author  : Ing. Jorge Lara
# @Email   : jlara@iee.unsj.edu.ar
# @File    : ------------
# @Software: PyCharm

import pandas as pd
import numpy as np
import miceforest as mf
from sklearn.impute import KNNImputer
from xgbimputer import XGBImputer
from pyppca import ppca
from fancyimpute import SoftImpute, BiScaler
from openpy_fxts.models.imputation.base_lib import init_models

# import sys
# sys.modules['sklearn.neighbors.base'] = sklearn.neighbors._base
# from missingpy import MissForest

from openpy_fxts.models.imputation.utilities.Utils import Preprocessing, Metrics, Utils

prepro = Preprocessing()
metrics = Metrics()


class imp_ml(init_models):
    
    def __init__(
            self,
            df_miss: pd.DataFrame = None,
            df_true: pd.DataFrame = None
    ):
        super().__init__(df_miss, df_true)

    def miceforest(
            self, 
            n_iter: int = 5, 
            seed: int = 123
    ):
        list_aux = Utils(self.df_miss).list_column_missing()
        self.df_miss, transf = prepro.LabelEncoder(self.df_miss)
        kernel = mf.ImputationKernel(
            data=self.df_miss,
            save_all_iterations=True,
            random_state=seed)
        kernel.mice(n_iter, verbose=True)
        MiceForest = kernel.complete_data(dataset=0, inplace=False)
        MiceForest['datetime'] = self.df_miss.index
        MiceForest.set_index('datetime', inplace=True)
        MiceForest = prepro.inverse_LabelEncoder(MiceForest, transf)

        if self.df_true is None:
            return MiceForest
        else:
            dict_aux = dict()
            dict_aux = metrics.add_dict_metrics(self.df_true[list_aux], MiceForest[list_aux], dict_aux, 'mice_forest')
            return MiceForest, dict_aux['mice_forest']

    def knn(
            self,
            missing_values=np.nan,
            n_neighbors=5,
            weights="uniform",
            metric="nan_euclidean",
            copy=True,
            add_indicator=False,
            keep_empty_features=False

    ):
        list_aux = Utils(self.df_miss).list_column_missing()
        self.df_miss, transf = prepro.LabelEncoder(self.df_miss)
        model_knn = KNNImputer(
            missing_values=missing_values,
            n_neighbors=n_neighbors,
            weights=weights,
            metric=metric,
            copy=copy,
            add_indicator=add_indicator,
            keep_empty_features=keep_empty_features
        )  # KNN mdits
        knn_imp = model_knn.fit_transform(self.df_miss)
        knn_imp = pd.DataFrame(knn_imp, columns=self.df_miss.columns).round(1)
        knn_imp['datetime'] = self.df_miss.index
        knn_imp.set_index('datetime', inplace=True)

        if self.df_true is None:
            return knn_imp
        else:
            dict_aux = dict()
            dict_aux = metrics.add_dict_metrics(self.df_true[list_aux], knn_imp[list_aux], dict_aux, 'knn')
            return knn_imp, dict_aux['knn']

    def XGBImputer(
            self, 
    ):
        list_aux = Utils(self.df_miss).list_column_missing()
        model_XGBimp = XGBImputer(
            categorical_features_index=prepro.index_column(self.df_miss),
            replace_categorical_values_back=True
        )
        XGB_Imp = model_XGBimp.fit_transform(self.df_miss)
        XGB_Imp = pd.DataFrame(XGB_Imp, columns=self.df_miss.columns)
        XGB_Imp['datetime'] = self.df_miss.index
        XGB_Imp.set_index('datetime', inplace=True)

        if self.df_true is None:
            return XGB_Imp
        else:
            dict_aux = dict()
            dict_aux = metrics.add_dict_metrics(
                self.df_true[list_aux],
                XGB_Imp[list_aux],
                dict_aux,
                'XGB'
            )
            return XGB_Imp, dict_aux['XGB']

    def ppca(
            self, 
            d=50,
            dia=True
    ):
        list_aux = Utils(self.df_miss).list_column_missing()
        self.df_miss, transf = prepro.LabelEncoder(self.df_miss)
        X_miss = self.df_miss.to_numpy()
        C1, ss1, M1, X1, Ye1 = ppca(X_miss, d, dia)
        ppca_imp = pd.DataFrame(Ye1, columns=self.df_miss.columns)
        ppca_imp['datetime'] = self.df_miss.index
        ppca_imp.set_index('datetime', inplace=True)

        if self.df_true is None:
            return ppca_imp
        else:
            dict_aux = dict()
            dict_aux = metrics.add_dict_metrics(self.df_true[list_aux], ppca_imp[list_aux], dict_aux, 'PPCA')
            return ppca_imp, dict_aux['PPCA']

    def biscaler(
            self,
            shrinkage_value=None,
            convergence_threshold=0.001,
            max_iters=100,
            max_rank=None,
            n_power_iterations=1,
            init_fill_method="zero",
            min_value=None,
            max_value=None,
            normalizer=None,
            verbose=True,
            center_rows=True,
            center_columns=True,
            scale_rows=True,
            scale_columns=True,
            tolerance=0.001,
    ):

        list_aux = Utils(self.df_miss).list_column_missing()
        self.df_miss, transf = prepro.LabelEncoder(self.df_miss)

        # Instead of solving the nuclear norm objective directly, instead
        # induce sparsity using singular value thresholding
        softImpute = SoftImpute(
            shrinkage_value,
            convergence_threshold,
            max_iters,
            max_rank,
            n_power_iterations,
            init_fill_method,
            min_value,
            max_value,
            normalizer,
            verbose
        )

        # simultaneously normalizes the rows and columns of your observed datasets,
        # sometimes useful for low-rank mdits methods
        model_biscaler = BiScaler(
            center_rows,
            center_columns,
            scale_rows,
            scale_columns,
            min_value,
            max_value,
            max_iters,
            tolerance,
            verbose
        )
        X_miss = self.df_miss.to_numpy()
        X_miss_norm = model_biscaler.fit_transform(X_miss)
        X_fill_soft_norm = softImpute.fit_transform(X_miss_norm)
        biscaler_imp = model_biscaler.inverse_transform(X_fill_soft_norm)
        biscaler_imp = pd.DataFrame(biscaler_imp, columns=self.df_miss.columns)
        biscaler_imp['datetime'] = self.df_miss.index
        biscaler_imp.set_index('datetime', inplace=True)

        if self.df_true is None:
            return biscaler_imp
        else:
            dict_aux = dict()
            dict_aux = metrics.add_dict_metrics(
                self.df_true[list_aux],
                biscaler_imp[list_aux],
                dict_aux, 'model_biscaler'
            )
            return biscaler_imp, dict_aux['model_biscaler']

    def softimpute(
            self,
            shrinkage_value=None,
            convergence_threshold=0.001,
            max_iters=100,
            max_rank=None,
            n_power_iterations=1,
            init_fill_method="zero",
            min_value=None,
            max_value=None,
            normalizer=None,
            verbose=True
    ):
        list_aux = Utils(self.df_miss).list_column_missing()
        self.df_miss, transf = prepro.LabelEncoder(self.df_miss)

        # Instead of solving the nuclear norm objective directly, instead
        # induce sparsity using singular value thresholding
        model_softImpute = SoftImpute(
            shrinkage_value,
            convergence_threshold,
            max_iters,
            max_rank,
            n_power_iterations,
            init_fill_method,
            min_value,
            max_value,
            normalizer,
            verbose
        )
        X_miss = self.df_miss.to_numpy()
        soft_imp = model_softImpute.fit_transform(X_miss)
        soft_imp = pd.DataFrame(soft_imp, columns=self.df_miss.columns)
        soft_imp['datetime'] = self.df_miss.index
        soft_imp.set_index('datetime', inplace=True)

        if self.df_true is None:
            return soft_imp
        else:
            dict_aux = dict()
            dict_aux = metrics.add_dict_metrics(self.df_true[list_aux], soft_imp[list_aux], dict_aux, 'softimpute')
            return soft_imp, dict_aux['softimpute']
