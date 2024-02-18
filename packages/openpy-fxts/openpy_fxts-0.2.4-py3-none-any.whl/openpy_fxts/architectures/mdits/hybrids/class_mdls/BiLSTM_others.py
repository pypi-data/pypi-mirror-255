# -*- coding: utf-8 -*-
# @Time    : 10/07/2023
# @Author  : Ing. Jorge Lara
# @Email   : jlara@iee.unsj.edu.ar
# @File    : ------------
# @Software: PyCharm

from openpy_fxts.base_tf import tkm, tkl, tkr, value_miss
from openpy_fxts.architectures.layers.attention_class import SeqSelfAttention


class bilstm_dense(tkm.Model):

    def __init__(
            self,
            n_future=None,
            n_out_ft=None,
            config=None
    ):
        super(bilstm_dense, self).__init__()
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
        self.bilstm = tkl.Bidirectional(
            tkl.LSTM(
                units=config['bilstm']['units'],
                activation=config['bilstm']['activation'],
                recurrent_activation=config['bilstm']['recurrent_activation'],
                return_sequences=False
            )
        )
        self.dropout = tkl.Dropout(config['dropout'])
        self.dense1 = tkl.Dense(
            n_future * n_out_ft,
            activation=config['dense']['activation']
        )
        self.dense2 = tkl.Reshape((n_future, n_out_ft))

    def call(self, inputs, training=True, **kwargs):
        x = self.mask(inputs)
        x = self.bilstm(x)
        x = self.dropout(x)
        x = self.dense1(x)
        x = self.dense2(x)
        return x


def bilstm_dense_model(
        n_past=None,
        n_inp_ft=None,
        n_future=None,
        n_out_ft=None):

    input_layer = tkl.Input(shape=(n_past, n_inp_ft))
    mask = tkl.Masking(mask_value=-1)(input_layer)
    bilstm = tkl.Bidirectional(tkl.LSTM(units=256, return_sequences=True))(mask)
    conv1d_1 = tkl.Conv1D(filters=64, kernel_size=3, activation='relu', padding='same')(bilstm)
    glob_pool = tkl.GlobalAveragePooling1D()(conv1d_1)
    drop = tkl.Dropout(0.3)(glob_pool)
    dense = tkl.Dense(units=(n_future * n_out_ft), activation='linear')(drop)
    reshape = tkl.Reshape((n_future, n_out_ft))(dense)
    out_layer = tkl.Conv1D(n_out_ft, 1, padding='same')(reshape)

    return tkm.Model(inputs=input_layer, outputs=out_layer)


class bilstm_conv1d_dense(tkm.Model):

    def __init__(
            self,
            n_future=None,
            n_out_ft=None,
            config=None
    ):
        super(bilstm_conv1d_dense, self).__init__()
        if config is None:
            config = {
                'bilstm': {
                    'units': 256,
                    },
                'conv1d': {
                    'filter': 64,
                    'kernel': 3,
                    'activation': 'relu',
                    'padding': 'same'
                },
                'dropout': 0.3,
                'dense': {
                    'activation': 'relu'
                }
            }
        self.mask = tkl.Masking(mask_value=value_miss)
        self.bilstm = tkl.Bidirectional(
            tkl.LSTM(
                units=config['bilstm']['units'],
                return_sequences=True
            )
        )
        self.conv1 = tkl.Conv1D(
            filters=config['conv1d']['filter'],
            kernel_size=config['conv1d']['kernel'],
            activation=config['conv1d']['activation'],
            padding=config['conv1d']['padding']
        )
        self.pool1d = tkl.GlobalAveragePooling1D()
        self.dropout = tkl.Dropout(config['dropout'])
        self.dense1 = tkl.Dense(
            n_future * n_out_ft,
            activation=config['dense']['activation']
        )
        self.dense2 = tkl.Reshape((n_future, n_out_ft))
        self.conv2 = tkl.Conv1D(n_out_ft, 1, padding='same')

    def call(self, inputs, training=True, **kwargs):
        x = self.mask(inputs)
        x = self.bilstm(x)
        x = self.conv1(x)
        x = self.pool1d(x)
        x = self.dropout(x)
        x = self.dense1(x)
        x = self.dense2(x)
        x = self.conv2(x)
        return x


