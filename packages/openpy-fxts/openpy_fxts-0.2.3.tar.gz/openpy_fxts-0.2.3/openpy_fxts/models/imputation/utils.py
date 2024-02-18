# -*- coding: utf-8 -*-
# @Time    : 06/07/2023
# @Author  : Ing. Jorge Lara
# @Email   : jlara@iee.unsj.edu.ar
# @File    : ------------
# @Software: PyCharm

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error
import matplotlib.pyplot as plt
import datetime
from openpy_fxts.mdits.mdls_dl.base_tf import tko, tkloss, tku, tkc, tkmtc, tf
from time import time
from openpy_fxts.base_tf import value_miss


def tk_optimizer_loss(optimizer: str = 'Adam'):
    if optimizer == 'Adam':
        opt = tko.Adam()
        return opt


def tk_loss(loss: str = 'Huber'):
    if loss == 'Huber':
        metric = tkloss.Huber()
    return metric


def _date_init_final(config: dict = None):
    init = config['dataset'].index[0]
    final = config['dataset'].index[-1]
    date1 = f"{init.year}{init.month}{init.day}"
    date2 = f"{final.year}{final.month}{final.day}"
    n_in_out = f"int{config['n_past']}_out{config['n_future']}"
    fts = ""
    for i in config['y_colname']:
        fts += f"_{i}"
    name_folder = date1 + '_' + date2 + fts + '_' + n_in_out
    mttr_upd = 'mttr_' + config['MTTR'] + '_upd_' + config['Act']

    return name_folder, mttr_upd


def _learning_curve(
        history,
        name_mode: str = 'model',
        filepath: str = None,
        time_start=None,
        monitor_label: str = 'val_loss'
):
    hist = pd.DataFrame(history.history)
    hist['epoch'] = history.epoch
    min_vec = []
    for i in range(0, len(hist)):
        if i == 0:
            min_vec.append(hist[[monitor_label]].iloc[i, :].values[0])
        else:
            if hist[[monitor_label]].iloc[i, :].values[0] < np.min(min_vec):
                min_vec.append(hist[[monitor_label]].iloc[i, :].values[0])
            else:
                min_vec.append(np.min(min_vec))

    hist['best_from_start'] = min_vec
    hist['improved'] = np.where(hist['best_from_start'] == hist[monitor_label], 1, 0)

    best_epoch = hist[hist[monitor_label] == np.min(hist[monitor_label])]['epoch'].values[0]

    plt.figure(figsize=(18, 9))
    plt.xticks(np.arange(len(hist['epoch'])), np.arange(1, len(hist['epoch']) + 1))
    plt.plot(hist[monitor_label], label=monitor_label)
    try:
        plt.plot(hist['loss'], label='loss')
    except:
        pass
    # plt.plot(hist[monitor_label], label = 'val_loss')

    plt.scatter(
        hist[hist['improved'] == 1]['epoch'],
        hist[hist['improved'] == 1][monitor_label],
        color='green',
        label='Improved'
    )
    plt.legend()
    plt.title(
        'Learning curve'
        '\n' + 'best epoch:' + str(best_epoch + 1) + '(' + str(round(np.min(hist[monitor_label]), 3)) + ')' +
        '\n' + 'time_train: ' + str(datetime.timedelta(seconds=time() - time_start))
    )
    if filepath is not None:
        plt.savefig(f'{filepath}/{name_mode}_{monitor_label}.png')


def _mdl_characteristics(model, config_sim: dict = None, filepath: str = None):
    if config_sim['view_summary']:
        model.summary(expand_nested=True)
    if config_sim['plt_model']:
        if filepath is None:
            tku.plot_model(model, show_shapes=True)
        else:
            tku.plot_model(model, to_file=filepath, show_shapes=True, show_layer_names=True)


