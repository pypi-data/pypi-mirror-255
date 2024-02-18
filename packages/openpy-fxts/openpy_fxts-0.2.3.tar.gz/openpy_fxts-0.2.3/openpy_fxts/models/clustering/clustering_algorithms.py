# -*- coding: utf-8 -*-
# @Time    : 04/09/2023
# @Author  : Ing. Jorge Lara
# @Email   : jlara@iee.unsj.edu.ar
# @File    : clustering_algorithms.py
# @Software: PyCharm

import warnings
import pandas as pd
import inspect

warnings.simplefilter(action='ignore', category=FutureWarning)
pd.options.mode.chained_assignment = None  # default='warn'

import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.cluster import KMeans, MiniBatchKMeans, MeanShift, DBSCAN, Birch, OPTICS, AffinityPropagation, \
    AgglomerativeClustering, SpectralClustering
from yellowbrick.cluster import KElbowVisualizer
from openpy_fxts.models.anomaly.removal_data import seasonal
import math
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
import os

from tslearn.clustering import TimeSeriesKMeans
from tslearn.barycenters import euclidean_barycenter, dtw_barycenter_averaging, dtw_barycenter_averaging_subgradient, \
    softdtw_barycenter

from sklearn.preprocessing import StandardScaler

from tslearn.piecewise import PiecewiseAggregateApproximation
from tslearn.piecewise import SymbolicAggregateApproximation
from tslearn.piecewise import OneD_SymbolicAggregateApproximation

from sklearn.metrics import silhouette_score, davies_bouldin_score, calinski_harabasz_score
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score, mean_absolute_percentage_error
from sklearn.manifold import TSNE, MDS
from sklearn.cluster import KMeans, MiniBatchKMeans, DBSCAN, Birch, OPTICS, AffinityPropagation, \
    AgglomerativeClustering, SpectralClustering
from sklearn.cluster import MeanShift, estimate_bandwidth
from sklearn.mixture import GaussianMixture
from minisom import MiniSom

from scipy import stats

from scipy.cluster.hierarchy import dendrogram
from tqdm.autonotebook import tqdm
from .data_preprocessing import moving_window_mean

from sklearn.neighbors import NearestNeighbors

clu_no_centroid = ['DBSCAN', 'Birch', 'GaussianMixture', 'OPTICS', 'Agglomerative', 'Spectral']
model_with_eps = ['DBSCAN', 'OPTICS']


def set_tittle_cluster(key, gamma):
    if key == 'centroid':
        return 'Centroid'
    if key == 'mean':
        return 'Mean'
    if key == 'euclidean':
        return "Euclidean"
    if key == 'dba_vectorized':
        return "DBA (vectorized version of Petitjean's EM)"
    if key == 'dba_subgradient':
        return "DBA (subgradient descent approach)"
    if key == 'soft_dtw':
        return f"Soft-DTW barycenter ($\gamma$={gamma})"


def set_tittle_cluster(case: bool = None, gamma=None):
    if case == 'centroid':
        return 'Centroid'
    if case == 'mean':
        return 'Mean'
    if case == 'euclidean':
        return "Euclidean"
    if case == 'dba_vectorized':
        return "DBA (vectorized \nversion of Petitjean's EM)"
    if case == 'dba_subgradient':
        return "DBA (subgradient \ndescent approach)"
    if case == 'soft_dtw':
        return f"Soft-DTW barycenter\n ($\gamma$={gamma})"


