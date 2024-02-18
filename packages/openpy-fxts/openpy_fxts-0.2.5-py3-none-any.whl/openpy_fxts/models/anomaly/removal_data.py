# -*- coding: utf-8 -*-
# @Time    : 05/09/2023
# @Author  : Ing. Jorge Lara
# @Email   : jlara@iee.unsj.edu.ar
# @File    : removal_data.py
# @Software: PyCharm

from statsmodels.tsa.seasonal import seasonal_decompose
import numpy as np


class seasonal:

    @staticmethod
    def nullify_outliers(col, period: int = None):
        """
        Remove outliers using seasonal decomposition
        :param col: (pd.Series) df to remove outliers for
        :return: (pd.Series) df with linearly interpolated values
        """
        #n_nan = col.isna().sum()
        decomp = seasonal_decompose(col, model='additive', period=period)
        resid = np.array(decomp.resid)

        # na fill outliers
        per_25, per_75 = np.percentile(resid[~np.isnan(resid)], [25, 75])
        upper = per_75 + (per_75 - per_25) * 1.5
        lower = per_25 - (per_75 - per_25) * 1.5
        col.iloc[np.argwhere((resid > upper) | (resid < lower)).flatten()] = np.nan

        return col