def _callbacks(
        filepath,
        model: bool = None,
        weights: bool = None,
        verbose: int = None,
        patience: int = None,
        model_checkpoint: bool = True,
        reduce_LR: bool = True,
        early_stopping: bool = True,
        tensor_board: bool = False
):
    if weights:
        save_best_only = True
        save_weights_only = True
        label = 'weights'
    if model:
        save_best_only = True
        save_weights_only = False
        label = 'model'

    callbacks_list = []
    if model_checkpoint:
        filepath = str(filepath) + f'/{label}' + '-{epoch:02d}.hdf5'
        checkpoint_cb = tkc.ModelCheckpoint(
            filepath=filepath,
            monitor='val_loss',
            verbose=verbose,
            save_best_only=save_best_only,
            save_weights_only=save_weights_only,
            mode='auto'
        )
        callbacks_list.append(checkpoint_cb)
    if reduce_LR:
        lr_cb = tkc.ReduceLROnPlateau(
            monitor='loss',
            factor=0.2,
            patience=patience,
            min_lr=2.5e-5,
            verbose=verbose,
            cooldown=0
        )
        callbacks_list.append(lr_cb)
    if early_stopping:
        es_cp = tkc.EarlyStopping(
            monitor='val_loss',
            patience=patience,
            verbose=verbose
        )
        callbacks_list.append(es_cp)
    if tensor_board:
        log_dir = "logs\\" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        tensorboard_callback = tkc.TensorBoard(log_dir=log_dir, histogram_freq=1)
        callbacks_list.append(tensorboard_callback)
    return callbacks_list


def _scaler_data(train_dict, val_dict):
    scaler = StandardScaler()
    encoder_input_train = scaler.fit_transform(
        train_dict['encoder_input_train'].reshape(-1, train_dict['encoder_input_train'].shape[-1])).reshape(
        train_dict['encoder_input_train'].shape)
    decoder_input_train = scaler.transform(
        train_dict['decoder_input_train'].reshape(-1, train_dict['decoder_input_train'].shape[-1])).reshape(
        train_dict['decoder_input_train'].shape)
    final_output_train = scaler.transform(
        train_dict['final_output_train'].reshape(-1, train_dict['final_output_train'].shape[-1])).reshape(
        train_dict['final_output_train'].shape)
    encoder_input_val = scaler.transform(
        val_dict['encoder_input_val'].reshape(-1, val_dict['encoder_input_val'].shape[-1])).reshape(
        val_dict['encoder_input_val'].shape)
    decoder_input_val = scaler.transform(
        val_dict['decoder_input_val'].reshape(-1, val_dict['decoder_input_val'].shape[-1])).reshape(
        val_dict['decoder_input_val'].shape)
    final_output_val = scaler.transform(
        val_dict['final_output_val'].reshape(-1, val_dict['final_output_val'].shape[-1])).reshape(
        val_dict['final_output_val'].shape)

    train_dict_scaler, val_dict_scaler = {}, {}
    # Train
    train_dict_scaler['encoder_input_train'] = encoder_input_train
    train_dict_scaler['decoder_input_train'] = decoder_input_train
    train_dict_scaler['final_output_train'] = final_output_train
    # Validation
    val_dict_scaler['encoder_input_val'] = encoder_input_val
    val_dict_scaler['decoder_input_val'] = decoder_input_val
    val_dict_scaler['final_output_val'] = final_output_val

    return train_dict_scaler, val_dict_scaler, scaler


def _inverse_transform(yhat, dict_test, columns):
    for index, i in enumerate(columns):
        scaler = dict_test['scaler']['scaler_' + i]
        yhat[:, :, index] = scaler.inverse_transform(yhat[:, :, index])
        dict_test['y'][:, :, index] = scaler.inverse_transform(dict_test['y'][:, :, index])
    return yhat, dict_test['y']


def _historical_max_min(encoder_input_train):
    historical_max = np.expand_dims(
        np.max(encoder_input_train.reshape(-1, encoder_input_train.shape[-1]), axis=0, keepdims=True), 0)
    historical_min = np.expand_dims(
        np.min(encoder_input_train.reshape(-1, encoder_input_train.shape[-1]), axis=0, keepdims=True), 0)
    return historical_max, historical_min


def _example_plot(ax, final_output_test, pred, i, fontsize=10, hide_labels=False):
    ax.plot(final_output_test.reshape(-1, final_output_test.shape[-1])[:, i], c='blue', label="measured")
    ax.plot(pred.reshape(-1, pred.shape[-1])[:, i], c='red', label="prediction")
    ax.legend()
    ax.locator_params(nbins=3)
    if hide_labels:
        ax.set_xticklabels([])
        ax.set_yticklabels([])
    else:
        ax.set_xlabel(f'Feature {i + 1} across all timesteps', fontsize=fontsize)
        ax.set_ylabel(f'F_{i + 1}', fontsize=fontsize)
        # ax.set_title('Title', fontsize=fontsize)
    mse = mean_squared_error(
        final_output_test.reshape(-1, final_output_test.shape[-1])[:, i],
        pred.reshape(-1, pred.shape[-1])[:, i],
        squared=False
    )
    print(f'Feature {i + 1} MSE: {mse}')


