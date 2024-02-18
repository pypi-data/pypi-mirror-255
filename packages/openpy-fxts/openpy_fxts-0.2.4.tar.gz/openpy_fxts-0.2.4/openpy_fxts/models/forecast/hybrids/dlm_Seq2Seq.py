# -*- coding: utf-8 -*-
# @Time    : 14/07/2023
# @Author  : Ing. Jorge Lara
# @Email   : jlara@iee.unsj.edu.ar
# @File    : ------------
# @Software: PyCharm
from openpy_fxts.baseline_mdls import base_class

import tensorflow as tf

from openpy_fxts.base_tf import tkm, tkl
from openpy_fxts.preprocessing_data.forecast.prepare_data import pre_processing_data
import keras.utils.vis_utils
from importlib import reload

reload(keras.utils.vis_utils)
from openpy_fxts.architectures.utils import callbacks, learning_curve
from openpy_fxts.architectures.utils import _values_preliminary_2D
from openpy_fxts.architectures.utils import mdl_characteristics

tkl = tf.keras.layers
tko = tf.keras.optimizers
tkm = tf.keras.models
tkloss = tf.keras.losses
tku = tf.keras.utils
tkr = tf.keras.regularizers


class Seq2Seq_RNN_class(base_class):

    def __init__(
            self,
            config_data=None,
            config_mdl=None,
            config_sim=None,
            config_arch=None,
            name_mdl='Seq2Seq_LSTM',
            type_mdl='seq2seq',
    ):
        super().__init__(config_data, config_mdl, config_sim, config_arch, name_mdl, type_mdl)
        return


class Seq2Seq_RNN2_class(base_class):

    def __init__(
            self,
            config_data=None,
            config_mdl=None,
            config_sim=None,
            config_arch=None,
            name_mdl='Seq2Seq_LSTM2',
            type_mdl='seq2seq',
    ):
        super().__init__(config_data, config_mdl, config_sim, config_arch, name_mdl, type_mdl)
        return


class Seq2Seq_RNN_Batch_Drop_class(base_class):

    def __init__(
            self,
            config_data=None,
            config_mdl=None,
            config_sim=None,
            config_arch=None,
            name_mdl='Seq2Seq_LSTM_Batch_Drop',
            type_mdl='seq2seq',
    ):
        super().__init__(config_data, config_mdl, config_sim, config_arch, name_mdl, type_mdl)
        return


class Seq2Seq_BiRNN_class(base_class):

    def __init__(
            self,
            config_data=None,
            config_mdl=None,
            config_sim=None,
            config_arch=None,
            name_mdl='Seq2Seq_BiLSTM',
            type_mdl='seq2seq',
    ):
        super().__init__(config_data, config_mdl, config_sim, config_arch, name_mdl, type_mdl)
        return


class Seq2Seq_BiRNN2_class(base_class):

    def __init__(
            self,
            config_data=None,
            config_mdl=None,
            config_sim=None,
            config_arch=None,
            name_mdl='Seq2Seq_BiLSTM2',
            type_mdl='seq2seq',
    ):
        super().__init__(config_data, config_mdl, config_sim, config_arch, name_mdl, type_mdl)
        return


class Seq2Seq_Conv1D_BiRNN_class(base_class):

    def __init__(
            self,
            config_data=None,
            config_mdl=None,
            config_sim=None,
            config_arch=None,
            name_mdl='Seq2Seq_Conv1D_BiLSTM',
            type_mdl='seq2seq',
    ):
        super().__init__(config_data, config_mdl, config_sim, config_arch, name_mdl, type_mdl)
        return


class Seq2Seq_Multi_Head_Conv1D_BiRNN_class(base_class):

    def __init__(
            self,
            config_data=None,
            config_mdl=None,
            config_sim=None,
            config_arch=None,
            name_mdl='Seq2Seq_Multi_Head_Conv1D_BiLSTM',
            type_mdl='seq2seq',
    ):
        super().__init__(config_data, config_mdl, config_sim, config_arch, name_mdl, type_mdl)
        return


class Seq2Seq_BiRNN_with_Attention_class(base_class):

    def __init__(
            self,
            config_data=None,
            config_mdl=None,
            config_sim=None,
            config_arch=None,
            name_mdl='Seq2Seq_BiLSTM_with_Attention',
            type_mdl='seq2seq',
    ):
        super().__init__(config_data, config_mdl, config_sim, config_arch, name_mdl, type_mdl)
        return


class Seq2Seq_RNN_with_Luong_Attention_class(base_class):

    def __init__(
            self,
            config_data=None,
            config_mdl=None,
            config_sim=None,
            config_arch=None,
            name_mdl='Seq2Seq_LSTM_with_Luong_Attention',
            type_mdl='seq2seq',
    ):
        super().__init__(config_data, config_mdl, config_sim, config_arch, name_mdl, type_mdl)
        return


