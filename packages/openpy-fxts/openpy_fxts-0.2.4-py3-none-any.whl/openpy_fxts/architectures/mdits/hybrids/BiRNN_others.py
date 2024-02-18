# -*- coding: utf-8 -*-
# @Time    : 14/07/2023
# @Author  : Ing. Jorge Lara
# @Email   : jlara@iee.unsj.edu.ar
# @File    : ------------
# @Software: PyCharm

from openpy_fxts.base_tf import tkm, tkl
from openpy_fxts.architectures.layers.layers_class import type_rnn, dense_multi_out, rnn_drop
from openpy_fxts.architectures.layers.layers_class import multi_conv1d_pool_flat_drop, multi_rnn_drop
from openpy_fxts.architectures.layers.layers_class import dense_reshape_conv1d_multi_out
from openpy_fxts.architectures.layers.layers_class import multi_rnn_attention_conv1d, multi_birnn_multihead_attention_conv1d
from openpy_fxts.architectures.mdits.arch_dicts import _get_dict_mdits


class birnn_timedist_dense_class(tkm.Model):

    def __init__(
            self,
            n_future=None,
            n_out_ft=None,
            config=None
    ):
        super(birnn_timedist_dense_class, self).__init__()
        if config is None:
            config = _get_dict_mdits('BiRNN_TimeDist_Dense').config_birnn()
        self.n_future = n_future
        self.n_out_ft = n_out_ft
        self.config = config
        units = config['timedist_dense_layers']['units']
        activations = config['timedist_dense_layers']['activations']
        self.hidden_rnn = rnn_drop(
            mdl=type_rnn(config['rnn_layer']['type']),
            n_units=config['rnn_layer']['units'],
            activation=config['rnn_layer']['activations'],
            return_seq=config['rnn_layer']['sequences'],
            bidirectional=config['rnn_layer']['bidirectional'],
        )
        self.hidden_timedist_dense = []
        for j, (unit, act) in enumerate(zip(units, activations)):
            self.hidden_timedist_dense.append(tkl.TimeDistributed(tkl.Dense(units=unit, activation=act)))
        self.flatten = tkl.Flatten()
        self.hidden_dense = tkl.Dense(
            config['dense_layer']['units'],
            activation=config['dense_layer']['activation']
        )
        if config['dropout']['activate']:
            self.drop = tkl.Dropout(config['dropout']['rate'])
        self.layer_output = dense_multi_out(n_future, n_out_ft, config['output_layer']['activation'])

    def call(self, inputs, training=True, **kwargs):
        x = self.hidden_rnn(inputs)
        for layer in self.hidden_timedist_dense:
            x = layer(x)
        x = self.flatten(x)
        x = self.hidden_dense(x)
        if self.config['dropout']['activate']:
            x = self.drop(x)
        x = self.layer_output(x)
        return x


class birnn_conv1d_dense(tkm.Model):

    def __init__(
            self,
            n_future=None,
            n_out_ft=None,
            config=None
    ):
        super(birnn_conv1d_dense, self).__init__()
        if config is None:
            config = _get_dict_mdits('BiRNN_Conv1D').config_birnn()
        self.n_future = n_future,
        self.n_out_ft = n_out_ft,
        self.config = config
        self.multi_hidden_birnn = multi_rnn_drop(
            mdl=type_rnn(config['rnn_layers']['type']),
            units=config['rnn_layers']['units'],
            activations=config['rnn_layers']['activations'],
            sequences=config['rnn_layers']['sequences'],
            bidirectional=config['rnn_layers']['bidirectional'],
            use_drop=config['dropout']['activate'],
            rate=config['dropout']['rate']
        )
        self.multi_hidden_conv1d = multi_conv1d_pool_flat_drop(
            filters=config['conv1d_layers']['filters'],
            kernels=config['conv1d_layers']['kernels'],
            activations=config['conv1d_layers']['activations'],
            paddings=config['conv1d_layers']['paddings'],
            use_drop=config['dropout']['activate'],
            rate=config['dropout']['rate'],
            maxpooling_1d=True,
            pool_global=True,
            pool_size=config['conv1d_layers']['pool_size'],
            flatten=True)

        self.dense_conv1d_out = dense_reshape_conv1d_multi_out(
            n_future,
            n_out_ft,
            config['output_layer']['activation'],
            'same'
        )

    def call(self, inputs, training=True, **kwargs):
        x = self.multi_hidden_birnn(inputs)
        x = self.multi_hidden_conv1d(x)
        x = self.dense_conv1d_out(x)
        return x