def _examples_plots_metrics_ft(
        ax,
        n_future,
        mae_list,
        type,
):
    ax.plot(range(0, n_future), mae_list, marker='o')
    ax.xticks((range(0, n_future)))
    ax.xlabel('Forecast Range')
    ax.ylabel(type)


def _examples_plots(
        ax,
        final_output_test,
        pred,
        i,
        fontsize,
        hide_labels=False
):
    ax.plot(final_output_test.reshape(-1, final_output_test.shape[-1])[:, i], c='blue', label="measured")
    ax.plot(pred.reshape(-1, pred.shape[-1])[:, i], c='red', label="prediction")
    ax.legend()
    ax.locator_params(nbins=3)
    if hide_labels:
        ax.set_xticklabels([])
        ax.set_yticklabels([])
    else:
        ax.set_xlabel(f'Feature {i + 1} across all timesteps', fontsize=fontsize)
        ax.set_ylabel(f'F_{i + 1}', fontsize=fontsize)
        # ax.set_title('Title', fontsize=fontsize)
    mse = mean_squared_error(
        final_output_test.reshape(-1, final_output_test.shape[-1])[:, i],
        pred.reshape(-1, pred.shape[-1])[:, i],
        squared=False
    )
    print(f'Feature {i + 1} MSE: {mse}')


def _plot_results(
        final_output_test,
        pred,
        filepath: str = None,
        view: bool = True,
        fontsize: int = 10
):
    import matplotlib.pyplot as plt

    features = final_output_test.shape[2]
    if features == 1:
        i = 0
        plt.plot(final_output_test.reshape(-1, final_output_test.shape[-1])[:, i], c='blue', label="measured")
        plt.plot(pred.reshape(-1, pred.shape[-1])[:, i], c='red', label="prediction")
        plt.legend()
        # plt.locator_params(nbins=3)

        plt.xlabel(f'Feature {i + 1} across all timesteps', fontsize=fontsize)
        plt.ylabel(f'F_{i + 1}', fontsize=fontsize)
        # ax.set_title('Title', fontsize=fontsize)
        mse = mean_squared_error(
            final_output_test.reshape(-1, final_output_test.shape[-1])[:, i],
            pred.reshape(-1, pred.shape[-1])[:, i],
            squared=False
        )
        print(f'Feature {i + 1} MSE: {mse}')
        if view:
            plt.show()
        if filepath is not None:
            plt.savefig(filepath)
    else:
        fig, axs = plt.subplots(int(features), 1, layout=None)
        aux = 0
        for ax, i in zip(axs.flat, range(features)):
            _examples_plots(ax, final_output_test, pred, i, fontsize)
            aux += 1
        if view:
            plt.show()
        if filepath is not None:
            fig.savefig(filepath)


def _evaluate_pred_global(
        y_test,
        y_pred,
        model_name=None
):
    list_aux = []
    name_aux = []
    _rmse = tkmtc.RootMeanSquaredError()
    _mae = tkmtc.MeanAbsoluteError()
    _mape = tkmtc.MeanAbsolutePercentageError()
    list_aux.append(float(_mae(y_test, y_pred)))
    name_aux.append('MAE')
    list_aux.append(float(_rmse(y_test, y_pred)))
    name_aux.append('RMSE')
    list_aux.append(float(_mape(y_test, y_pred)))
    name_aux.append('MAPE')
    list_aux.append(model_name)
    name_aux.append('Model')
    df_aux = pd.DataFrame([list_aux], columns=name_aux)
    print(df_aux)

    return df_aux


