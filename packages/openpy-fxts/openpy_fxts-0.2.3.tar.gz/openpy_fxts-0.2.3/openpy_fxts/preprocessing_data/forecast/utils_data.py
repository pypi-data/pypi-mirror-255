import numpy as np
import pandas as pd
from sklearn.preprocessing import FunctionTransformer
from openpy_fxts.base_tf import value_miss

class complete_missing:
    pass


def sin_transformer(period):
    return FunctionTransformer(lambda x: np.sin(x / period * 2 * np.pi))


def cos_transformer(period):
    return FunctionTransformer(lambda x: np.cos(x / period * 2 * np.pi))


def _filter_y_features(df_y, y_features, n_future):
    list_filter = list()
    for i in range(len(y_features)):
        a = [x for x in list(df_y.columns) if y_features[i] in x]
        list_filter.extend(a)
    df_y = df_y[list_filter]

    dict_aux = {}
    for i in range(len(y_features)):
        a = [x for x in list(df_y.columns) if y_features[i] in x]
        dict_aux[i] = a

    list_aux = []
    for i in range(n_future):
        for key, value in dict_aux.items():
            dict_aux[key] = value
            list_aux.append(value[i])

    return df_y[list_aux]


def _series_to_supervised(
        data,
        dropnan=None,
        n_in=1,
        n_out=1,
        feat_str_at_end=True,
        feat_lag_str='IP',
        feat_lead_str='OP',
        value_replace=value_miss
):

    if data.isnull().sum().sum() > 0:
        data.fillna(value_replace, inplace=True)

    if feat_str_at_end:
        n_vars = 1 if type(data) is list else data.shape[1]
        df = pd.DataFrame(data)
        cols, names = list(), list()
        # input sequence (t-n, ... t-1)
        for i in range(n_in, 0, -1):
            cols.append(df.shift(i))
            if i < 10:
                name_i = '0' + str(i)
            else:
                name_i = str(i)
            names += [
                (
                        str(
                            pd.DataFrame(df.iloc[:, j]).columns.values
                        ).replace("']", '').replace("['", '') + '_' + feat_lag_str + '_' + name_i
                ) for j in range(n_vars)
            ]
        # forecast sequence (t, t+1, ... t+n)
        for i in range(0, n_out):
            cols.append(df.shift(-i))
            if i == 0:
                names += [
                    (
                        str(
                            pd.DataFrame(df.iloc[:, j]).columns.values
                        ).replace("']", '').replace("['", '')
                    ) for j in range(n_vars)
                ]
            else:
                if i < 10:
                    name_i = '0' + str(i)
                else:
                    name_i = str(i)
                names += [
                    (
                            str(
                                pd.DataFrame(df.iloc[:, j]).columns.values
                            ).replace("']", '').replace("['", '') + '_' + feat_lead_str + '_' + name_i
                    ) for j in range(n_vars)
                ]
        # put it all together
        agg = pd.concat(cols, axis=1)
        agg.columns = names
        # drop rows with NaN values
        if dropnan:
            agg.dropna(inplace=True)

    else:
        n_vars = 1 if type(data) is list else data.shape[1]
        df = pd.DataFrame(data)
        cols, names = list(), list()
        # input sequence (t-n, ... t-1)
        for i in range(n_in, 0, -1):
            cols.append(df.shift(i))
            names += [
                (
                    feat_lag_str + '%d' % (i) + str(
                        pd.DataFrame(df.iloc[:, j]).columns.values
                    ).replace("']", '').replace("['", '')
                ) for j in range(n_vars)
            ]
        # forecast sequence (t, t+1, ... t+n)
        for i in range(0, n_out):
            cols.append(df.shift(-i))
            if i == 0:
                names += [
                    (
                        str(pd.DataFrame(df.iloc[:, j]).columns.values).replace("']", '').replace("['", '')
                    ) for j in range(n_vars)
                ]
            else:
                if i < 10:
                    name_i = '0' + str(i)
                else:
                    name_i = str(i)
                names += [
                    (
                            str(
                                pd.DataFrame(df.iloc[:, j]).columns.values
                            ).replace("']", '').replace("['", '') + '_' + feat_lead_str + '_' + name_i
                    ) for j in range(n_vars)
                ]
        # put it all together
        agg = pd.concat(cols, axis=1)
        agg.columns = names
        # drop rows with NaN values
        if dropnan:
            agg.dropna(inplace=True)
    return agg


def _scaler_data(df_data, MinMax: bool = True, Standard: bool = None):
    if Standard:
        MinMax = False
        from sklearn.preprocessing import StandardScaler
        scaler = StandardScaler()
    if MinMax:
        from sklearn.preprocessing import MinMaxScaler
        scaler = MinMaxScaler(feature_range=(-1, 1))
    df = pd.DataFrame(
        columns=df_data.columns,
        index=df_data.index)
    df_scaler = df_data

    scalers = {}
    for i in df_data.columns:
        scaler = MinMaxScaler(feature_range=(-1, 1))
        s_s = scaler.fit_transform(df_scaler[i].values.reshape(-1, 1))
        s_s = np.reshape(s_s, len(s_s))
        scalers['scaler_' + i] = scaler
        # df.loc[:, i] = np.asarray(s_s, dtype=float)
        df_scaler[i] = s_s

    return df_scaler, scalers