class clustering_ts:

    def __init__(
            self,
            users=None,
            model: str = 'KMeans',
            metric: str = 'dtw',
            type_dr: str = None,
            cdata: str = None,
            reduced: bool = False,
            n_components: int = 2,
            seed: int = 23,
            df_sce: pd.DataFrame = None,
            dict_sce: dict = None,
            clu_lbl=None,
            n_jobs: int = -1,
            max_iter: int = 10
    ):
        if users is None:
            users = df_sce.columns[:-11]
        self.model = model
        self.users = users
        self.metric = metric
        self.type_dr = type_dr
        self.cdata = cdata
        self.reduced = reduced
        self.n_components = n_components
        self.seed = seed
        self.df_sce = df_sce
        self.dict_sce = dict_sce
        self.clu_lbl = clu_lbl
        self.n_jobs = -1
        self.max_iter = 10

    def reshape_to_clu_atypical_mean(
            self,
            plot_user: bool = False,
            id_user: str = None,
            op: int = 1
    ):
        dict_sce = dict()
        df_users_mean = pd.DataFrame()
        if self.reduced is False and self.clu_lbl is None:
            for k in self.users:
                df_aux = self.get_df_aux(k)
                dict_sce[k] = df_aux
            return dict_sce
        if self.reduced and self.clu_lbl is None:
            for k in self.users:
                df_aux = self.get_df_aux(k)
                dict_sce[k] = df_aux
                user_mean = self.outlier_removal(df_aux, df_aux.columns, op, k)
                df_users_mean = pd.concat([df_users_mean, user_mean], axis=0)
            df_users_mean.interpolate(inplace=True, axis=1)
            dict_sce['means'] = df_users_mean
            return dict_sce
        if self.reduced and self.clu_lbl is not None:
            for k in self.users:
                df_aux = self.get_df_aux(k)
                cols = df_aux.columns
                df_aux = pd.merge(df_aux, self.clu_lbl, left_index=True, right_index=True)
                df_aux.rename(columns={"cluster": "clu_1"}, inplace=True)
                dict_sce[k] = df_aux
                for x in self.clu_lbl.unique():
                    df_clu_aux = self.outlier_removal(df_aux[df_aux.clu_1 == x], cols, op, k)
                    df_clu_aux.loc[:, 'clu_1'] = x
                    df_users_mean = pd.concat([df_users_mean, df_clu_aux], axis=0)
            dict_sce['means'] = df_users_mean
            return dict_sce
        if self.reduced is False and self.clu_lbl is not None:
            for k in self.users:
                df_aux = self.get_df_aux(k)
                df_aux = pd.merge(df_aux, self.clu_lbl, left_index=True, right_index=True)
                df_aux.rename(columns={"cluster": "clu_1"}, inplace=True)
                dict_sce[k] = df_aux
            return dict_sce

        df_users_mean_1, df_users_mean_2 = pd.DataFrame(), pd.DataFrame()
        for k in self.users:
            df_aux = self.get_df_aux(k)
            if self.clu_lbl is not None:
                df_aux = pd.merge(df_aux, self.clu_lbl, left_index=True, right_index=True)
                # df_aux.loc[:, 'user'] = k
                df_aux.rename(columns={"cluster": "clu_1"}, inplace=True)
            dict_sce[k] = df_aux
            if self.reduced and self.clu_lbl is not None:
                cols = df_aux.columns[:-1]
                for x in self.clu_lbl.unique():
                    df_clu_aux = self.outlier_removal(df_aux[df_aux.clu_1 == x], cols, op, k)
                    df_clu_aux.loc[:, 'clu_1'] = x
                    df_users_red_2 = pd.concat([df_users_mean_2, df_clu_aux], axis=0)
            else:
                if self.clu_lbl is not None:
                    cols = df_aux.columns[:-1]
                else:
                    cols = df_aux.columns
                user_mean = self.outlier_removal(df_aux, cols, op, k)
                df_users_mean_1 = pd.concat([df_users_mean_1, user_mean], axis=0)
        df_users_mean_1.interpolate(inplace=True, axis=1)
        dict_sce['means'] = df_users_mean_1

        if self.reduced and self.clu_lbl is not None:
            dict_sce['means'] = df_users_mean_2

        if plot_user:
            if id_user is None:
                cols = 3
                rows = round((len(dict_sce.keys()) - 1) / cols) + 1
                fig_1, ax = plt.subplots(nrows=rows, ncols=cols, sharex=True)
                n, m = 0, 0
                for key, value in dict_sce.items():
                    if key == 'means':
                        pass
                    else:
                        ax[n, m].plot(dict_sce[key].T, "k-", alpha=0.2)
                        ax[n, m].plot(dict_sce['means'].loc[key].T, c='r')
                        ax[n, m].set_title(key)
                        m += 1
                        if m == cols:
                            m = 0
                            n += 1
                plt.show()
            else:
                plt.plot(dict_sce[id_user].T, "k-", alpha=0.2)
                plt.plot(dict_sce['means'].loc[id_user].T, c='r')
                plt.title(id_user)
                plt.show()

        return dict_sce

    def get_df_aux(self, user):
        data = self.df_sce.loc[:, [user, 'count_day', 'date']].copy()
        aux = []
        for i in data['count_day'].unique():
            aux.append(data[data['count_day'] == i].shape[0])
        n_meas = max(aux)
        data = data.reset_index()
        data[data.columns[0]] = data[data.columns[0]].apply(lambda x: x.strftime('%H:%M'))
        data.set_index(data.columns[0], inplace=True)
        day_aux = list(data.count_day.value_counts()[data.count_day.value_counts() == n_meas].index)
        data = data[data.count_day.isin(day_aux)]
        data.reset_index(inplace=True)
        data.drop(columns=['count_day'], inplace=True)
        df_aux = pd.pivot(
            data,
            index=['date'],
            columns=['index']
        )
        df_aux.columns = ['_'.join(col) for col in df_aux.columns.values]
        df_aux.columns = [item.replace(f'{user}_', "") for item in df_aux.columns]
        return df_aux

    def outlier_removal(self, df_aux, cols, op=1, user=None):
        data_graf = []
        vector_Prom = []
        aux = 0
        for i in cols:
            data = df_aux[i]
            size = len(data)  # determinar la longitud de los datos
            if size != 0:
                if op == 1:
                    # print(k, i)
                    Q1 = data.quantile(0.25)
                    Q3 = data.quantile(0.75)
                    IQR = Q3 - Q1
                    lower_lim = Q1 - 1.5 * IQR
                    upper_lim = Q3 + 1.5 * IQR
                    outliers_low = (data < lower_lim)
                    outliers_up = (data > upper_lim)
                    data[outliers_low] = lower_lim
                    data[outliers_up] = upper_lim
                if op == 2:
                    z_critical = stats.norm.ppf(q=0.999)
                    mean = data.mean()  # determina la media.
                    std = data.std()  # Get the population standard deviation
                    margin_of_error = z_critical * (std / math.sqrt(size))  # margen de error
                    confidence_interval = (mean - margin_of_error, mean + margin_of_error)
                    int_min = mean - margin_of_error
                    int_max = mean + margin_of_error
                    data = data[(data >= int_min)]  # filtrar obteniendo los valores de mayores al min
                    data = data[(data <= int_max)]  # filtrar obteniendo los valores de menores al min

            data_graf.append(data)
            Promedio = data_graf[aux].mean()
            vector_Prom.append(Promedio)
            aux += 1

        user_mean = pd.DataFrame(vector_Prom, index=cols, columns=[user]).T
        user_mean.interpolate(inplace=True, axis=1)
        return user_mean

    def transformer_dataset(
            self,
            model: str = None,  # 'PAA', 'SAX', '1d_SAX'
            n_paa_segments=5,
            n_sax_symbols=4,
            n_sax_symbols_avg=4,
            n_sax_symbols_slope=4
    ):

        prepo_ts = self.reshape_to_clu_atypical_mean()
        dict_scaler = self._scaler_data(prepo_ts)
        if dict_scaler['dataset'].isnull().sum().sum() > 0:
            dict_scaler['dataset'].ffill(inplace=True)

        # PAA transform (and inverse transform) of the data
        paa = PiecewiseAggregateApproximation(n_segments=n_paa_segments)
        paa_dataset_inv = paa.inverse_transform(paa.fit_transform(dict_scaler['dataset']))

        # SAX transform
        sax = SymbolicAggregateApproximation(n_segments=n_paa_segments, alphabet_size_avg=n_sax_symbols)
        sax_dataset_inv = sax.inverse_transform(sax.fit_transform(dict_scaler['dataset']))
        # 1d-SAX transform
        one_d_sax = OneD_SymbolicAggregateApproximation(
            n_segments=n_paa_segments,
            alphabet_size_avg=n_sax_symbols_avg,
            alphabet_size_slope=n_sax_symbols_slope)
        transformed_data = one_d_sax.fit_transform(dict_scaler['dataset'])
        one_d_sax_dataset_inv = one_d_sax.inverse_transform(transformed_data)

        i = 0
        plt.figure()
        plt.subplot(2, 2, 1)  # First, raw time series
        plt.plot(dict_scaler['dataset'].iloc[i].ravel(), "b-")
        plt.title("Raw time series")

        plt.subplot(2, 2, 2)  # Second, PAA
        plt.plot(dict_scaler['dataset'].iloc[i].ravel(), "b-", alpha=0.4)
        plt.plot(paa_dataset_inv[i].ravel(), "b-")
        plt.title("PAA")

        plt.subplot(2, 2, 3)  # Then SAX
        plt.plot(dict_scaler['dataset'].iloc[i].ravel(), "b-", alpha=0.4)
        plt.plot(sax_dataset_inv[i].ravel(), "b-")
        plt.title("SAX, %d symbols" % n_sax_symbols)

        plt.subplot(2, 2, 4)  # Finally, 1d-SAX
        plt.plot(dict_scaler['dataset'].iloc[i].ravel(), "b-", alpha=0.4)
        plt.plot(one_d_sax_dataset_inv[i].ravel(), "b-")
        plt.title(
            "1d-SAX, %d symbols""(%dx%d)" % (
                n_sax_symbols_avg * n_sax_symbols_slope, n_sax_symbols_avg, n_sax_symbols_slope
            )
        )
        plt.tight_layout()
        plt.show()
        # Scaler data
        dict_scaler = self._scaler_data(prepo_ts)
        if dict_scaler['dataset'].isnull().sum().sum() > 0:
            dict_scaler['dataset'].ffill(inplace=True)
        return dict_scaler

    def prepare_data_to_clu(
            self,
            atypical: bool = True
    ):
        data = self.df_sce.copy()
        aux = []
        for i in data['count_day'].unique():
            aux.append(data[data['count_day'] == i].shape[0])
        n_meas = max(aux)
        data = data.reset_index()
        data[data.columns[0]] = data[data.columns[0]].apply(lambda x: x.strftime('%H:%M'))
        data.set_index(data.columns[0], inplace=True)
        day_aux = list(data.count_day.value_counts()[data.count_day.value_counts() == n_meas].index)
        data = data[data.count_day.isin(day_aux)]
        if atypical:
            if type(self.users) == str:
                self.users = self.users.split()
            # remove atypical datasets
            for col in self.users:
                Q1 = data.loc[:, col].quantile(0.25)
                Q3 = data.loc[:, col].quantile(0.75)
                IQR = Q3 - Q1
                lower_lim = Q1 - 1.5 * IQR
                upper_lim = Q3 + 1.5 * IQR
                outliers_low = (data.loc[:, col] < lower_lim)
                outliers_up = (data.loc[:, col] > upper_lim)
                data.loc[:, col][(outliers_low | outliers_up)] = np.nan
                '''
                data.loc[:, col] = data.loc[:, col].apply(
                    lambda x: seasonal.nullify_outliers(x, period=n_meas),
                    axis='index'
                )
                '''
                if data[col].isna().sum().sum() > 0:
                    data[col].ffill(inplace=True)
        data.reset_index(inplace=True)
        # data['user'] = data.columns[1]
        sce_days = dict()
        for user in self.users:
            sce_days[user] = pd.pivot(
                data,
                values=user,
                index=['date'],
                columns=data.columns[0]
            )
        return sce_days

    def _scaler_data(self, dict_data, label=None):
        dict_scaler = {}
        if self.reduced and self.clu_lbl is None:
            df_scaler = dict_data['means']
            user_aux = list(dict_data['means'].index)
            cols = df_scaler.columns
        if self.reduced is False and self.clu_lbl is None:
            df_scaler = pd.DataFrame()
            user_aux = []
            for user, df_data in dict_data.items():
                if user != 'means':
                    if self.clu_lbl is not None:
                        cols = df_data.columns[:-1]
                        df_data = df_data[df_data.clu_1 == label].iloc[:, :len(cols)]
                    else:
                        cols = df_data.columns
                    df_scaler = pd.concat([df_scaler, df_data], axis=0)
                    user_aux += [user] * df_data.shape[0]
        if self.reduced and self.clu_lbl is not None:
            df_scaler = dict_data['means']
            cols = df_scaler.columns[:-1]
            df_scaler = df_scaler[df_scaler.clu_1 == label].iloc[:, :len(cols)]
            user_aux = list(df_scaler.index)
        if self.reduced is False and self.clu_lbl is not None:
            df_scaler = pd.DataFrame()
            user_aux = []
            for user, df_data in dict_data.items():
                if user != 'means':
                    if self.clu_lbl is not None:
                        cols = df_data.columns[:-1]
                        df_data = df_data[df_data.clu_1 == label].iloc[:, :len(cols)]
                    else:
                        cols = df_data.columns
                    df_scaler = pd.concat([df_scaler, df_data], axis=0)
                    user_aux += [user] * df_data.shape[0]
        scalars = {}
        for i in cols:
            scaler = MinMaxScaler(feature_range=(0, 1))
            s_s = scaler.fit_transform(df_scaler[i].values.reshape(-1, 1))
            s_s = np.reshape(s_s, len(s_s))
            scalars['scaler_' + i] = scaler
            df_scaler[i] = s_s
        dict_scaler['dataset'] = df_scaler
        dict_scaler['scaler'] = scalars
        dict_scaler['user'] = user_aux
        return dict_scaler

        if self.reduced:
            df_scaler = dict_data['means']
            user_aux = list(dict_data['means'].index)
        else:
            df_scaler = pd.DataFrame()
            user_aux = []
            for user, df_data in dict_data.items():
                if user != 'means':
                    if self.clu_lbl is not None:
                        cols = df_data.columns[:-1]
                        df_data = df_data[df_data.clu_1 == label].iloc[:, :len(cols)]
                    else:
                        cols = df_data.columns
                    df_scaler = pd.concat([df_scaler, df_data], axis=0)
                    user_aux += [user] * df_data.shape[0]
        scalars = {}
        for i in cols:
            scaler = MinMaxScaler(feature_range=(0, 1))
            s_s = scaler.fit_transform(df_scaler[i].values.reshape(-1, 1))
            s_s = np.reshape(s_s, len(s_s))
            scalars['scaler_' + i] = scaler
            df_scaler[i] = s_s
        dict_scaler['dataset'] = df_scaler
        dict_scaler['scaler'] = scalars
        dict_scaler['user'] = user_aux
        return dict_scaler

    def _inverse_transform(
            self,
            yhat,
            dict_scaler,
    ):
        for index, i in enumerate(dict_scaler['dataset'].columns):
            scaler = dict_scaler['scaler']['scaler_' + i]
            yhat[index, :] = scaler.inverse_transform(yhat[index, :].reshape(-1, 1)).reshape(yhat.shape[1], )
        return yhat

    def scaler_data(self, data):
        from sklearn.preprocessing import StandardScaler, MinMaxScaler
        scaler = MinMaxScaler()
        dict_scaler = {
            'dataset': scaler.fit_transform(data.T).T,
            'scaler': scaler
        }
        return dict_scaler

    def get_centroids_for_clustering(
            self,
            labels_clu,
            max_iter: int = 10,
            tol: float = 1e-3,
            gamma: float = 1.0,
            verbose: bool = False,
            all_barycenter: bool = False,
            mean: bool = None,
            euclidean: bool = None,
            dba_vec: bool = None,
            dba_sub: bool = None,
            soft_dtw: bool = None,
            all_plots: bool = False,
            plot_n_cluster: int = 0,
            plt_barycenters: bool = True,
            plt_bar_cluster: bool = None,
            plt_bar_summary: bool = None,
            plt_clusters: bool = None,
            view_clusters: bool = None,
            pct_clusters: bool = None
    ):

        if all_barycenter:
            mean, euclidean, dba_vec, dba_sub, soft_dtw = True, True, True, True, True
        if plt_barycenters:
            plt_bar_cluster, plt_bar_summary, = True, True
        if plt_clusters:
            view_clusters, pct_clusters = True, True
        dict_scaler = self.transformer_dataset()
        dict_scaler['dataset'].loc[:, 'cluster'] = labels_clu
        dataset = dict_scaler['dataset']
        ts_clustered = [0] * len(labels_clu.unique())
        for i in labels_clu.unique():
            ts_clustered[i] = np.array(dataset[dataset.cluster == i].iloc[:, :-1])
        dataset.drop(columns=['cluster'], inplace=True)
        dict_bar = {
            'dataset': dataset,
            'clusters': [x.T for x in ts_clustered]
        }
        # Find barycentre's
        bar = barycenter(ts_clustered, max_iter, tol, verbose, gamma)
        if mean:
            dict_bar['mean'] = bar.mean()
        if euclidean:
            dict_bar['euclidean'] = bar.euclidean()
        if dba_vec:
            dict_bar['dba_vectorized'] = bar.dba_vectorized()
        if dba_sub:
            dict_bar['dba_subgradient'] = bar.dba_subgradient()
        if soft_dtw:
            dict_bar['soft_dtw'] = bar.soft_dtw()

        for key, values_scales in dict_bar.items():
            if key == 'dataset':
                dict_bar['dataset'] = pd.DataFrame(
                    self._inverse_transform(values_scales.values.T, dict_scaler).T,
                    columns=dict_scaler['dataset'].columns,
                    index=dict_scaler['dataset'].index
                )
            else:
                for x in values_scales:
                    self._inverse_transform(x, dict_scaler)

        n_clusters = len(labels_clu.unique())
        if plt_bar_summary:
            self.plots.all_barycenter(True, False, plot_n_cluster, gamma, dict_bar)
        if plt_bar_cluster:
            self.plots.all_barycenter(False, True, plot_n_cluster, gamma, dict_bar)
        if view_clusters:
            self.view_cluster(n_clusters, dict_bar, gamma)
        if pct_clusters:
            self.pct_clusters(labels_clu)
        dict_bar['dataset'].loc[:, 'cluster'] = labels_clu
        dict_bar['dataset']['user'] = dict_scaler['user']
        return dict_bar

    def train_clu_model(
            self,
            n_clusters: int = 3,
            n_components: int = 3,
            quantile: float = 0.13,
            n_samples: int = None,
            eps: float = 1.1,
            min_samples=None,
            threshold: float = 1.5,
            branching_factor: int = 50,
            damping: float = 0.90,
            sigma: float = 0.5,
            lr: float = 0.5,
            num_iteration: int = 500,
            points_2d: bool = False,
            view_clu: bool = False
    ):

        parameters = {
            'type_dr': self.type_dr,
            'model': self.model,
            'metric': self.metric,
            'n_jobs': self.n_jobs,
            'max_iter': self.max_iter,
            'seed': self.seed,
            'n_clusters': n_clusters,
            'n_components': n_components,
            'quantile': quantile,
            'n_samples': n_samples,
            'eps': eps,
            'min_samples': min_samples,
            'threshold': threshold,
            'branching_factor': branching_factor,
            'damping': damping,
            'sigma': sigma,
            'lr': lr,
            'num_iteration': num_iteration,
            'points_2d': points_2d,
            'view_clu': view_clu
        }
        clu = _clu_model(parameters)
        if self.reduced is False and self.clu_lbl is None:
            dict_sce = self.reshape_to_clu_atypical_mean()
            dict_scaler = self._scaler_data(dict_sce)
            ts_scaler = dict_scaler['dataset'].values
            # Dimensional reduction
            if self.type_dr is not None:
                data = self.dimensionality_reduction().fit_transform(ts_scaler)
            else:
                data = ts_scaler
            return clu.check_model(data, ts_scaler, dict_scaler)
        if self.reduced and self.clu_lbl is None:
            dict_sce = self.reshape_to_clu_atypical_mean()
            dict_scaler = self._scaler_data(dict_sce)
            ts_scaler = dict_scaler['dataset'].values
            # Dimensional reduction
            if self.type_dr is not None:
                data = self.dimensionality_reduction().fit_transform(ts_scaler)
            else:
                data = ts_scaler
            return clu.check_model(data, ts_scaler, dict_scaler)
        if self.reduced and self.clu_lbl is not None:
            models_with_labels = {}
            dict_sce = self.reshape_to_clu_atypical_mean()
            for i in self.clu_lbl.unique():
                dict_scaler = self._scaler_data(dict_sce, i)
                ts_scaler = dict_scaler['dataset'].values
                if self.type_dr is not None:
                    data = self.dimensionality_reduction().fit_transform(ts_scaler)
                else:
                    data = ts_scaler
                models_with_labels[i] = clu.check_model(data, ts_scaler, dict_scaler)
            return models_with_labels
        if self.reduced is False and self.clu_lbl is not None:
            models_with_labels = {}
            dict_sce = self.reshape_to_clu_atypical_mean()
            for i in self.clu_lbl.unique():
                dict_scaler = self._scaler_data(dict_sce, i)
                ts_scaler = dict_scaler['dataset'].values
                if self.type_dr is not None:
                    data = self.dimensionality_reduction().fit_transform(ts_scaler)
                else:
                    data = ts_scaler
                models_with_labels[i] = clu.check_model(data, ts_scaler, dict_scaler)
            return models_with_labels

        if self.clu_lbl is not None and self.reduced:
            models_with_labels = {}
            dict_sce = self.reshape_to_clu_atypical_mean()
            for i in self.clu_lbl.unique():
                dict_scaler = self._scaler_data(dict_sce, i)
                ts_scaler = dict_scaler['dataset'].values
                if self.type_dr is not None:
                    data = self.dimensionality_reduction().fit_transform(ts_scaler)
                else:
                    data = ts_scaler
                models_with_labels[i] = clu.check_model(data, ts_scaler, dict_scaler)
            return models_with_labels
        if self.clu_lbl is not None:
            models_with_labels = {}
            dict_sce = self.reshape_to_clu_atypical_mean()
            for i in self.clu_lbl.unique():
                dict_scaler = self._scaler_data(dict_sce, i)
                ts_scaler = dict_scaler['dataset'].values
                if self.type_dr is not None:
                    data = self.dimensionality_reduction().fit_transform(ts_scaler)
                else:
                    data = ts_scaler
                models_with_labels[i] = clu.check_model(data, ts_scaler, dict_scaler)
            return models_with_labels
        else:
            dict_sce = self.reshape_to_clu_atypical_mean()
            dict_scaler = self._scaler_data(dict_sce)
            ts_scaler = dict_scaler['dataset'].values
            # Dimensional reduction
            if self.type_dr is not None:
                data = self.dimensionality_reduction().fit_transform(ts_scaler)
            else:
                data = ts_scaler
            return clu.check_model(data, ts_scaler, dict_scaler)

    def cluster_ts_extraction(
            self,
            n_clusters: int = 3,
            plot_n_cluster: int = 0,
            max_iter: int = 10,
            tol: float = 1e-3,
            gamma: float = 1.0,
            verbose: bool = False,
            all_barycenters: bool = False,
            centroid: bool = None,
            mean: bool = None,
            euclidean: bool = None,
            dba_vec: bool = None,
            dba_sub: bool = None,
            soft_dtw: bool = None,
            plt_barycenters: bool = None,
            plt_all_barycenters: bool = None,
            summary_barycenters: bool = None,
            plt_clu: bool = None,
            view_clusters: bool = None,
            pct_clusters: bool = None
    ):
        bool_bar = {
            'centroid': centroid,
            'mean': mean,
            'euclidean': euclidean,
            'dba_vec': dba_vec,
            'dba_sub': dba_sub,
            'soft_dtw': soft_dtw
        }
        bool_plots = {
            'plot_n_cluster': plot_n_cluster,
            'plt_barycenters': plt_barycenters,
            'plt_all_barycenters': plt_all_barycenters,
            'summary_barycenters': summary_barycenters,
            'plt_clu': plt_clu,
            'view_clusters': view_clusters,
            'pct_clusters': pct_clusters
        }
        if all_barycenters:
            bool_bar['centroid'] = True
            bool_bar['mean'] = False
            bool_bar['euclidean'] = True
            bool_bar['dba_vec'] = True
            bool_bar['dba_sub'] = True
            bool_bar['soft_dtw'] = True
        if plt_barycenters:
            bool_plots['plt_all_barycenters'], bool_plots['summary_barycenters'], = True, True
        if plt_clu:
            bool_plots['view_clusters'], bool_plots['pct_clusters'] = True, True
        train_model = self.train_clu_model(n_clusters=n_clusters)
        if self.reduced is False and self.clu_lbl is None:
            return self.dict_barycenter(
                train_model, bool_bar, bool_plots, n_clusters, max_iter, tol, verbose, gamma
            )
        if self.reduced and self.clu_lbl is None:
            return self.dict_barycenter(
                train_model, bool_bar, bool_plots, n_clusters, max_iter, tol, verbose, gamma
            )
        if self.reduced and self.clu_lbl is not None:
            print('here')
            dict_bar_labels = {}
            for i in self.clu_lbl.unique():
                dict_bar_labels[i] = self.dict_barycenter(
                    train_model[i], bool_bar, bool_plots, n_clusters, max_iter, tol, verbose, gamma
                )
            return dict_bar_labels
        if self.reduced is False and self.clu_lbl is not None:
            dict_bar_labels = {}
            for i in self.clu_lbl.unique():
                dict_bar_labels[i] = self.dict_barycenter(
                    train_model[i], bool_bar, bool_plots, n_clusters, max_iter, tol, verbose, gamma
                )
            return dict_bar_labels

        #################################################
        if self.clu_lbl is not None:
            dict_bar_labels = {}
            for i in self.clu_lbl.unique():
                dict_bar_labels[i] = self.dict_barycenter(
                    train_model[i], bool_bar, bool_plots, n_clusters, max_iter, tol, verbose, gamma
                )
            return dict_bar_labels
        else:
            return self.dict_barycenter(
                train_model, bool_bar, bool_plots, n_clusters, max_iter, tol, verbose, gamma
            )

        return None

    def dict_barycenter(self, train_model, bool_bar, bool_plots, n_clusters, max_iter, tol, verbose, gamma):
        dict_bar = {
            'dataset': train_model['dict_scaler']['dataset'],
            'clusters': [x.T for x in train_model['ts_clustered']]
        }
        # Find barycentre's
        bar = barycenter(train_model['ts_clustered'], max_iter, tol, verbose, gamma)
        if self.model in clu_no_centroid:
            pass
        else:
            if bool_bar['centroid']:
                dict_bar['centroid'] = bar.centroid(
                    train_model['clu_model'],
                    train_model['ts_scaler'],
                    train_model['data']
                )
        if bool_bar['mean']:
            dict_bar['mean'] = bar.mean()
        if bool_bar['euclidean']:
            dict_bar['euclidean'] = bar.euclidean()
        if bool_bar['dba_vec']:
            dict_bar['dba_vectorized'] = bar.dba_vectorized()
        if bool_bar['dba_sub']:
            dict_bar['dba_subgradient'] = bar.dba_subgradient()
        if bool_bar['soft_dtw']:
            dict_bar['soft_dtw'] = bar.soft_dtw()
        for key, values_scales in dict_bar.items():
            if key == 'dataset':
                dict_bar['dataset'] = pd.DataFrame(
                    self._inverse_transform(values_scales.values.T, train_model['dict_scaler']).T,
                    columns=train_model['dict_scaler']['dataset'].columns,
                    index=train_model['dict_scaler']['dataset'].index
                )
            else:
                for x in values_scales:
                    self._inverse_transform(x, train_model['dict_scaler'])
        if bool_plots['summary_barycenters']:
            self.plots.all_barycenter(True, False, bool_plots['plot_n_cluster'], gamma, dict_bar)
        if bool_plots['plt_all_barycenters']:
            self.plots.all_barycenter(False, True, bool_plots['plot_n_cluster'], gamma, dict_bar)
        if bool_plots['view_clusters']:
            self.view_cluster(n_clusters, dict_bar, gamma)
        if bool_plots['pct_clusters']:
            self.pct_clusters(train_model['clu_model'].labels_)

        dict_bar['dataset']['cluster'] = train_model['cluster_labels']
        dict_bar['dataset']['user'] = train_model['dict_scaler']['user']

        df_count_clu = dict_bar['dataset'].groupby(['cluster', 'user', ]).size().unstack()
        df_count_clu = df_count_clu / df_count_clu.sum(axis=0)
        # plot df_count_clu T in barprlot stacked = True

        df_count_clu.T.plot.bar(stacked=True, figsize=(10, 5))


        return dict_bar

    def _get_hyperparameters(
            self,
            data: np.array = None
    ):
        if data is None:
            dict_scaler = self.transformer_dataset()
            data = dict_scaler['dataset'].values
        if self.type_dr is not None:
            data = self.dimensionality_reduction().fit_transform(data)
        model = NearestNeighbors(n_neighbors=2)  # creating an object of the NearestNeighbors class
        train_model = model.fit(data)  # fitting the data to the object
        distances, indices = train_model.kneighbors(data)  # finding the nearest neighbours
        # Sort and plot the distances results
        distances = np.sort(distances, axis=0)  # sorting the distances
        distances = distances[:, 1]  # taking the second column of the sorted distances
        plt.rcParams['figure.figsize'] = (5, 3)  # setting the figure size
        plt.plot(distances)  # plotting the distances
        plt.show()  # showing the plot

    def reduce_data(self):
        df_reduce = pd.DataFrame()

    def optimal_number_of_clusters(
            self,
            data: np.array = None,
            max_clusters: int = 10,
            max_quantile: float = 1.0,
            step: float = 0.05,
            plot: bool = True,
            n_clusters: int = 3,
            n_components: int = 3,
            quantile: float = 0.13,
            n_samples: int = None,
            eps: float = 1.1,
            min_samples=None,
            threshold: float = 1.5,
            branching_factor: int = 50,
            damping: float = 0.90,
            sigma: float = 0.5,
            lr: float = 0.5,
            num_iteration: int = 500,
            points_2d: bool = False,
            view_clu: bool = False,

    ):
        """
        Runs KMeans n times (according to max_cluster range)

        datasets: pd.DataFrame or np.array
            Time Series Data
        max_clusters: int
            Number of different clusters for KMeans algorithm
        metric: str
            Distance metric between the observations
        Returns:
        -------
        None
        """

        if self.reduced is False and self.clu_lbl is None:
            dict_sce = self.reshape_to_clu_atypical_mean()
            dict_scaler = self._scaler_data(dict_sce)
            ts_scaler = dict_scaler['dataset'].values
            # Dimensional reduction
            if self.type_dr is not None:
                data = self.dimensionality_reduction().fit_transform(ts_scaler)
            else:
                data = ts_scaler
        if self.reduced and self.clu_lbl is None:
            dict_sce = self.reshape_to_clu_atypical_mean()
            dict_scaler = self._scaler_data(dict_sce)
            ts_scaler = dict_scaler['dataset'].values
            # Dimensional reduction
            if self.type_dr is not None:
                data = self.dimensionality_reduction().fit_transform(ts_scaler)
            else:
                data = ts_scaler
        if self.reduced and self.clu_lbl is not None:
            models_with_labels = {}
            dict_sce = self.reshape_to_clu_atypical_mean()
            for i in self.clu_lbl.unique():
                dict_scaler = self._scaler_data(dict_sce, i)
                ts_scaler = dict_scaler['dataset'].values
                if self.type_dr is not None:
                    data = self.dimensionality_reduction().fit_transform(ts_scaler)
                else:
                    data = ts_scaler
        if self.reduced is False and self.clu_lbl is not None:
            models_with_labels = {}
            dict_sce = self.reshape_to_clu_atypical_mean()
            for i in self.clu_lbl.unique():
                dict_scaler = self._scaler_data(dict_sce, i)
                ts_scaler = dict_scaler['dataset'].values
                if self.type_dr is not None:
                    data = self.dimensionality_reduction().fit_transform(ts_scaler)
                else:
                    data = ts_scaler
        if self.clu_lbl is not None and self.reduced:
            models_with_labels = {}
            dict_sce = self.reshape_to_clu_atypical_mean()
            for i in self.clu_lbl.unique():
                dict_scaler = self._scaler_data(dict_sce, i)
                ts_scaler = dict_scaler['dataset'].values
                if self.type_dr is not None:
                    data = self.dimensionality_reduction().fit_transform(ts_scaler)
                else:
                    data = ts_scaler
        if self.clu_lbl is not None:
            models_with_labels = {}
            dict_sce = self.reshape_to_clu_atypical_mean()
            for i in self.clu_lbl.unique():
                dict_scaler = self._scaler_data(dict_sce, i)
                ts_scaler = dict_scaler['dataset'].values
                if self.type_dr is not None:
                    data = self.dimensionality_reduction().fit_transform(ts_scaler)
                else:
                    data = ts_scaler
        else:
            dict_sce = self.reshape_to_clu_atypical_mean()
            dict_scaler = self._scaler_data(dict_sce)
            ts_scaler = dict_scaler['dataset'].values
            # Dimensional reduction
            if self.type_dr is not None:
                data = self.dimensionality_reduction().fit_transform(ts_scaler)
            else:
                data = ts_scaler

        '''
        if data is None:
            dict_sce = self.reshape_to_clu_atypical_mean()
            dict_scaler = self._scaler_data(dict_sce)
            data = dict_scaler['dataset'].values
        if self.type_dr is not None:
            data = self.dimensionality_reduction().fit_transform(data)
        '''
        parameters = {
            'type_dr': self.type_dr,
            'model': self.model,
            'metric': self.metric,
            'n_jobs': self.n_jobs,
            'max_iter': self.max_iter,
            'seed': self.seed,
            'n_clusters': n_clusters,
            'n_components': n_components,
            'quantile': quantile,
            'n_samples': n_samples,
            'eps': eps,
            'min_samples': min_samples,
            'threshold': threshold,
            'branching_factor': branching_factor,
            'damping': damping,
            'sigma': sigma,
            'lr': lr,
            'num_iteration': num_iteration,
            'points_2d': points_2d,
            'view_clu': view_clu
        }

        # list empty for metrics
        distortions = []
        silhouette = []
        davies_bouldin = []
        calinski_harabasz = []
        range_aux = []
        # Number the test
        if self.model == 'MeanShift':
            clusters_range = np.arange(0.1, max_quantile, step)
            for k in tqdm(clusters_range):
                parameters['quantile'] = k
                clu = _clu_model(parameters)
                clu_model = clu.check_model(data, ts_scaler, dict_scaler)
                clu_labels = clu_model.fit_predict(data)
                # distortions.append(clu_model.inertia_)
                if k < 1:
                    if len(np.unique(clu_labels)) > 1:
                        silhouette.append(silhouette_score(data, clu_labels))
                        davies_bouldin.append(davies_bouldin_score(data, clu_labels))
                        calinski_harabasz.append(calinski_harabasz_score(data, clu_labels))
                        range_aux.append(k)
            clusters_range = range_aux
        elif self.model in model_with_eps:
            self._get_hyperparameters()
            return None
        else:
            clusters_range = range(1, max_clusters + 1)
            for k in tqdm(clusters_range):
                parameters['n_clusters'] = k
                clu = _clu_model(parameters)
                clu_model = clu.check_model(data, ts_scaler, dict_scaler)
                clu_labels = clu_model['clu_model'].fit_predict(data)
                if k == 1:
                    distortions.append(clu_model['clu_model'].inertia_)
                    silhouette.append(np.NaN)
                    davies_bouldin.append(np.NaN)
                    calinski_harabasz.append(np.NaN)
                    range_aux.append(k)
                if k > 1:
                    distortions.append(clu_model['clu_model'].inertia_)
                    silhouette.append(silhouette_score(data, clu_labels))
                    davies_bouldin.append(davies_bouldin_score(data, clu_labels))
                    calinski_harabasz.append(calinski_harabasz_score(data, clu_labels))
                    range_aux.append(k)
            clusters_range = range_aux

        metrics = {
            'distortions': distortions,
            'clusters_range': clusters_range,
            'silhouette': silhouette,
            'davies_bouldin': davies_bouldin,
            'calinski_harabasz': calinski_harabasz
        }

        if plot:
            self.plots.optimal_numbers_clustering(metrics, self.model)
        return metrics

        # Visualization
        fig, ax = plt.subplots()
        fig.subplots_adjust(right=0.75)
        twin1 = ax.twinx()
        twin2 = ax.twinx()
        twin3 = ax.twinx()

        # Offset the right spine of twin2.  The ticks and label have already been
        # placed on the right by twinx above.
        twin2.spines.right.set_position(("axes", 1.1))
        twin3.spines.right.set_position(("axes", 1.2))

        p1, = ax.plot(clusters_range, distortions, "bx-", label="Intra-cluster")
        p2, = twin1.plot(clusters_range[1:], silhouette, "rx-", label="Silhouette")
        p3, = twin2.plot(clusters_range[1:], davies_bouldin, "gx-", label="Davies Bouldin")
        p4, = twin3.plot(clusters_range[1:], calinski_harabasz, "yx-", label="Calinski Harabasz")

        ax.set_xlabel("Number of clusters (k)")
        ax.set_ylabel("Inertia")
        twin1.set_ylabel("Silhouette score")
        twin2.set_ylabel("Davies Bouldin score")
        twin3.set_ylabel("Alinski_Harabasz score")

        ax.yaxis.label.set_color(p1.get_color())
        twin1.yaxis.label.set_color(p2.get_color())
        twin2.yaxis.label.set_color(p3.get_color())
        twin3.yaxis.label.set_color(p4.get_color())

        tkw = dict(size=4, width=1.5)
        ax.tick_params(axis='y', colors=p1.get_color(), **tkw)
        twin1.tick_params(axis='y', colors=p2.get_color(), **tkw)
        twin2.tick_params(axis='y', colors=p3.get_color(), **tkw)
        twin3.tick_params(axis='y', colors=p4.get_color(), **tkw)
        ax.tick_params(axis='x', **tkw)

        ax.legend(handles=[p1, p2, p3, p4])
        plt.show()

    def performance_to_clu(
            self,
            dict_results,
            metrics: bool = True,
            pairplot_global: bool = False,
            violinplot_global: bool = False,
            boxplot_global: bool = False,
            boxplot_nMEAS: bool = False,
            PDC_AMI: bool = False,
            n_plots: int = 3,
            all_metrics: bool = True,
            mse: bool = None,
            mae: bool = None,
            mape: bool = None,
            m_global: bool = True,
            m_partial: bool = False
    ):
        preview = {
            'PDC_AMI': PDC_AMI,
            'n_plots': n_plots
        }
        dict_metrics = {
            'mse': mse,
            'mae': mae,
            'mape': mape,
            'case': {
                'm_global': m_global,
                'm_partial': m_partial
            },
            'plots': {
                'pairplot_global': pairplot_global,
                'boxplot_global': boxplot_global,
                'violinplot_global': violinplot_global,
                'boxplot_nMEAS': boxplot_nMEAS
            }
        }
        if all_metrics:
            dict_metrics['mse'], dict_metrics['mae'], dict_metrics['mape'] = False, False, True

        if self.reduced is False and self.clu_lbl is None:
            aux = 2
            dict_dates = self.get_summation_MEAS_Barycenter(dict_results, aux)
        if self.reduced and self.clu_lbl is None:
            aux = 2
            dataset_aux = pd.DataFrame()
            dict_sce = self.reshape_to_clu_atypical_mean()
            dict_sce.pop('means')
            df_results = dict_results['dataset'][['cluster', 'user']].reset_index(drop=True)
            df_aux = pd.DataFrame()
            for key, value in dict_sce.items():
                clu = df_results[df_results.user == key].values[0, 0]
                value.loc[:, 'cluster'] = clu
                value.loc[:, 'user'] = key
                dataset_aux = pd.concat([dataset_aux, value])
            dict_results['dataset'] = dataset_aux
            del dataset_aux
            del dict_sce
            dict_dates = self.get_summation_MEAS_Barycenter(dict_results, aux)

        if self.reduced and self.clu_lbl is not None:
            aux = 3
            dataset_aux = pd.DataFrame()
            dict_sce = self.reshape_to_clu_atypical_mean()
            dict_sce.pop('means')
            for x in self.clu_lbl.unique():
                df_results = dict_results[x]['dataset'][['cluster', 'user']].reset_index(drop=True)
                for key, value in dict_sce.items():
                    clu = df_results[df_results.user == key].values[0, 0]
                    df_aux = value[value.clu_1 == x]
                    df_aux.loc[:, 'cluster'] = clu
                    df_aux.loc[:, 'user'] = key
                    dataset_aux = pd.concat([dataset_aux, df_aux])
            dataset_aux.sort_index(inplace=True)
            dataset_aux.rename(columns={'clu_1': 'label'}, inplace=True)
            dict_results['dataset'] = dataset_aux
            del dataset_aux
            del dict_sce
            dict_dates = self.get_summation_MEAS_Barycenter(dict_results, aux)
            if preview['PDC_AMI']:
                self.plots.summation_MEAS_Barycenters(dict_dates, preview['n_plots'], self.seed)
            if metrics:
                dict_results_metrics = self.calculate_metrics(dict_dates, dict_metrics)
            return dict_results_metrics

        if self.reduced is False and self.clu_lbl is not None:
            aux = 3
            for i in self.clu_lbl.unique():
                dict_results[i]['dataset'].loc[:, 'label'] = i
            df_dataset = pd.DataFrame()
            for key, value in dict_results.items():
                df_dataset = pd.concat([df_dataset, value['dataset']])
                del value['dataset']
            df_dataset.sort_index(inplace=True)
            dict_results['dataset'] = df_dataset
            dict_dates = self.get_summation_MEAS_Barycenter(dict_results, aux)
        if preview['PDC_AMI']:
            self.plots.summation_MEAS_Barycenters(dict_dates, preview['n_plots'], self.seed)
        if metrics:
            dict_results_metrics = self.calculate_metrics(dict_dates, dict_metrics)
        return dict_results_metrics

    def get_summation_MEAS_Barycenter(self, dict_results, aux):
        dates = dict_results['dataset'].index.unique()
        dict_dates = dict()
        for d in dates:
            dict_data = dict()
            df_filter = dict_results['dataset'][dict_results['dataset'].index == d]
            meas_PDC = df_filter.iloc[:, :-aux].T.sum(axis=1).values
            dict_data['PDC'] = meas_PDC

            if self.reduced is False and self.clu_lbl is None:
                for i in dict_results.keys():
                    if i == 'dataset' or i == 'clusters':
                        pass
                    else:
                        np_aux = np.zeros((df_filter.shape[1] - aux, 1))
                        for j in df_filter.cluster:
                            np_aux += dict_results[i][j]
                        dict_data[i] = np_aux.reshape(df_filter.shape[1] - aux, )
                dict_dates[d] = dict_data
            if self.reduced and self.clu_lbl is None:
                for i in dict_results.keys():
                    if i == 'dataset' or i == 'clusters':
                        pass
                    else:
                        np_aux = np.zeros((df_filter.shape[1] - aux, 1))
                        for j in df_filter['cluster']:
                            np_aux += dict_results[i][j]
                        dict_data[i] = np_aux.reshape(df_filter.shape[1] - aux, )
                dict_dates[d] = dict_data
            if self.reduced and self.clu_lbl is not None:
                k = df_filter.label.unique()[0]
                if self.clu_lbl is not None:
                    for i in dict_results[k].keys():
                        if i == 'dataset' or i == 'clusters':
                            pass
                        else:
                            np_aux = np.zeros((df_filter.shape[1] - aux, 1))
                            for j in df_filter.cluster:
                                np_aux += dict_results[k][i][j]
                            dict_data[i] = np_aux.reshape(df_filter.shape[1] - aux, )
                    dict_dates[d] = dict_data

            if self.reduced is False and self.clu_lbl is not None:
                k = df_filter.label.unique()[0]
                if self.clu_lbl is not None:
                    for i in dict_results[k].keys():
                        if i == 'dataset' or i == 'clusters':
                            pass
                        else:
                            np_aux = np.zeros((df_filter.shape[1] - aux, 1))
                            for j in df_filter.cluster:
                                np_aux += dict_results[k][i][j]
                            dict_data[i] = np_aux.reshape(df_filter.shape[1] - aux, )
                    dict_dates[d] = dict_data
        return dict_dates

    def calculate_metrics(self, dict_dates, dict_metrics):
        df_global, df_partial = None, None
        if dict_metrics['case']['m_global']:
            df_global = pd.DataFrame()
        if dict_metrics['case']['m_partial']:
            df_partial = pd.DataFrame()
        for date in dict_dates.keys():
            for key, values in dict_dates[date].items():
                true = dict_dates[date]['PDC']
                if key == 'PDC':
                    pass
                else:
                    predict = values
                    if dict_metrics['case']['m_global']:
                        cols = ['model', 'date']
                        list_global = [key, date]
                        if dict_metrics['mse']:
                            list_global.append(mean_squared_error(true, predict.reshape(-1), squared=False))
                            cols.append('MSE')
                        if dict_metrics['mae']:
                            list_global.append(mean_absolute_error(true, predict.reshape(-1)))
                            cols.append('MAE')
                        if dict_metrics['mape']:
                            list_global.append(mean_absolute_percentage_error(true, predict.reshape(-1)))
                            cols.append('MAPE')
                        df_aux = pd.DataFrame(np.array(list_global).reshape(1, len(cols)), columns=cols)
                        df_global = pd.concat([df_global, df_aux], axis=0)
                    if dict_metrics['case']['m_partial']:
                        aux = np.concatenate((true.reshape(-1, 1), predict.reshape(-1).reshape(-1, 1)), axis=1)
                        for j in range(0, aux.shape[0]):
                            cols = ['Nro', 'model', 'date']
                            m_ind = [j, key, date]
                            if dict_metrics['mse']:
                                m_ind.append(
                                    mean_squared_error(
                                        aux[j][1].reshape(1, -1), squared=False
                                    )
                                )
                                cols.append('MSE')
                            if dict_metrics['mae']:
                                m_ind.append(
                                    mean_absolute_error(
                                        aux[j][0].reshape(1, -1),
                                        aux[j][1].reshape(1, -1)
                                    )
                                )
                                cols.append('MAE')
                            if dict_metrics['mape']:
                                m_ind.append(
                                    mean_absolute_percentage_error(
                                        aux[j][0].reshape(1, -1),
                                        aux[j][1].reshape(1, -1)
                                    )
                                )
                                cols.append('MAPE')
                            df_aux2 = pd.DataFrame(np.array(m_ind).reshape(1, len(cols)), columns=cols)
                            df_partial = pd.concat([df_partial, df_aux2], axis=0)
                            m_ind.clear(), cols.clear()
        metrics_aux = {}
        if dict_metrics['case']['m_global']:
            df_global.reset_index(inplace=True, drop=True)
            df_global.set_index('date', inplace=True, drop=True)
            df_global.index = pd.to_datetime(df_global.index)
            for i in df_global.columns[1:]:
                df_global[i] = df_global[i].astype(float)
            metrics_aux['global'] = df_global
        if dict_metrics['case']['m_partial']:
            df_partial.reset_index(inplace=True, drop=True)
            for i in df_partial.columns[3:]:
                df_partial[i] = df_partial[i].astype(float)
            metrics_aux['partial'] = df_partial

        if dict_metrics['plots']['pairplot_global']:
            sns.pairplot(df_global, hue='model')
            # sns.scatterplot(data=df_metric, x=df_metric.index, y='MAE', hue='model')
            plt.legend()
            plt.show()
        if dict_metrics['plots']['boxplot_global']:
            self.plots.plt_global(metrics_aux, True, False)
        if dict_metrics['plots']['violinplot_global']:
            self.plots.plt_global(metrics_aux, False, True)
        if dict_metrics['plots']['boxplot_nMEAS']:
            self.plots.plt_partial(metrics_aux, True, False)
        return metrics_aux

    def dimensionality_reduction(self):
        if self.type_dr == 'tsne':
            return TSNE(
                n_components=self.n_components,
                init='pca',
                random_state=self.seed
            )
        if self.type_dr == 'mds':
            return MDS(
                n_components=self.n_components,
                n_init=3,
                max_iter=100,
                random_state=self.seed
            )

    # Visualization for obtained clusters

    def view_cluster(
            self,
            n_clusters: int = None,
            dict_bar: dict = None,
            gamma: float = None
    ):
        fig_3, ax = plt.subplots(nrows=n_clusters, ncols=len(dict_bar.keys()) - 2, sharex=True)
        n = 0
        for key, value in dict_bar.items():
            if key == 'dataset' or key == 'clusters':
                pass
            else:
                for index, series in enumerate(dict_bar[key]):
                    ax[index, n].plot(dict_bar['clusters'][index], "k-", alpha=0.15)
                    ax[index, n].plot(series, c='r')
                    if n == 0:
                        ax[index, n].set_ylabel(f'Cluster {index}')
                    if index == n_clusters - 1:
                        ax[index, n].set_xlabel('Number of measurements')
                    if index == 0:
                        myTitle = f"Cluster with {set_tittle_cluster(key, gamma)}"
                        ax[index, n].set_title(myTitle, loc='center', wrap=True)
                n += 1
        plt.legend()
        fig_3.suptitle(f"Nro. {n_clusters} Clusters\nwith {self.type_dr} dimentional reduction ")
        plt.show()

    def pct_clusters(
            self,
            labels_clu
    ):
        labels = np.unique(labels_clu, return_counts=True)
        fig, ax = plt.subplots()
        ax.pie(labels[1], labels=labels[0], autopct='%1.1f%%', shadow=True, startangle=90)
        plt.show()

    def clu_model_2d(self, model):
        # Visualization for obtained clusters
        u_labels = np.unique(model['cluster_labels'])
        # Centroids Visualization
        plt.figure(figsize=(16, 10))
        if self.model in clu_no_centroid:
            pass
        else:
            centroids = model['clu_model'].cluster_centers_
            plt.scatter(centroids[:, 0], centroids[:, 1], s=150, color='r', marker="x")
        # Downsize the datasets into 2D
        if model['data'].shape[1] > 2:
            self.type_dr = 'tsne'
            data = self.dimensionality_reduction().fit_transform(model['data'])
            for u_label in u_labels:
                cluster_points = data[(model['cluster_labels'] == u_label)]
                plt.scatter(cluster_points[:, 0], cluster_points[:, 1], label=u_label)
        else:
            for u_label in u_labels:
                cluster_points = model['data'][(model['cluster_labels'] == u_label)]
                plt.scatter(cluster_points[:, 0], cluster_points[:, 1], label=u_label)
        plt.title('Clustered Data')
        plt.xlabel("Feature space for the 1st feature")
        plt.ylabel("Feature space for the 2nd feature")
        plt.grid(True)
        plt.legend(title='Cluster Labels')
        plt.show()

    def plot_2D_clusters(
            self,
            cluster_model,
            data=None
    ):
        """
        Plots clusters obtained by clustering model

        datasets: pd.DataFrame or np.array
            Time Series Data
        cluster_model: Class
            Clustering algorithm
        dim_red_algo: Class
            Dimensionality reduction algorithm (e.g. TSNE/PCA/MDS...)
        Returns:
        -------
        None
        """
        if data is None:
            dict_scaler = self.transformer_dataset()
            data = dict_scaler['dataset'].values
        if self.type_dr is not None:
            dim_red_algo = self.dimensionality_reduction()
            data = dim_red_algo.fit_transform(data)

        cluster_labels = cluster_model.fit_predict(data)
        centroids = cluster_model.cluster_centers_
        u_labels = np.unique(cluster_labels)

        # Centroids Visualization
        plt.figure(figsize=(16, 10))
        plt.scatter(centroids[:, 0], centroids[:, 1], s=150, color='r', marker="x")

        # Downsize the datasets into 2D
        if data.shape[1] > 2:
            self.type_dr = 'tsne'
            data = self.dimensionality_reduction().fit_transform(data)
            for u_label in u_labels:
                cluster_points = data[(cluster_labels == u_label)]
                plt.scatter(cluster_points[:, 0], cluster_points[:, 1], label=u_label)
        else:
            for u_label in u_labels:
                cluster_points = data[(cluster_labels == u_label)]
                plt.scatter(cluster_points[:, 0], cluster_points[:, 1], label=u_label)

        plt.title('Clustered Data')
        plt.xlabel("Feature space for the 1st feature")
        plt.ylabel("Feature space for the 2nd feature")
        plt.grid(True)
        plt.legend(title='Cluster Labels')
        plt.show()

    class plots:

        def __init__(self):
            return

        @staticmethod
        def optimal_numbers_clustering(
                metrics: dict = None,
                model: str = None
        ):
            if metrics is None:
                print('run the function: optimal_number_of_clusters_with_kmeans')
            else:
                # Visualization
                fig, ax = plt.subplots()
                fig.subplots_adjust(right=0.75)
                twin1 = ax.twinx()
                twin2 = ax.twinx()
                twin3 = ax.twinx()

                # Offset the right spine of twin2.  The ticks and label have already been
                # placed on the right by twinx above.
                twin2.spines.right.set_position(("axes", 1.1))
                twin3.spines.right.set_position(("axes", 1.2))

                p1, = ax.plot(metrics['clusters_range'], metrics['silhouette'], "rx-", label="Silhouette")
                p2, = twin1.plot(metrics['clusters_range'], metrics['davies_bouldin'], "gx-", label="Davies Bouldin")
                p3, = twin2.plot(metrics['clusters_range'], metrics['calinski_harabasz'], "yx-",
                                 label="Calinski Harabasz")
                if len(metrics['distortions']) > 0:
                    p4, = twin3.plot(metrics['clusters_range'], metrics['distortions'], "bx-", label="Intra-cluster")

                if model == 'MeanShift':
                    ax.set_xlabel("Quantile (k)")
                else:
                    ax.set_xlabel("Number of clusters (k)")

                ax.set_ylabel("Silhouette score")
                twin1.set_ylabel("Davies Bouldin score")
                twin2.set_ylabel("Alinski_Harabasz score")
                twin3.set_ylabel("Inertia")

                ax.yaxis.label.set_color(p1.get_color())
                twin1.yaxis.label.set_color(p2.get_color())
                twin2.yaxis.label.set_color(p3.get_color())
                if len(metrics['distortions']) > 0:
                    twin3.yaxis.label.set_color(p4.get_color())

                tkw = dict(size=4, width=1.5)

                ax.tick_params(axis='y', colors=p1.get_color(), **tkw)
                twin1.tick_params(axis='y', colors=p2.get_color(), **tkw)
                twin2.tick_params(axis='y', colors=p3.get_color(), **tkw)
                if len(metrics['distortions']) > 0:
                    twin3.tick_params(axis='y', colors=p4.get_color(), **tkw)
                ax.tick_params(axis='x', **tkw)

                if len(metrics['distortions']) > 0:
                    ax.legend(handles=[p1, p2, p3, p4])
                else:
                    ax.legend(handles=[p1, p2, p3])
                plt.show()

        @staticmethod
        def clu_model_view(
                model
        ):
            def plot_cluster_ts(current_cluster):
                """
                Plots time series in a cluster

                current_cluster: np.array
                    Cluster with time series
                Returns:
                -------
                None
                """
                fig, ax = plt.subplots(
                    int(np.ceil(current_cluster.shape[0] / 5)),
                    5,
                    figsize=(45, 3 * int(np.ceil(current_cluster.shape[0] / 5))),
                    sharex=True,
                    sharey=True
                )
                fig.autofmt_xdate(rotation=45)
                ax = ax.reshape(-1)
                for index, series in enumerate(current_cluster):
                    ax[index].plot(series)
                    plt.xticks(rotation=45)

                plt.tight_layout()
                plt.show()

            # Objects distribution in the obtained clusters
            labels = [f'Cluster_{i}' for i in range(len(model['ts_clustered']))]
            samples_in_cluster = [val.shape[0] for val in model['ts_clustered']]
            plt.figure(figsize=(16, 5))
            plt.bar(labels, samples_in_cluster)
            # plt.pie(samples_in_cluster, labels=labels, autopct='%1.1f%%', shadow=True, startangle=90)
            for cluster in range(len(model['ts_clustered'])):
                print(f"==========Cluster number: {cluster}==========")
                plot_cluster_ts(model['ts_clustered'][cluster])
            # plt.show()

        @staticmethod
        def all_barycenter(
                summary: bool = True,
                all_bar: bool = False,
                plot_n_cluster: int = 1,
                gamma: int = 1.0,
                dict_bar: dict = None
        ):
            if all_bar:
                # Plot barycenter of the cluster input for user and selected
                fig_1, ax = plt.subplots(nrows=len(dict_bar.keys()) - 2, ncols=1, sharex=True)
                n = 0
                for key, value in dict_bar.items():
                    if key == 'dataset' or key == 'clusters':
                        pass
                    else:
                        ax[n].plot(dict_bar['clusters'][plot_n_cluster], "k-", alpha=0.2)
                        ax[n].plot(dict_bar[key][plot_n_cluster], c='r')
                        ax[n].set_title(set_tittle_cluster(key, gamma), loc='left', y=0.85, x=0.02, fontsize='medium')
                        n += 1
                fig_1.suptitle(f'Cluster Series - Cluster No. {plot_n_cluster}')
                plt.show()

            if summary:
                fig, ax = plt.subplots(nrows=len(dict_bar['clusters']), ncols=1, sharex=True, layout='constrained')
                for i in range(len(dict_bar['clusters'])):
                    ax[i].plot(dict_bar['clusters'][i], "k-", alpha=0.2)
                    for key, value in dict_bar.items():
                        if (key == 'dataset') or (key == 'clusters'):
                            pass
                        else:
                            ax[i].plot(dict_bar[key][i], label=set_tittle_cluster(key, gamma))
                    ax[i].set_title(f"Summary to Cluster Nro. {i}")
                labels_handles = {
                    label: handle for ax in fig.axes for handle, label in zip(*ax.get_legend_handles_labels())
                }
                lines = []
                labels = []
                for ax in fig.axes:
                    Line, Label = ax.get_legend_handles_labels()
                    # print(Label)
                    lines.extend(Line)
                    labels.extend(Label)

                lines = [i for n, i in enumerate(lines) if i not in lines[:n]]
                labels = [i for n, i in enumerate(labels) if i not in labels[:n]]

                # rotating x-axis labels of last sub-plot
                plt.xticks(rotation=45)

                fig.legend(lines, labels, loc='outside right')
                plt.show()

        @staticmethod
        def summation_MEAS_Barycenters(dict_dates, preview, seed):
            import random
            random.seed(seed)
            dates_aux = random.choices(list(dict_dates.keys()), k=preview)
            for d in dates_aux:
                plt.figure(figsize=(15, 5))
                for key, values in dict_dates[d].items():
                    if key == 'PDC':
                        plt.plot(values, label=key, color='k', lw=3, marker='o')
                    else:
                        plt.plot(values, label=key, ls='--')
                plt.title(d)
                plt.legend(loc="best")

                plt.show()

        @staticmethod
        def plt_global(dict_metrics, boxplot: bool = None, violinplot: bool = None):
            df_global = dict_metrics['global']
            if boxplot:
                # Boxplot
                if len(df_global.columns[1:]) == 1:
                    sns.boxplot(data=df_global, x='model', y=df_global.columns[1:][0], fliersize=0)
                    plt.title('Boxplot for clustering')
                    plt.show()
                else:
                    n = len(df_global.columns[1:])
                    fig, axes = plt.subplots(n, 1, sharex=True)
                    n = 1
                    for k in df_global.columns[1:]:
                        sns.boxplot(ax=axes[n], data=df_global, x='model', y=k, fliersize=0)
                        n += 1
                    fig.suptitle('Boxplot for clustering')
                    plt.show()

            if violinplot:
                # Violinplot
                # Boxplot
                if len(df_global.columns[1:]) == 1:
                    sns.violinplot(data=df_global, x='model', y=df_global.columns[1:][0], fliersize=0)
                    plt.title('Violinplot for clustering')
                    plt.show()
                else:
                    n = len(df_global.columns[1:])
                    fig, axes = plt.subplots(n, 1, sharex=True)
                    n = 1
                    for k in df_global.columns[1:]:
                        sns.violinplot(ax=axes[n], data=df_global, x='model', y=k, fliersize=0)
                        n += 1
                    fig.suptitle('Violinplot for clustering')
                    plt.show()

        @staticmethod
        def plt_partial(dict_metrics, boxplot: bool = None, violinplot: bool = None):
            df_partial = dict_metrics['partial']
            if boxplot:
                fig2, axes = plt.subplots(3, 1, figsize=(18, 10))
                fig2.suptitle('Boxplot for clustering')
                sns.boxplot(ax=axes[0], data=df_partial[df_partial.model == 'mean'], x='Nro', y='MAPE', fliersize=0)
                sns.lineplot(ax=axes[1], data=df_partial[df_partial.model == 'mean'], x='Nro', y='MAPE')
                sns.catplot(ax=axes[2], data=df_partial, x='Nro', y='MAPE', hue='model', kind="point")
                # sns.boxplot(ax=axes[2], data=df_metric_min, x='model', y='MAPE')
                sns.boxplot()