def _metrics_3D(
        y_colname,
        n_output,
        y_test,
        yhat,
        name_model=None,
        path_save: str = None,
        scaler=None
):
    import pandas as pd
    from sklearn.metrics import mean_squared_error, mean_absolute_error

    if scaler != None:
        d1, d2, d3 = y_test.shape[0], y_test.shape[1], y_test.shape[2]

        y_test = y_test.reshape(d1 * d2, d3)
        yhat = yhat.reshape(d1 * d2, d3)
        y_test = scaler.inverse_transform(y_test)
        yhat = scaler.inverse_transform(yhat)

        y_test = y_test.reshape(d1, d2, d3)
        yhat = yhat.reshape(d1, d2, d3)

    dict_values = {}
    for a in range(len(y_colname)):
        col_true, col_pred, col_mae, col_mse = [], [], [], []
        for i in range(n_output):
            col_true.append(f'True_{i}')
            col_pred.append(f'Pred_{i}')
            col_mae.append(f'MAE_{i}')
            col_mse.append(f'MSE_{i}')
        col_value = col_true + col_pred + col_mae + col_mse
        df_value = pd.DataFrame(
            columns=col_value,
            index=range(y_test.shape[0])
        )

        for jj in range(y_test.shape[0]):
            list_true, list_pred, list_mae, list_mse = [], [], [], []
            for m in range(n_output):
                true, pred = y_test[jj][:, a: a + 1][m], yhat[jj][:, a: a + 1][m]
                list_true.append(true[0])
                list_pred.append(pred[0])
                list_mae.append(mean_absolute_error(true, pred))
                list_mse.append(mean_squared_error(true, pred))
            list_value = list_true + list_pred + list_mae + list_mse
            df_value.iloc[jj] = list_value

        if path_save != None:
            key = y_colname[a]
            df_value.to_csv(
                f'{path_save}/{name_model}_{key}.csv',
                index=False
            )
        dict_values[y_colname[a]] = df_value

    list_mae_vec = []
    col_3d = ['MAE_3D', 'MSE_3D']
    col_2d = []
    for i in range(len(y_colname)):
        col_2d.append(f'MAE_2D_V{i}')
        col_2d.append(f'MSE_2D_V{i}')

    col_3d_2d = col_3d + col_2d
    df_value_3d = pd.DataFrame(
        columns=col_3d_2d,
        index=range(y_test.shape[0])
    )
    for ii in range(y_test.shape[0]):
        list_mae_3d, list_mse_3d = [], []
        list_mae_3d.append(mean_absolute_error(y_test[ii], yhat[ii]))
        list_mse_3d.append(mean_squared_error(y_test[ii], yhat[ii]))

        list_mae_2d, list_mse_2d = [], []
        for a in range(len(y_colname)):
            true, pred = y_test[ii][:, a: a + 1], yhat[ii][:, a: a + 1]
            list_mae_2d.append(mean_absolute_error(true, pred))
            list_mse_2d.append(mean_squared_error(true, pred))
        list_value_3d_2d = list_mae_3d + list_mse_3d + list_mae_2d + list_mse_2d

        df_value_3d.iloc[ii] = list_value_3d_2d

    if path_save != None:
        df_value.to_csv(
            f'{path_save}/{name_model}_3D.csv',
            index=False
        )
    return dict_values, df_value_3d


def _plot_boxplot_n_steps_future(dict_values_2D, df_values_3D):
    import matplotlib.pyplot as plt
    import seaborn as sns
    import re
    metrics = ['MAE', 'MSE']
    for i in metrics:
        filter = [x for x in list(df_values_3D.columns) if re.match(i, x)]
        df_aux = df_values_3D[filter]
        fig, ax = plt.subplots(figsize=(10, 5))
        boxplot = sns.boxplot(data=df_aux.astype(float), showfliers=False)
        # boxplot.axes.set_title("MAE en 3D y 2D", fontsize=16)
        boxplot.set_ylabel(i, fontsize=14)
        # boxplot.set_xlabel("Columnas", fontsize=14)
        plt.show()

    for k in metrics:
        i = 0
        fig, axes = plt.subplots(1, 4, figsize=(12, 3), constrained_layout=True)
        for x in list(dict_values_2D.resolution()):
            filter = [x for x in dict_values_2D[x].columns if re.match(k, x)]
            df_aux = dict_values_2D[x][filter]
            fig = sns.boxplot(data=df_aux, ax=axes[i], showfliers=False)
            fig.axes.set_title(x)
            fig.axes.set_ylabel(k)
            i += 1
        plt.show()


