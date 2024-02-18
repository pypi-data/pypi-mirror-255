# -*- coding: utf-8 -*-
# @Time    : 24/03/2023
# @Author  : Ing. Jorge Lara
# @Email   : jlara@iee.unsj.edu.ar
# @File    : ------------
# @Software: PyCharm

import logging

import pandas as pd

from openpy_fxts.datasets.test_data.load_examples import _sample_test
from .generate_missing_data.MCAR_MAR_MNAR_Pattern import generate_missing_data

log_py = logging.getLogger(__name__)


def hpc_dataframe(
        data_name: str = 'HPC',
        date_init: str = '2008-11-26 00:00:00',
        date_end: str = None
):
    ex = _sample_test()
    data = ex._example(data_name, date_init, date_end)
    return data


class dataset_examples:

    def generate_missing_data(
            self,
            X: pd.DataFrame = None,
            p_miss: float = 0.40,
            mecha: str = "MCAR",
            opt=None,
            p_obs=None,
            q=None,
            seed: int = 0
    ):
        """
        Generate missing values for specifics missing-datasets mechanism and proportion of missing values.

        Parameters
        ----------
        X : torch.DoubleTensor or np.ndarray, shape (n, d)
            Data for which missing values will be simulated.
            If a numpy array is provided, it will be converted to a pytorch tensor.
        p_miss : float
            Proportion of missing values to generate for variables which will have missing values.
        mecha : str,
                Indicates the missing-datasets mechanism to be used. "MCAR" by default, "MAR", "MNAR" or "MNARsmask"
        opt: str,
                For mecha = "MNAR", it indicates how the missing-datasets mechanism is generated: using a logistic regression ("logistic"), quantile censorship ("quantile") or logistic regression for generating a self-masked MNAR mechanism ("selfmasked").
        p_obs : float
                If mecha = "MAR", or mecha = "MNAR" with opt = "logistic" or "quanti", proportion of variables with *no* missing values that will be used for the logistic masking model.
        q : float
            If mecha = "MNAR" and opt = "quanti", quantile level at which the cuts should occur.

        Returns
        ----------
        A dictionnary containing:
        'X_init': the initial datasets matrix.
        'X_incomp': the datasets with the generated missing values.
        'mask': a matrix indexing the generated missing values.s
        """
        miss_data = generate_missing_data(seed)
        df_data_miss = miss_data.produce_NaN(X.to_numpy(), p_miss, mecha, opt, p_obs, q)
        df_data_miss = pd.DataFrame(df_data_miss['X_incomp'], columns=X.columns)
        df_data_miss['datetime'] = X.index
        df_data_miss.set_index('datetime', inplace=True)

        return df_data_miss

    def data_preprocessing(self):
        pass

    def visualization_missing_data(self):
        pass

    def Simple_Imputation(self):
        pass

    def ML_Imputation(self):
        pass

    def DL_Imputation(self):
        pass

    def Forescating_Imputation(self):
        pass
