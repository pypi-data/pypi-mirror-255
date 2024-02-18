# -*- coding: utf-8 -*-
# @Time    : 10/07/2023
# @Author  : Ing. Jorge Lara
# @Email   : jlara@iee.unsj.edu.ar
# @File    : ------------
# @Software: PyCharm

from openpy_fxts.base_tf import tkm, tkl, value_miss
from openpy_fxts.architectures.layers.layers_class import StackedSciNet


class lstm_stacked(tkm.Model):

    def __init__(
            self,
            n_future=None,
            n_out_ft=None,
            config=None
    ):
        super(lstm_stacked, self).__init__()
        if config is None:
            config = {
                'bilstm': {
                    'units': 256,
                    'activation': 'tanh',
                    'recurrent_activation': 'relu'
                },
                'dropout': 0.3,
                'dense': {
                    'activation': 'linear'
                }
            }
        self.mask = tkl.Masking(mask_value=value_miss)
        self.lstm1 = tkl.LSTM(units=256, activation='relu', return_sequences=True)
        self.lstm2 = tkl.LSTM(units=256, activation='relu')
        self.dense1 = tkl.Dense(units=128)
        self.dropout = tkl.Dropout(0.3)
        self.dense2 = tkl.Dense(n_future * n_out_ft, activation='relu')
        self.reshape = tkl.Reshape((n_future, n_out_ft))
        self.conv1d = tkl.Conv1D(n_out_ft, 1, padding='same')

    def call(self, inputs, training=True, **kwargs):
        x = self.mask(inputs)
        x = self.lstm1(x)
        x = self.lstm2(x)
        x = self.dense1(x)
        x = self.dropout(x)
        x = self.dense2(x)
        x = self.reshape(x)
        x = self.conv1d(x)
        return x

class bilstm_stacked(tkm.Model):

    def __init__(
            self,
            n_future=None,
            n_out_ft=None,
            config=None
    ):
        super(bilstm_stacked, self).__init__()
        if config is None:
            config = {
                'bilstm': {
                    'units': 256,
                    'activation': 'tanh',
                    'recurrent_activation': 'relu'
                },
                'dropout': 0.3,
                'dense': {
                    'activation': 'linear'
                }
            }
        self.mask = tkl.Masking(mask_value=value_miss)
        self.bilstm1 = tkl.Bidirectional(tkl.LSTM(units=128, activation='relu', return_sequences=True))
        self.bilstm2 = tkl.Bidirectional(tkl.LSTM(units=128, activation='relu'))
        self.dense1 = tkl.Dense(units=128)
        self.dropout = tkl.Dropout(0.3)
        self.dense2 = tkl.Dense(n_future * n_out_ft, activation='relu')
        self.reshape = tkl.Reshape((n_future, n_out_ft))
        self.conv1d = tkl.Conv1D(n_out_ft, 1, padding='same')

    def call(self, inputs, training=True, **kwargs):
        x = self.mask(inputs)
        x = self.bilstm1(x)
        x = self.bilstm2(x)
        x = self.dense1(x)
        x = self.dropout(x)
        x = self.dense2(x)
        x = self.reshape(x)
        x = self.conv1d(x)
        return x


class stackedscinet(tkm.Model):
    def __init__(
            self,
            n_future=None,
            n_out_ft=None,
            config=None
    ):
        super(stackedscinet, self).__init__()
        if config is None:
            config = {
                'bilstm': {
                    'units': 256,
                    'activation': 'tanh',
                    'recurrent_activation': 'relu'
                },
                'dropout': 0.3,
                'dense': {
                    'activation': 'linear'
                }
            }
        self.mask = tkl.Masking(mask_value=value_miss)
        self.stackedscinet = StackedSciNet(
            horizon=n_future,
            features=n_out_ft,
            stacks=2,
            levels=4,
            h=4,
            kernel_size=5
        )

    def call(self, inputs, training=True, **kwargs):
        x = self.mask(inputs)
        x = self.stackedscinet(x)
        return x