class bilstm_bahdanau_attention_conv1d_dense(tkm.Model):

    def __init__(
            self,
            n_future=None,
            n_out_ft=None,
            config=None
    ):
        super(bilstm_bahdanau_attention_conv1d_dense, self).__init__()
        if config is None:
            config = {
                'bilstm1': {'units': 64},
                'conv1d_1': {
                    'filter': 128,
                    'kernel': 3,
                    'activation': 'relu',
                    'padding': 'same'
                },
                'dropout': 0.5,
                'bilstm2': {'units': 32},
                'conv1d_2': {
                    'filter': 256,
                    'kernel': 3,
                    'activation': 'relu',
                    'padding': 'same'
                },
                'dense': {'activation': 'relu'}
            }
        self.mask = tkl.Masking(mask_value=value_miss)
        self.bilstm1 = tkl.Bidirectional(
            tkl.LSTM(
                units=config['bilstm1']['units'],
                return_sequences=True
            )
        )
        self.attention1 = SeqSelfAttention(
            attention_type=SeqSelfAttention.ATTENTION_TYPE_ADD,
            kernel_regularizer=tkr.l2(1e-4),
            bias_regularizer=tkr.l1(1e-4),
            attention_regularizer_weight=1e-4,
            name='Attention1'
        )
        self.conv1 = tkl.Conv1D(
            filters=config['conv1d_1']['filter'],
            kernel_size=config['conv1d_1']['kernel'],
            activation=config['conv1d_1']['activation'],
            padding=config['conv1d_1']['padding']
        )
        self.maxpool1d = tkl.MaxPool1D()
        self.bilstm2 = tkl.Bidirectional(
            tkl.LSTM(
                units=config['bilstm2']['units'],
                return_sequences=True
            )
        )
        self.attention2 = SeqSelfAttention(
            attention_type=SeqSelfAttention.ATTENTION_TYPE_ADD,
            kernel_regularizer=tkr.l2(1e-4),
            bias_regularizer=tkr.l1(1e-4),
            attention_regularizer_weight=1e-4,
            name='Attention2'
        )
        self.conv2 = tkl.Conv1D(
            filters=config['conv1d_2']['filter'],
            kernel_size=config['conv1d_2']['kernel'],
            activation=config['conv1d_2']['activation'],
            padding=config['conv1d_2']['padding']
        )
        self.glob_maxpool1d = tkl.GlobalAveragePooling1D()
        self.dropout = tkl.Dropout(config['dropout'])
        self.dense1 = tkl.Dense(
            n_future * n_out_ft,
            activation=config['dense']['activation']
        )
        self.dense2 = tkl.Reshape((n_future, n_out_ft))
        self.conv3 = tkl.Conv1D(n_out_ft, 1, padding='same')

    def call(self, inputs, training=True, **kwargs):
        x = self.mask(inputs)
        x = self.bilstm1(x)
        x = self.attention1(x)
        x = self.conv1(x)
        x = self.maxpool1d(x)
        x = self.bilstm2(x)
        x = self.attention2(x)
        x = self.conv2(x)
        x = self.glob_maxpool1d(x)
        x = self.dropout(x)
        x = self.dense1(x)
        x = self.dense2(x)
        x = self.conv3(x)
        return x


class bilstm_multihead_attention_conv1d_dense(tkm.Model):

    def __init__(
            self,
            n_future=None,
            n_out_ft=None,
            config=None
    ):
        super(bilstm_multihead_attention_conv1d_dense, self).__init__()
        if config is None:
            config = {
                'bilstm1': {'units': 64},
                'conv1d_1': {
                    'filter': 128,
                    'kernel': 3,
                    'activation': 'relu',
                    'padding': 'same'
                },
                'dropout': 0.5,
                'bilstm2': {'units': 64},
                'conv1d_2': {
                    'filter': 256,
                    'kernel': 3,
                    'activation': 'relu',
                    'padding': 'same'
                },
                'dense': {'activation': 'relu'}
            }
        self.mask = tkl.Masking(mask_value=value_miss)
        self.bilstm1 = tkl.Bidirectional(
            tkl.LSTM(
                units=config['bilstm1']['units'],
                return_sequences=True
            )
        )
        self.multihead_attention = tkl.MultiHeadAttention(num_heads=2, key_dim=2, dropout=0.1)
        self.conv1 = tkl.Conv1D(
            filters=config['conv1d_1']['filter'],
            kernel_size=config['conv1d_1']['kernel'],
            activation=config['conv1d_1']['activation'],
            padding=config['conv1d_1']['padding']
        )
        self.maxpool1d = tkl.MaxPool1D()
        self.bilstm2 = tkl.Bidirectional(
            tkl.LSTM(
                units=config['bilstm2']['units'],
                return_sequences=True
            )
        )
        self.conv2 = tkl.Conv1D(
            filters=config['conv1d_2']['filter'],
            kernel_size=config['conv1d_2']['kernel'],
            activation=config['conv1d_2']['activation'],
            padding=config['conv1d_2']['padding']
        )
        self.glob_maxpool1d = tkl.GlobalAveragePooling1D()
        self.dropout = tkl.Dropout(config['dropout'])
        self.dense = tkl.Dense(
            n_future * n_out_ft,
            activation=config['dense']['activation']
        )
        self.reshape = tkl.Reshape((n_future, n_out_ft))
        self.conv3 = tkl.Conv1D(filters=n_out_ft, kernel_size=1, padding='same')

    def call(self, inputs, training=True, **kwargs):
        x = self.mask(inputs)
        x = self.bilstm1(x)
        x = self.multihead_attention(x, x)
        x = self.conv1(x)
        x = self.maxpool1d(x)
        x = self.bilstm2(x)
        x = self.multihead_attention(x, x)
        x = self.conv2(x)
        x = self.glob_maxpool1d(x)
        x = self.dropout(x)
        x = self.dense(x)
        x = self.reshape(x)
        x = self.conv3(x)
        return x


