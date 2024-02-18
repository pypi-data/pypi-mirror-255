# -*- coding: utf-8 -*-
# @Time    : 10/07/2023
# @Author  : Ing. Jorge Lara
# @Email   : jlara@iee.unsj.edu.ar
# @File    : ------------
# @Software: PyCharm

from tcn import TCN
from openpy_fxts.base_tf import tkm, tkl, value_miss
from openpy_fxts.architectures.layers.layers_class import Time2Vec


class tcn_bilstm(tkm.Model):

    def __init__(
            self,
            n_future=None,
            n_out_ft=None,
            config=None
    ):
        super(tcn_bilstm, self).__init__()
        if config is None:
            config = {
                'dense': {
                    'activation': 'linear'
                }
            }
        self.mask = tkl.Masking(mask_value=value_miss)
        self.tcn = TCN(
            nb_filters=32,
            kernel_size=16,
            nb_stacks=4,
            dilations=(2, 4, 8, 16, 32, 64),
            padding='causal',
            use_skip_connections=True,
            dropout_rate=0.0,
            activation='tanh',
            kernel_initializer='glorot_uniform',
            use_batch_norm=False,
            use_layer_norm=False,
            use_weight_norm=False,
            return_sequences=True
        )
        self.bilstm = tkl.Bidirectional(
            tkl.LSTM(
                units=n_out_ft,
                return_sequences=False,
                activation='tanh'
            )
        )
        self.dense1 = tkl.Dense(
            n_future * n_out_ft,
            activation=config['dense']['activation']
        )
        self.dense2 = tkl.Reshape((n_future, n_out_ft))

    def call(self, inputs, training=True, **kwargs):
        x = self.mask(inputs)
        x = self.tcn(x)
        x = self.bilstm(x)
        x = self.dense1(x)
        x = self.dense2(x)
        return x


class time2vec_bilstm(tkm.Model):

    def __init__(
            self,
            n_future=None,
            n_out_ft=None,
            config=None
    ):
        super(time2vec_bilstm, self).__init__()
        if config is None:
            config = {
                'time2vec': {
                    'units': 256
                },
                'dense': {
                    'activation': 'linear'
                }
            }
        self.mask = tkl.Masking(mask_value=value_miss)
        self.time2vec = Time2Vec(
            config['time2vec']['units']
        )
        self.bilstm = tkl.Bidirectional(
            tkl.LSTM(
                units=n_out_ft,
                return_sequences=False,
                activation='tanh'
            )
        )
        self.dense1 = tkl.Dense(
            n_future * n_out_ft,
            activation=config['dense']['activation']
        )
        self.dense2 = tkl.Reshape((n_future, n_out_ft))

    def call(self, inputs, training=True, **kwargs):
        x = self.mask(inputs)
        x = self.time2vec(x)
        x = self.bilstm(x)
        x = self.dense1(x)
        x = self.dense2(x)
        return x