class _clu_model:
    def __init__(
            self,
            parameters
    ):
        self.type_dr = parameters['type_dr']
        self.model = parameters['model']
        self.metric = parameters['metric']
        self.n_jobs = parameters['n_jobs']
        self.max_iter = parameters['max_iter']
        self.seed = parameters['seed']
        self.n_clusters = parameters['n_clusters']
        self.n_components = parameters['n_components']
        self.quantile = parameters['quantile']
        self.n_samples = parameters['n_samples']
        self.eps = parameters['eps']
        self.min_samples = parameters['min_samples']
        self.threshold = parameters['threshold']
        self.branching_factor = parameters['branching_factor']
        self.damping = parameters['damping']
        self.sigma = parameters['sigma']
        self.lr = parameters['lr']
        self.num_iteration = parameters['num_iteration']
        self.points_2d = parameters['points_2d']
        self.view_clu = parameters['view_clu']

    def check_model(self, data, ts_scaler, dict_scaler):
        # Select model of clustering
        if self.min_samples is None:
            self.min_samples = 2 * data.shape[1]
        if self.model == 'SOM':
            # Initialization and training
            som_shape = (1, self.n_clusters)
            som = MiniSom(
                som_shape[0],
                som_shape[1],
                data.shape[1],
                sigma=self.sigma,
                learning_rate=self.lr,
                neighborhood_function='gaussian',
                random_seed=10
            )
            som.train_batch(data, num_iteration=self.num_iteration, verbose=True)
            # each neuron represents a cluster
            winner_coordinates = np.array([som.winner(x) for x in data]).T
            # with np.ravel_multi_index we convert the bidimensional
            # coordinates to a monodimensional index
            cluster_labels = np.ravel_multi_index(winner_coordinates, som_shape)
            ts_clustered = [ts_scaler[(cluster_labels == label), :] for label in np.unique(cluster_labels)]
            train_model = {
                'clu_model': som,
                'ts_clustered': ts_clustered,
                'cluster_labels': cluster_labels,
                'data': data,
                'ts_scaler': ts_scaler,
                'dict_scaler': dict_scaler
            }
            if self.points_2d:
                # plotting the clusters using the first 2 dimensions of the data
                for c in np.unique(cluster_labels):
                    plt.scatter(
                        data[cluster_labels == c, 0],
                        data[cluster_labels == c, 1],
                        label='cluster=' + str(c),
                        alpha=.7
                    )
                # plotting centroids
                for centroid in som.get_weights():
                    plt.scatter(
                        centroid[:, 0],
                        centroid[:, 1],
                        marker='x',
                        s=80,
                        linewidths=5,
                        color='k',
                        label='centroid'
                    )
                plt.legend()
            if self.view_clu:
                self.plots.clu_model_view(train_model)
            return train_model

        clu_model = self._select_model(data)
        cluster_labels = clu_model.fit_predict(data)
        ts_clustered = [ts_scaler[(cluster_labels == label), :] for label in np.unique(cluster_labels)]
        train_model = {
            'clu_model': clu_model,
            'ts_clustered': ts_clustered,
            'cluster_labels': cluster_labels,
            'data': data,
            'ts_scaler': ts_scaler,
            'dict_scaler': dict_scaler
        }
        if self.points_2d:
            self.clu_model_2d(train_model)
        if self.view_clu:
            self.plots.clu_model_view(train_model)
        return train_model

    def _select_model(self, data):
        # Clustering model
        if self.model == 'KMeans':
            clu_model = TimeSeriesKMeans(
                n_clusters=self.n_clusters,
                metric=self.metric,
                n_jobs=self.n_jobs,
                max_iter=self.max_iter,
                random_state=self.seed
            )
            return clu_model
        elif self.model == 'MiniBatchKMeans':
            clu_model = MiniBatchKMeans(
                n_clusters=self.n_clusters,
                max_iter=self.max_iter,
                random_state=self.seed
            )
            return clu_model
        elif self.model == 'MeanShift':
            return MeanShift(
                bandwidth=estimate_bandwidth(
                    data,
                    quantile=self.quantiles,
                    n_samples=self.n_sampless
                )
            )
        elif self.model == 'DBSCAN':
            return DBSCAN(eps=self.eps, min_samples=self.min_samples)
        elif self.model == 'Birch':
            return Birch(
                n_clusters=self.n_clusters,
                threshold=self.threshold,
                branching_factor=self.branching_factor
            )
        elif self.model == 'GaussianMixture':
            return GaussianMixture(
                n_components=self.n_components
            )
        elif self.model == 'OPTICS':
            return OPTICS(
                eps=self.eps,
                min_samples=self.min_samples
            )
        elif self.model == 'AffinityPropagation':
            return AffinityPropagation(
                damping=self.damping
            )
        elif self.model == 'Agglomerative':
            return AgglomerativeClustering(
                n_clusters=self.n_clusters
            )
        elif self.model == 'Spectral':
            return SpectralClustering(
                n_clusters=self.n_clusters
            )