class Seq2Seq_Conv2D_RNN_class:

    def __init__(self, config_data=None, config_mdl=None, config_sim=None):
        self.config_data = config_data
        self.n_past = config_data['n_past']
        self.n_future = config_data['n_future']
        self.n_inp_ft = config_data['n_inp_ft']
        self.n_out_ft = config_data['n_out_ft']
        # Parameters for model
        self.config_mdl = config_mdl
        self.optimizer = config_mdl['optimizer']
        self.loss = config_mdl['loss']
        self.metrics = config_mdl['metrics']
        self.batch_size = config_mdl['batch_size']  # Batch size for training.
        self.epochs = config_mdl['epochs']  # Number of epochs to train for.
        self.units = config_mdl['units']  # no of lstm units
        self.dropout = config_mdl['dropout']
        # Parameters for simulation
        self.config_sim = config_sim
        self.verbose = config_sim['verbose']
        self.patience = config_sim['patience']
        self.plot_history = config_sim['plt_history']
        self.preliminary = config_sim['preliminary']
        self.name_model = 'Seq2Seq_ConvLSTM2D'

    def build_model(self):
        model = tkm.Sequential()
        model.add(tkl.BatchNormalization(name='batch_norm_0', input_shape=(self.n_past, self.n_inp_ft, 1, 1)))
        model.add(tkl.ConvLSTM2D(
            name='conv_lstm_1',
            filters=64,
            kernel_size=(10, 1),
            padding='same',
            return_sequences=True)
        )
        model.add(tkl.Dropout(0.2, name='dropout_1'))
        model.add(tkl.BatchNormalization(name='batch_norm_1'))
        model.add(tkl.ConvLSTM2D(
            name='conv_lstm_2',
            filters=64,
            kernel_size=(5, 1),
            padding='same',
            return_sequences=False)
        )
        model.add(tkl.Dropout(0.1, name='dropout_2'))
        model.add(tkl.BatchNormalization(name='batch_norm_2'))
        model.add(tkl.Flatten())
        # Repeat Vector
        model.add(tkl.RepeatVector(self.n_future))
        #
        if (self.n_inp_ft - self.n_out_ft) == 0:
            aux = 1
        else:
            aux = self.n_inp_ft - self.n_out_ft
        model.add(tkl.Reshape((self.n_future, self.n_out_ft, aux, 64)))
        model.add(tkl.ConvLSTM2D(
            name='conv_lstm_3',
            filters=64,
            kernel_size=(10, 1),
            padding='same',
            return_sequences=True)
        )
        model.add(tkl.Dropout(0.1, name='dropout_3'))
        model.add(tkl.BatchNormalization(name='batch_norm_3'))
        model.add(tkl.ConvLSTM2D(
            name='conv_lstm_4',
            filters=64,
            kernel_size=(5, 1),
            padding='same',
            return_sequences=True)
        )
        model.add(tkl.TimeDistributed(tkl.Dense(units=1, name='dense_1', activation='relu')))
        # model.add(Dense(units=1, name = 'dense_2'))
        return model

    def train_model(
            self,
            filepath: str = None
    ):
        data = pre_processing_data(self.config_data, train=True, valid=True)
        pre_processed = data.transformer_data()
        model = Seq2Seq_Conv2D_RNN_class(self.config_data, self.config_mdl).build_model()
        model.compile(
            optimizer=self.optimizer,
            loss=self.loss,
            metrics=self.metrics
        )
        mdl_characteristics(model, self.config_sim, filepath)
        # Training
        X_train = pre_processed['train']['X']
        y_train = pre_processed['train']['y']
        X_train = X_train.reshape_out(X_train.shape[0], X_train.shape[1], X_train.shape[2], 1, 1)
        y_train = y_train.reshape_out(y_train.shape[0], y_train.shape[1], y_train.shape[2], 1, 1)

        X_valid = pre_processed['valid']['X']
        y_valid = pre_processed['valid']['y']
        X_valid = X_valid.reshape_out(X_valid.shape[0], X_valid.shape[1], X_valid.shape[2], 1, 1)
        y_valid = y_valid.reshape_out(y_valid.shape[0], y_valid.shape[1], y_valid.shape[2], 1, 1)

        history = model.fit(
            X_train,
            y_train,
            epochs=self.epochs,
            validation_data=(
                X_valid,
                y_valid
            ),
            batch_size=self.batch_size,
            verbose=self.verbose,
            callbacks=callbacks(filepath, weights=True)
        )
        if self.config_data['plt_history']:
            learning_curve(history, self.name_model, self.config_data['time_init'], filepath=filepath)
        if self.config_data['preliminary']:
            data = pre_processing_data(self.config_data, test=True)
            dict_test = data.transformer_data()
            _values_preliminary_2D(model, dict_test, self.config_data)
        return model

    def prediction(
            self,
            model
    ):
        data = pre_processing_data(self.config_data, test=True)
        dict_test = data.transformer_data()
        yhat = _values_preliminary_2D(model, dict_test, self.config_data)
        return yhat