def reshape_test(type_mdl, dict_test):
    if type_mdl == 'MLP':
        X_test = dict_test['X']
        return X_test.reshape(X_test.shape[0], X_test.shape[1] * X_test.shape[2])
    if type_mdl == 'Conv1D':
        X_test = dict_test['X']
        return X_test.reshape(X_test.shape[0], X_test.shape[1], X_test.shape[2], 1)
    if type_mdl == 'Conv2D':
        X_test = dict_test['X']
        return X_test.reshape(X_test.shape[0], X_test.shape[1], X_test.shape[2], 1, 1)
    else:
        return dict_test['X']


def reshape_yhat(type_mdl, yhat, n_future, n_out_ft):
    if type_mdl == 'MLP':
        return yhat.reshape(yhat.shape[0], n_future, n_out_ft)
    else:
        return yhat

class _process_values_preliminary:

    def __init__(
            self,
            model,
            dict_test,
            config_data,
            config_sim,
            name_model=None
    ):
        self.model = model
        self.dict_test = dict_test
        self.config_data = config_data
        self.config_sim = config_sim
        self.name_model = name_model

    def get_values(
            self,
            type_mdl,
            filepath
    ):
        X_test = reshape_test(type_mdl, self.dict_test)
        X_test[np.isnan(X_test)] = value_miss

        yhat = self.model.predict(X_test)
        yhat = reshape_yhat(type_mdl, yhat, self.config_data['n_future'], self.config_data['n_out_ft'])
        yhat_inverse, y_test_inverse = _inverse_transform(yhat, self.dict_test, self.config_data['y_colname'])
        _evaluate_pred_global(y_test_inverse, yhat_inverse, self.name_model)
        if self.config_sim['plt_results']:
            _plot_results(y_test_inverse, yhat_inverse)
            _metrics_n_steps_for_future(y_test_inverse, yhat_inverse, self.config_data)
        if self.config_sim['plt_metrics']:
            dict_values_M1, df_value_3d_M1 = _metrics_3D(
                y_colname=self.config_data['y_colname'],
                n_output=self.config_data['n_future'],
                y_test=y_test_inverse,
                yhat=yhat_inverse
            )
            _plot_boxplot_n_steps_future(dict_values_M1, df_value_3d_M1)
        if self.config_sim['metrics']:
            scorer_dict = dict_metrics(y_test_inverse, yhat_inverse, self.config_data, self.name_model)
            return yhat_inverse, scorer_dict
        else:
            yhat_inverse

        return yhat_inverse


def _values_preliminary(model, dict_test, config_data, config_sim, name_model=None):
    yhat = model.predict(dict_test['X'])
    yhat_inverse, y_test_inverse = _inverse_transform(yhat, dict_test, config_data['y_colname'])
    _evaluate_pred_global(y_test_inverse, yhat_inverse, name_model)
    if config_sim['plt_results']:
        _plot_results(y_test_inverse, yhat_inverse)
        _metrics_n_steps_for_future(y_test_inverse, yhat_inverse, config_data)
    if config_sim['plt_metrics']:
        dict_values_M1, df_value_3d_M1 = _metrics_3D(
            y_colname=config_data['y_colname'],
            n_output=config_data['n_future'],
            y_test=y_test_inverse,
            yhat=yhat_inverse
        )
        _plot_boxplot_n_steps_future(dict_values_M1, df_value_3d_M1)
    if config_sim['metrics']:
        scorer_dict = dict_metrics(y_test_inverse, yhat_inverse, config_data, name_model)
        return yhat_inverse, scorer_dict
    else:
        yhat_inverse
    return yhat_inverse


def _values_preliminary_mlp(model, dict_test, config_data, name_model=None):
    X_test = dict_test['X']
    X_test = X_test.reshape(X_test.shape[0], config_data['n_past'] * config_data['n_inp_ft'])
    yhat = model.predict(X_test)
    yhat = yhat.reshape(yhat.shape[0], config_data['n_future'], config_data['n_out_ft'])
    yhat_inverse, y_test_inverse = _inverse_transform(yhat, dict_test, config_data['y_colname'])
    _evaluate_pred_global(y_test_inverse, yhat_inverse, name_model)
    if config_data['plt_results']:
        _plot_results(y_test_inverse, yhat_inverse)
        _metrics_n_steps_for_future(y_test_inverse, yhat_inverse, config_data)
    if config_data['plt_metrics']:
        dict_values_M1, df_value_3d_M1 = _metrics_3D(
            y_colname=config_data['y_colname'],
            n_output=config_data['n_future'],
            y_test=y_test_inverse,
            yhat=yhat_inverse
        )
        _plot_boxplot_n_steps_future(dict_values_M1, df_value_3d_M1)
    if config_data['metrics']:
        scorer_dict = dict_metrics(y_test_inverse, yhat_inverse, config_data, name_model)
        return yhat_inverse, scorer_dict
    else:
        yhat_inverse

    return yhat_inverse