class birnn_bahdanau_attention_conv1d_dense(tkm.Model):

    def __init__(
            self,
            n_future=None,
            n_out_ft=None,
            config=None
    ):
        super(birnn_bahdanau_attention_conv1d_dense, self).__init__()
        if config is None:
            config = _get_dict_mdits('BiRNN_Bahdanau_Attention_Conv1D').config_birnn()
        self.config = config
        self.multi_hidden_layers = multi_rnn_attention_conv1d(
            mdl=type_rnn(config['rnn_layers']['type']),
            bidirectional=config['rnn_layers']['bidirectional'],
            units=config['rnn_layers']['units'],
            rnn_act=config['rnn_layers']['activations'],
            return_seq=config['rnn_layers']['sequences'],
            att_type='Bahdanau',
            kernel_reg=config['attention']['kernel_reg'],
            bias_reg=config['attention']['bias_reg'],
            reg_weight=config['attention']['reg_weight'],
            n_filters=config['conv1d_layers']['filters'],
            kernels=config['conv1d_layers']['kernels'],
            conv_act=config['conv1d_layers']['activations'],
            paddings=config['conv1d_layers']['paddings'],
            simple_pool=True,
            global_pool=False,
            pool_size=config['conv1d_layers']['pool_size']
        )
        self.flatten = tkl.Flatten()
        if config['dropout']['activate']:
            self.dropout = tkl.Dropout(config['dropout']['rate'])
        self.dense_out = dense_multi_out(
            n_future,
            n_out_ft,
            config['output_layer']['activation']
        )

    def call(self, inputs, training=True, **kwargs):
        x = self.multi_hidden_layers(inputs)
        x = self.flatten(x)
        if self.config['dropout']['activate']:
            x = self.dropout(x)
        x = self.dense_out(x)
        return x


class birnn_luong_attention_conv1d_dense(tkm.Model):

    def __init__(
            self,
            n_future=None,
            n_out_ft=None,
            config=None
    ):
        super(birnn_luong_attention_conv1d_dense, self).__init__()
        if config is None:
            config = _get_dict_mdits('BiRNN_Luong_Attention_Conv1D').config_birnn()
        self.config = config
        self.multi_hidden_layers = multi_rnn_attention_conv1d(
            mdl=type_rnn(config['rnn_layers']['type']),
            bidirectional=config['rnn_layers']['bidirectional'],
            units=config['rnn_layers']['units'],
            rnn_act=config['rnn_layers']['activations'],
            return_seq=config['rnn_layers']['sequences'],
            att_type='Luong',
            kernel_reg=config['attention']['kernel_reg'],
            bias_reg=config['attention']['bias_reg'],
            reg_weight=config['attention']['reg_weight'],
            n_filters=config['conv1d_layers']['filters'],
            kernels=config['conv1d_layers']['kernels'],
            conv_act=config['conv1d_layers']['activations'],
            paddings=config['conv1d_layers']['paddings'],
            simple_pool=True,
            global_pool=False,
            pool_size=config['conv1d_layers']['pool_size']
        )
        self.flatten = tkl.Flatten()
        if config['dropout']['activate']:
            self.dropout = tkl.Dropout(config['dropout']['rate'])
        self.dense_out = dense_multi_out(
            n_future,
            n_out_ft,
            config['output_layer']['activation']
        )

    def call(self, inputs, training=True, **kwargs):
        x = self.multi_hidden_layers(inputs)
        x = self.flatten(x)
        if self.config['dropout']['activate']:
            x = self.dropout(x)
        x = self.dense_out(x)
        return x


class birnn_multihead_attention_conv1d_dense(tkm.Model):

    def __init__(
            self,
            n_future=None,
            n_out_ft=None,
            config=None
    ):
        super(birnn_multihead_attention_conv1d_dense, self).__init__()
        if config is None:
            config = _get_dict_mdits('BiRNN_MultiHeadAttention_Conv1D').config_birnn()
        self.config = config
        self.multi_hidden_layers = multi_birnn_multihead_attention_conv1d(
            mdl=type_rnn(config['rnn_layers']['type']),
            bidirectional=config['rnn_layers']['bidirectional'],
            units=config['rnn_layers']['units'],
            rnn_act=config['rnn_layers']['activations'],
            return_seq=config['rnn_layers']['sequences'],
            att_type='MultiHeadAttention',
            num_heads=config['attention']['num_heads'],
            key_dim=config['attention']['key_dim'],
            dropout=config['attention']['dropout'],
            n_filters=config['conv1d_layers']['filters'],
            kernels=config['conv1d_layers']['kernels'],
            conv_act=config['conv1d_layers']['activations'],
            paddings=config['conv1d_layers']['paddings'],
            simple_pool=True,
            global_pool=False,
            pool_size=config['conv1d_layers']['pool_size']
        )
        self.flatten = tkl.Flatten()
        if config['dropout']['activate']:
            self.dropout = tkl.Dropout(config['dropout']['rate'])
        self.dense_out = dense_multi_out(
            n_future,
            n_out_ft,
            config['output_layer']['activation']
        )

    def call(self, inputs, training=True, **kwargs):
        x = self.multi_hidden_layers(inputs)
        x = self.flatten(x)
        if self.config['dropout']['activate']:
            x = self.dropout(x)
        x = self.dense_out(x)
        return x