class barycenter:

    def __init__(self, ts_clustered, max_iter, tol, verbose, gamma):
        self.ts_clustered = ts_clustered
        self.max_iter = max_iter
        self.tol = tol
        self.verbose = verbose
        self.gamma = gamma

    def centroid(self, clu_model, ts_scaler, data):
        # Cluster Centroid
        closest_clusters_index = [
            np.argmin(
                [np.linalg.norm(cluster_center - point, ord=2) for point in data]
            ) for cluster_center in clu_model.cluster_centers_
        ]
        closest_ts = ts_scaler[closest_clusters_index, :]
        # Centroids
        all_centroids = [np.array(x).reshape(np.array(x).shape[0], 1) for x in closest_ts.tolist()]
        return all_centroids

    def mean(self):
        # Means to cluster's
        all_meas = [
            np.mean(np.array(x), axis=0).reshape(np.mean(np.array(x), axis=0).shape[0], 1) for x in self.ts_clustered
        ]
        return all_meas

    def euclidean(self):
        euclidean = [euclidean_barycenter(cluster_series) for cluster_series in self.ts_clustered]
        return euclidean

    def dba_vectorized(self):
        dba_ts = [
            dtw_barycenter_averaging(
                cluster_series,
                max_iter=self.max_iter,
                tol=self.tol,
                verbose=self.verbose
            ) for cluster_series in self.ts_clustered
        ]
        return dba_ts

    def dba_subgradient(self):
        dba_sub = [
            dtw_barycenter_averaging_subgradient(
                cluster_series,
                max_iter=self.max_iter,
                tol=self.tol,
                verbose=self.verbose
            ) for cluster_series in self.ts_clustered
        ]
        return dba_sub

    def soft_dtw(self):
        dba_sotf = [
            softdtw_barycenter(
                cluster_series,
                gamma=self.gamma,
                max_iter=self.max_iter,
                tol=self.tol
            ) for cluster_series in self.ts_clustered
        ]
        return dba_sotf