def _values_preliminary_1D(model, dict_test, config, name_model=None):
    X_test = dict_test['X']
    X_test = X_test.reshape(X_test.shape[0], X_test.shape[1], X_test.shape[2], 1)
    yhat = model.predict(X_test)
    yhat = yhat.reshape(yhat.shape[0], yhat.shape[1], yhat.shape[2])
    yhat_inverse, y_test_inverse = _inverse_transform(yhat, dict_test, config['y_colname'])
    _evaluate_pred_global(y_test_inverse, yhat_inverse, name_model)
    if config['plt_results']:
        _plot_results(y_test_inverse, yhat_inverse)
        _metrics_n_steps_for_future(y_test_inverse, yhat_inverse, config)
    if config['plt_metrics']:
        dict_values_M1, df_value_3d_M1 = _metrics_3D(
            y_colname=config['y_colname'],
            n_output=config['n_future'],
            y_test=y_test_inverse,
            yhat=yhat_inverse
        )
        _plot_boxplot_n_steps_future(dict_values_M1, df_value_3d_M1)
    if config['metrics']:
        scorer_dict = dict_metrics(y_test_inverse, yhat_inverse, config, name_model)
        return yhat_inverse, scorer_dict
    else:
        yhat_inverse

    return yhat_inverse


def _values_preliminary_2D(model, dict_test, config, name_model=None):
    X_test = dict_test['X']
    X_test = X_test.reshape(X_test.shape[0], X_test.shape[1], X_test.shape[2], 1, 1)

    yhat = model.predict(X_test)
    yhat = yhat.reshape(yhat.shape[0], yhat.shape[1], yhat.shape[2])

    yhat_inverse, y_test_inverse = _inverse_transform(yhat, dict_test, config['y_colname'])
    _evaluate_pred_global(y_test_inverse, yhat_inverse, name_model)
    if config['plt_results']:
        _plot_results(y_test_inverse, yhat_inverse)
        _metrics_n_steps_for_future(y_test_inverse, yhat_inverse, config)
    if config['plt_metrics']:
        dict_values_M1, df_value_3d_M1 = _metrics_3D(
            y_colname=config['y_colname'],
            n_output=config['n_future'],
            y_test=y_test_inverse,
            yhat=yhat_inverse
        )
        _plot_boxplot_n_steps_future(dict_values_M1, df_value_3d_M1)
    if config['metrics']:
        scorer_dict = dict_metrics(y_test_inverse, yhat_inverse, config, name_model)
        return yhat_inverse, scorer_dict
    else:
        yhat_inverse

    return yhat_inverse


def _values_preliminary_mdn(model, dict_test, config, output_dim, n_mixtures, name_model=None):
    from mdn import sample_from_output

    yhat = model.predict(dict_test['X'])
    pred_dist = []
    for i in range(0, 10001):
        y_samples = np.apply_along_axis(sample_from_output, 1, yhat, output_dim, n_mixtures, temp=1.0)
        pred_dist.append(y_samples[0].ravel())

    yhat = pred_dist.reshape(pred_dist.shape[0], config['n_future'], config['n_out_ft'])
    yhat_inverse, y_test_inverse = _inverse_transform(yhat, dict_test, config['y_colname'])
    _evaluate_pred_global(y_test_inverse, yhat_inverse, name_model)
    if config['plt_results']:
        _plot_results(y_test_inverse, yhat_inverse)
        _metrics_n_steps_for_future(y_test_inverse, yhat_inverse, config)
    if config['plt_metrics']:
        dict_values_M1, df_value_3d_M1 = _metrics_3D(
            y_colname=config['y_colname'],
            n_output=config['n_future'],
            y_test=y_test_inverse,
            yhat=yhat_inverse
        )
        _plot_boxplot_n_steps_future(dict_values_M1, df_value_3d_M1)
    if config['metrics']:
        scorer_dict = dict_metrics(y_test_inverse, yhat_inverse, config, name_model)
        return yhat_inverse, scorer_dict
    else:
        yhat_inverse

    return yhat_inverse