class bilstm_luong_attention_conv1d_dense(tkm.Model):

    def __init__(
            self,
            n_future=None,
            n_out_ft=None,
            config=None
    ):
        super(bilstm_luong_attention_conv1d_dense, self).__init__()
        if config is None:
            config = {
                'bilstm1': {'units': 64},
                'conv1d_1': {
                    'filter': 128,
                    'kernel': 3,
                    'activation': 'relu',
                    'padding': 'same'
                },
                'dropout': 0.5,
                'bilstm2': {'units': 32},
                'conv1d_2': {
                    'filter': 256,
                    'kernel': 3,
                    'activation': 'relu',
                    'padding': 'same'
                },
                'dense': {'activation': 'relu'}
            }
        self.mask = tkl.Masking(mask_value=value_miss)
        self.bilstm1 = tkl.Bidirectional(
            tkl.LSTM(
                units=config['bilstm1']['units'],
                return_sequences=True
            )
        )
        self.attention1 = SeqSelfAttention(
            attention_type=SeqSelfAttention.ATTENTION_TYPE_MUL,
            kernel_regularizer=tkr.l2(1e-4),
            bias_regularizer=tkr.l1(1e-4),
            attention_regularizer_weight=1e-4,
            name='Attention1'
        )
        self.conv1 = tkl.Conv1D(
            filters=config['conv1d_1']['filter'],
            kernel_size=config['conv1d_1']['kernel'],
            activation=config['conv1d_1']['activation'],
            padding=config['conv1d_1']['padding']
        )
        self.maxpool1d = tkl.MaxPool1D()
        self.bilstm2 = tkl.Bidirectional(
            tkl.LSTM(
                units=config['bilstm2']['units'],
                return_sequences=True
            )
        )
        self.attention2 = SeqSelfAttention(
            attention_type=SeqSelfAttention.ATTENTION_TYPE_MUL,
            kernel_regularizer=tkr.l2(1e-4),
            bias_regularizer=tkr.l1(1e-4),
            attention_regularizer_weight=1e-4,
            name='Attention2'
        )
        self.conv2 = tkl.Conv1D(
            filters=config['conv1d_2']['filter'],
            kernel_size=config['conv1d_2']['kernel'],
            activation=config['conv1d_2']['activation'],
            padding=config['conv1d_2']['padding']
        )
        self.glob_maxpool1d = tkl.GlobalAveragePooling1D()
        self.dropout = tkl.Dropout(config['dropout'])
        self.dense1 = tkl.Dense(
            n_future * n_out_ft,
            activation=config['dense']['activation']
        )
        self.dense2 = tkl.Reshape((n_future, n_out_ft))
        self.conv3 = tkl.Conv1D(n_out_ft, 1, padding='same')

    def call(self, inputs, training=True, **kwargs):
        x = self.mask(inputs)
        x = self.bilstm1(x)
        x = self.attention1(x)
        x = self.conv1(x)
        x = self.maxpool1d(x)
        x = self.bilstm2(x)
        x = self.attention2(x)
        x = self.conv2(x)
        x = self.glob_maxpool1d(x)
        x = self.dropout(x)
        x = self.dense1(x)
        x = self.dense2(x)
        x = self.conv3(x)
        return x