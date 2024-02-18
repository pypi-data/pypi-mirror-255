import tensorflow as tf

import pandas as pd
import numpy as np
from .dtw_funcs import slow_dtw_distance
from dtaidistance import dtw
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib.pyplot as plt

tkm = tf.keras.metrics


def _tf_evaluate_forecast_global(y_test_inverse, yhat_inverse):
    _rmse = tkm.RootMeanSquaredError()
    _mae = tkm.MeanAbsoluteError()
    _mape = tkm.MeanAbsolutePercentageError()

    mae = _mae(y_test_inverse, yhat_inverse)
    print('MAE:', float(mae))
    rmse = _rmse(y_test_inverse, yhat_inverse)
    print('RMSE:', float(rmse))
    mape = _mape(y_test_inverse, yhat_inverse)
    print('MAPE:', float(mape))


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

        y_test = y_test.reshape_out(d1 * d2, d3)
        yhat = yhat.reshape_out(d1 * d2, d3)
        y_test = scaler.inverse_transform(y_test)
        yhat = scaler.inverse_transform(yhat)

        y_test = y_test.reshape_out(d1, d2, d3)
        yhat = yhat.reshape_out(d1, d2, d3)

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
    return 1 - SS_res / (SS_tot + tf.keras.backend.epsilon())


def _metrics_n_steps_for_future(y_test_inverse, yhat_inverse, config, view=True, filepath=None):
    import matplotlib.pyplot as plt
    _rmse = tkm.RootMeanSquaredError()
    _mape = tkm.MeanAbsolutePercentageError()
    _mae = tkm.MeanAbsoluteError()

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


