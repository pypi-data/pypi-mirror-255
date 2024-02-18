# -*- coding: utf-8 -*-
# @Time    : 10/07/2023
# @Author  : Ing. Jorge Lara
# @Email   : jlara@iee.unsj.edu.ar
# @File    : ------------
# @Software: PyCharm

from openpy_fxts.base_tf import tkm, tkl, value_miss
from openpy_fxts.architectures.layers.attention_class import attention


class conv1D_dense(tkm.Model):

    def __init__(
            self,
            n_future=None,
            n_out_ft=None,
            config=None
    ):
        super(conv1D_dense, self).__init__()
        if config is None:
            config = {
                'conv1d': {
                    'filter': 256,
                    'kernel': 2,
                    'activation': 'relu',
                    'padding': 'causal'
                },
                'dropout': 0.3,
                'pooling': 2,
                'dense': {
                    'activation': 'relu'
                }
            }
        self.mask = tkl.Masking(mask_value=value_miss)
        self.conv1 = tkl.Conv1D(
            filters=config['conv1d']['filter'],
            kernel_size=config['conv1d']['kernel'],
            activation=config['conv1d']['activation'],
            padding=config['conv1d']['padding'],

            dilation_rate=2
        )
        self.conv2 = tkl.Conv1D(
            filters=config['conv1d']['filter'],
            kernel_size=config['conv1d']['kernel'],
            activation=config['conv1d']['activation'],
            padding=config['conv1d']['padding']
        )
        self.conv3 = tkl.Conv1D(
            filters=config['conv1d']['filter'],
            kernel_size=config['conv1d']['kernel'],
            activation=config['conv1d']['activation'],
            padding=config['conv1d']['padding']
        )
        self.dropout = tkl.Dropout(config['dropout'])
        self.maxpool = tkl.MaxPooling1D(pool_size=config['pooling'])
        self.flatten = tkl.Flatten()
        self.dense = tkl.Dense(
            units=128,
            activation=config['dense']['activation']
        )
        self.dense1 = tkl.Dense(
            n_future * n_out_ft,
            activation=config['dense']['activation']
        )
        self.dense2 = tkl.Reshape((n_future, n_out_ft))

    def call(self, inputs, training=True, **kwargs):
        x = self.mask(inputs)
        x = self.conv1(x)
        x = self.conv2(x)
        x = self.conv3(x)
        x = self.dropout(x)
        x = self.maxpool(x)
        x = self.flatten(x)
        x = self.dense(x)
        x = self.dense1(x)
        x = self.dense2(x)
        return x


class conv1D_lstm_dense(tkm.Model):

    def __init__(
            self,
            n_future=None,
            n_out_ft=None,
            config=None
    ):
        super(conv1D_lstm_dense, self).__init__()
        if config is None:
            config = {
                'conv1d': {
                    'filter': 256,
                    'kernel': 2,
                    'activation': 'relu',
                    'padding': 'causal'
                },
                'dropout': 0.3,
                'lstm': {
                    'units': 256,
                    'activation': 'relu'
                },
                'dense': {
                    'activation': 'relu'
                }
            }
        self.mask = tkl.Masking(mask_value=value_miss)
        self.conv1 = tkl.Conv1D(
            filters=config['conv1d']['filter'],
            kernel_size=config['conv1d']['kernel'],
            activation=config['conv1d']['activation'],
            padding=config['conv1d']['padding'],
            dilation_rate=2
        )
        self.conv2 = tkl.Conv1D(
            filters=config['conv1d']['filter'],
            kernel_size=config['conv1d']['kernel'],
            activation=config['conv1d']['activation'],
            padding=config['conv1d']['padding']
        )
        self.conv3 = tkl.Conv1D(
            filters=config['conv1d']['filter'],
            kernel_size=config['conv1d']['kernel'],
            activation=config['conv1d']['activation'],
            padding=config['conv1d']['padding']
        )
        self.dropout = tkl.Dropout(config['dropout'])
        self.lstm = tkl.LSTM(
            units=config['lstm']['units'],
            activation=config['lstm']['activation'],
        )
        self.dense = tkl.Dense(
            units=128,
            activation=config['dense']['activation']
        )
        self.dense1 = tkl.Dense(
            n_future * n_out_ft,
            activation=config['dense']['activation']
        )
        self.dense2 = tkl.Reshape((n_future, n_out_ft))

    def call(self, inputs, training=True, **kwargs):
        x = self.mask(inputs)
        x = self.conv1(x)
        x = self.conv2(x)
        x = self.conv3(x)
        x = self.dropout(x)
        x = self.lstm(x)
        x = self.dense1(x)
        x = self.dense2(x)
        return x