def _values_rdr_score_mlp(model, dict_train, dict_test, config):
    # train
    X_train = dict_train['train']['X']

    # test
    X_test = dict_test['X']
    X_test = X_test.reshape(X_test.shape[0], config['n_past'] * config['n_inp_ft'])

    yhat = model.predict(X_test)
    yhat = yhat.reshape(yhat.shape[0], config['n_future'], config['n_out_ft'])
    yhat_inverse, y_test_inverse = _inverse_transform(yhat, dict_test, config['y_colname'])
    # test_rdr_scorer(X_train, yhat_inverse, y_test_inverse, config)


def dict_metrics(y_test_inverse, yhat_inverse, config_data, name_model):
    ytest_2d = y_test_inverse.reshape(y_test_inverse.shape[0] * y_test_inverse.shape[1], y_test_inverse.shape[2])
    yhat_2d = yhat_inverse.reshape(yhat_inverse.shape[0] * yhat_inverse.shape[1], yhat_inverse.shape[2])
    df_ytest = pd.DataFrame(ytest_2d, columns=config_data['y_colname'])
    df_yhat = pd.DataFrame(yhat_2d, columns=config_data['y_colname'])
    scorer_dict = {}
    for idx, y_colname in enumerate(config_data['y_colname']):
        scorer = calculate_metrics()
        scorer.fit(
            y_true=df_ytest[y_colname],
            y_pred=df_yhat[y_colname],
            model_name=y_colname + '_' + name_model
        )
        scorer_dict[y_colname] = scorer
    return scorer_dict


def _R_squared(y_true, y_pred):
    """
    R^2 (coefficient of determination) regression score function.
    Best possible score is 1.0, lower values are worse.
    Args:
        y_true ([np.array]): test samples
        y_pred ([np.array]): predicted samples
    Returns:
        [float]: R2
    """
    SS_res = tf.reduce_sum(tf.square(y_true - y_pred), axis=-1)
    SS_tot = tf.reduce_sum(tf.square(y_true - tf.reduce_mean(y_true, axis=-1)), axis=-1)
    return (1 - SS_res / (SS_tot + tf.keras.backend.epsilon()))


def _metrics_n_steps_for_future(y_test_inverse, yhat_inverse, config, view=True, filepath=None):
    import matplotlib.pyplot as plt
    _rmse = tkmtc.RootMeanSquaredError()
    _mape = tkmtc.MeanAbsolutePercentageError()
    _mae = tkmtc.MeanAbsoluteError()

    # yhat_inverse_time_step and y_test_inverse_time_step are both same dimension.
    time_step_list_yhat = [[] for i in range(config['n_future'])]
    time_step_list_y_test = [[] for i in range(config['n_future'])]
    for i in range(0, yhat_inverse.shape[0]):
        for j in range(0, yhat_inverse.shape[1]):
            time_step_list_yhat[j].append(list(yhat_inverse[i][j]))
            time_step_list_y_test[j].append(list(y_test_inverse[i][j]))
    yhat_time_step = np.array(time_step_list_yhat)
    yhat_time_step = yhat_time_step.reshape(yhat_time_step.shape[0], -1)
    y_test_time_step = np.array(time_step_list_y_test)
    y_test_time_step = y_test_time_step.reshape(y_test_time_step.shape[0], -1)
    # plotting
    mae_list, r2_list, rmse_list = [], [], []
    for i in range(0, config['n_future']):
        mae = _mae(y_test_time_step[i], yhat_time_step[i])
        r2 = _R_squared(y_test_time_step[i], yhat_time_step[i])
        rmse = _rmse(y_test_time_step[i], yhat_time_step[i])
        mae_list.append(mae)
        r2_list.append(r2)
        rmse_list.append(rmse)

    list_name = ['MAE', 'R2', 'RMSE']
    list_results = [mae_list, r2_list, rmse_list]

    dict_results = dict(zip(list_name, list_results))
    fig, axs = plt.subplots(3, 1, layout=None)
    aux = 0
    for key, values in dict_results.items():
        axs[aux].plot(range(0, config['n_future']), values, marker='o')
        axs[aux].set(ylabel=key, xlabel='number of steps in future')
        aux += 1
    if view:
        plt.show()
    if filepath is not None:
        fig.savefig(filepath)