class calculate_metrics:

    def __init__(self):
        return

    def fit(self, y_true, y_pred, model_name='MODEL'):
        self._y_true = y_true
        self._y_pred = y_pred
        self._model_name = model_name
        # Metrics
        self.mae = True
        self.rmse = True
        self.mse = True
        self.mape = True
        self.r2 = True
        self.dwt = False

        _rmse = tkm.RootMeanSquaredError()
        _mse = tkm.MeanAbsoluteError()
        _mae = tkm.MeanAbsoluteError()
        _mape = tkm.MeanAbsolutePercentageError()
        _accuracy = tkm.Accuracy()
        list_metrics = []
        name_metrics = []
        y_true_1d = y_true.ravel()
        y_pred_1d = y_pred.ravel()
        
        if self.mae:
            mae = _mae(y_true_1d, y_pred_1d)
            list_metrics.append(float(mae))
            name_metrics.append('MAE')
        if self.rmse:
            rmse = _rmse(y_true_1d, y_pred_1d)
            list_metrics.append(float(rmse))
            name_metrics.append('RMSE')
        if self.mse:
            mse = _mse(y_true_1d, y_pred_1d)
            list_metrics.append(float(mse))
            name_metrics.append('MSE')
        if self.mape:
            mape = _mape(y_true_1d, y_pred_1d)
            list_metrics.append(float(mape))
            name_metrics.append('MAPE')
        if self.r2:
            r2 = r2_score(y_true_1d, y_pred_1d)
            list_metrics.append(r2)
            name_metrics.append('R2')
        if self.dwt:
            dtw_distance_model = dtw.distance(y_true_1d, y_pred_1d)
            list_metrics.append(float(dtw_distance_model))
            name_metrics.append('DWT')

        df = pd.DataFrame([list_metrics], columns=name_metrics)
        list_aux = []
        for _ in range(len(list_metrics)):
            list_aux.append(0)
        df_scale = pd.DataFrame([list_aux], columns=name_metrics)
        df_all = pd.concat([df_scale, df], axis=0, ignore_index=True).reset_index(drop=True)

        self._model_df = df[name_metrics]
        self._model_df['MODEL_NAME'] = str(model_name)
        self._all_df = df_all[name_metrics]
        self._rw_df = df_scale.loc[df_scale['RMSE'] > 0][name_metrics]
        self._rw_df['MODEL_NAME'] = 'RandomWalk'
        self._all_df = df_all[name_metrics]
        self._def_viz = pd.concat([self._model_df, self._rw_df], axis=0, ignore_index=True).reset_index(drop=True)

    def rename_model(self, model_name):
        self._model_name = model_name
        self._model_df['MODEL_NAME'] = str(model_name)
        self._def_viz = pd.concat([self._model_df, self._rw_df], axis=0, ignore_index=True).reset_index(drop=True)

    def get_df_viz(self):
        return self._def_viz

    def add_rdr(
            self,
            rdr_object
    ):
        self._def_viz = pd.concat(
            [self._def_viz, rdr_object._def_viz],
            axis=0, ignore_index=True
        ).reset_index(drop=True)
        self._def_viz = self._def_viz.drop_duplicates()
        return self._def_viz

    def plot_rdr_rank(self, models=list([])):
        if len(models) == 0:
            models = self._def_viz
        models = models.append(
            pd.DataFrame([[0, 0, 1.0, 'Perfect Score']], index=[max(models.index) + 1], columns=models.columns))
        model_ranking = models.sort_values(by='RdR_SCORE', ascending=True)
        model_ranking['RdR_SCORE'] = model_ranking['RdR_SCORE'] * 100
        # model_ranking = model_ranking.loc[~model_ranking['MODEL_NAME'].isin(['PERFECT_SCORE', 'WORST_SCORE'])]
        colors = []
        for value in model_ranking.loc[:, 'RdR_SCORE']:  # keys are the names of the boys
            if value < 0:
                colors.append('r')
            elif value <= np.max(model_ranking.loc[model_ranking['MODEL_NAME'] == 'RandomWalk']['RdR_SCORE']):
                colors.append('y')
            else:
                colors.append('g')

        fig, ax = plt.subplots()
        fig.set_size_inches(8, 10, forward=True)
        ax.barh(model_ranking['MODEL_NAME'], model_ranking['RdR_SCORE'], color=colors, alpha=0.65)
        ax.tick_params(axis="y", labelsize=10)
        # ax.set_xticks(rotation = 60, fontsize = 8)
        # for i in enumerate('RMSE:' + model_ranking['LB_RMSE'].round(4).astype(str)):
        #    plt.text(i + 0, str(v), fontweight='bold')
        # find the values and append to list
        totals = []
        for i in ax.patches:
            totals.append(i.get_width())
        # set individual bar lables using above list
        # total = sum(totals)
        for i in ax.patches:
            # get_width pulls left or right; get_y pushes up or down
            ax.text(i.get_width(), i.get_y() + .38, \
                    str(round(i.get_width(), 2)) + '%', fontsize=12,
                    color='black', weight="bold"
                    )
        plt.title(
            'Model Ranking based on RdR score' + '\n'
            + 'Best possible model = 100%' + '\n'
            + '0% = Naïve RandomWalk' + '\n'
            + '< 0% = Worst than Naïve RandomWalk (Red)' + '\n'
            + '> 0% = Better than Naïve RandomWalk (Green)'
        )
        plt.tight_layout()

    def plot_rdr(
            self,
            models=list([]),
            scatter_size=80,
            scatter_label=True,
            scatter_label_size=6,
            scatter_alpha=0.65,
            figsize=(10, 10)
    ):
        if len(models) == 0:
            models = self._def_viz
        #############################################################################################
        ################### PLOT MODEL VALIDATION GRAPH GRID ########################################
        #############################################################################################
        models = models.append(
            pd.DataFrame([[0, 0, 1.0, 'Perfect Score']], index=[max(models.index) + 1], columns=models.columns))

        import matplotlib.patches as mpatches
        # rectangle = [(0,0),(0,1),(1,1),(1,0)]
        fig1 = plt.figure(figsize=figsize)
        ax1 = fig1.add_subplot(111, aspect='equal')
        ax1.add_patch(
            mpatches.Rectangle(
                (0, 0),
                self._rw_df['DTW'].value[0],
                self._rw_df['RMSE'].value[0],
                alpha=0.1,
                color='green',
                linestyle='--',
                linewidth=1.5,
                edgecolor='grey'
            )
        )
        ax2 = fig1.add_subplot(111, aspect='equal')
        ax2.add_patch(
            mpatches.Rectangle(
                (0, self._rw_df['RMSE'].value[0]),
                np.max(self._def_viz['DTW']) * 1.15,
                np.max(self._def_viz['RMSE']) * 1.15,
                alpha=0.07, color='red',
                edgecolor=None, linewidth=0
            )
        )
        ax3 = fig1.add_subplot(111, aspect='equal')
        ax3.add_patch(
            mpatches.Rectangle(
                (self._rw_df['DTW'].value[0], 0),
                np.max(self._def_viz['DTW']) * 1.15,
                self._rw_df['RMSE'].value[0],
                alpha=0.07,
                color='red',
                edgecolor=None,
                linewidth=0
            )
        )
        plt.scatter(
            self._rw_df['DTW'],
            self._rw_df['RMSE'],
            s=scatter_size,
            label='Naïve Random Walk Score',
            color='red'
        )
        for i in range(0, len(models)):
            model = pd.DataFrame(models.iloc[i:i + 1, :])
            # print(model)
            # print(model.columns.tolist())
            if (
                    (
                            model['DTW'].value[0] >= self._rw_df['DTW'].value[0]
                    ) or (
                    model['RMSE'].value[0] >= self._rw_df['RMSE'].value[0]
            )
            ):
                plt.scatter(
                    model['DTW'],
                    model['RMSE'],
                    color='red',
                    s=scatter_size,
                    label=model['MODEL_NAME'],
                    alpha=scatter_alpha
                )
            else:
                plt.scatter(
                    model['DTW'],
                    model['RMSE'],
                    color='green',
                    s=scatter_size,
                    label=model['MODEL_NAME'],
                    alpha=scatter_alpha
                )
            if scatter_label:
                if len(model['MODEL_NAME'][i]) > 15:
                    model_name = model['MODEL_NAME'][i][:15] + str('[...]')
                else:
                    model_name = model['MODEL_NAME'][i]
                plt.annotate(model_name, (model['DTW'][i], model['RMSE'][i]), fontsize=scatter_label_size)

        plt.ylim(0, np.max(self._def_viz['RMSE']) * 1.15)
        plt.xlim(0, np.max(self._def_viz['DTW']) * 1.15)
        plt.xlabel(
            'Dynamic Time Warping Distance' + '\n' +
            '(Metric for time series shape similarity, prediction vs test set)',
            fontsize=15
        )
        plt.ylabel(
            'RMSE score' + '\n' +
            '(Metric for penalized prediction errors on test set)',
            fontsize=10
        )
        plt.title(
            'MODELS A PERFORMANCE COMPARISON for multistep forecast in the future' +
            '\n' +
            'TIME SERIE' +
            '\n' +
            'RED ZONES: Not better than Naïve model' +
            '\n' +
            'GREEN ZONE: Better than Naïve model'
        )
        # plt.legend(loc='upper left', fontsize = 15)
        plt.show()
    # print('TEST')
    # plt.savefig('all_best_preds_test.png', dpi = 800)
    # plt.tight_layout()