class conv1D_bilstm_dense(tkm.Model):

    def __init__(
            self,
            n_future=None,
            n_out_ft=None,
            config=None
    ):
        super(conv1D_bilstm_dense, self).__init__()
        if config is None:
            config = {
                'conv1d': {
                    'filter': 64,
                    'kernel': 3,
                    'activation': 'relu',
                    'padding': 'causal'
                },
                'dropout': 0.3,
                'bilstm': {
                    'units': 256,
                    'activation': 'relu'
                },
                'dense': {
                    'activation': 'linear'
                }
            }
        self.mask = tkl.Masking(mask_value=value_miss)
        self.conv1 = tkl.Conv1D(
            filters=config['conv1d']['filter'],
            kernel_size=config['conv1d']['kernel'],
            activation=config['conv1d']['activation'],
            padding=config['conv1d']['padding'],
            dilation_rate=2
        )
        self.conv2 = tkl.Conv1D(
            filters=config['conv1d']['filter'],
            kernel_size=config['conv1d']['kernel'],
            activation=config['conv1d']['activation'],
            padding=config['conv1d']['padding']
        )
        self.conv3 = tkl.Conv1D(
            filters=config['conv1d']['filter'],
            kernel_size=config['conv1d']['kernel'],
            activation=config['conv1d']['activation'],
            padding=config['conv1d']['padding']
        )
        self.drop1 = tkl.Dropout(config['dropout'])
        self.bilstm = tkl.Bidirectional(
            tkl.LSTM(
                units=config['bilstm']['units'],
                activation=config['bilstm']['activation'],
            )
        )
        self.drop2 = tkl.Dropout(config['dropout'])
        self.flatten = tkl.Flatten()
        self.dense1 = tkl.Dense(
            n_future * n_out_ft,
            activation=config['dense']['activation']
        )
        self.dense2 = tkl.Reshape((n_future, n_out_ft))

    def call(self, inputs, training=True, **kwargs):
        x = self.mask(inputs)
        x = self.conv1(x)
        x = self.conv2(x)
        x = self.conv3(x)
        x = self.drop1(x)
        x = self.bilstm(x)
        x = self.drop2(x)
        x = self.flatten(x)
        x = self.dense1(x)
        x = self.dense2(x)
        return x


class conv1D_bilstm_attention_dense(tkm.Model):

    def __init__(
            self,
            n_future=None,
            n_out_ft=None,
            config=None
    ):
        super(conv1D_bilstm_attention_dense, self).__init__()
        if config is None:
            config = {
                'conv1d': {
                    'filter': 64,
                    'kernel': 3,
                    'activation': 'relu',
                    'padding': 'causal'
                },
                'dropout': 0.3,
                'bilstm': {
                    'units': 256
                },
                'dense': {
                    'activation': 'linear'
                }
            }
        self.mask = tkl.Masking(mask_value=value_miss)
        self.conv1 = tkl.Conv1D(
            filters=config['conv1d']['filter'],
            kernel_size=config['conv1d']['kernel'],
            activation=config['conv1d']['activation'],
            padding=config['conv1d']['padding'],
            dilation_rate=2
        )
        self.drop1 = tkl.Dropout(config['dropout'])
        self.bilstm = tkl.Bidirectional(
            tkl.LSTM(
                units=config['bilstm']['units'],
                return_sequences=True
            )
        )
        self.drop2 = tkl.Dropout(config['dropout'])
        self.attention = attention()
        self.flatten = tkl.Flatten()
        self.dense1 = tkl.Dense(
            n_future * n_out_ft,
            activation=config['dense']['activation']
        )
        self.dense2 = tkl.Reshape((n_future, n_out_ft))

    def call(self, inputs, training=True, **kwargs):
        x = self.mask(inputs)
        x = self.conv1(x)
        x = self.drop1(x)
        x = self.bilstm(x)
        x = self.drop2(x)
        x = self.attention(x)
        x = self.flatten(x)
        x = self.dense1(x)
        x = self.dense2(x)
        return x
