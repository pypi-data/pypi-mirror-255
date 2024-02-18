# -*- coding: utf-8 -*-
# @Time    : 14/07/2023
# @Author  : Ing. Jorge Lara
# @Email   : jlara@iee.unsj.edu.ar
# @File    : ------------
# @Software: PyCharm

from openpy_fxts.base_tf import tkl, tkm
from openpy_fxts.architectures.layers.layers_class import type_rnn, rnn_drop, dense_multi_out, multi_rnn_drop
from openpy_fxts.architectures.mdits.arch_dicts import _get_dict_mdits


class birnn_dense_class(tkm.Model):

    def __init__(
            self,
            n_future=None,
            n_out_ft=None,
            config=None
    ):
        super(birnn_dense_class, self).__init__()
        if config is None:
            config = _get_dict_mdits(name_mdl='BiRNN_Dense').config_birnn()
        self.n_future = n_future
        self.n_out_ft = n_out_ft
        self.config = config
        self.hidden_rnn = multi_rnn_drop(
            mdl=type_rnn(config['rnn_layers']['type']),
            units=config['rnn_layers']['units'],
            activations=config['rnn_layers']['activations'],
            sequences=config['rnn_layers']['sequences'],
            bidirectional= config['rnn_layers']['bidirectional'],
            use_drop=config['dropout']['activate'],
            rate=config['dropout']['rate'],
            is_mask=True
        )
        if config['dense_layer']['activate']:
            self.hidden_dense = tkl.Dense(
                config['dense_layer']['units'],
                activation=config['dense_layer']['activation']
            )
        self.layer_output = dense_multi_out(n_future, n_out_ft, config['output_layer']['activation'])

    def call(self, inputs, training=True, **kwargs):
        x = self.hidden_rnn(inputs)
        if self.config['dense_layer']['activate']:
            x = self.hidden_dense(x)
        x = self.layer_output(x)
        return x


class multi_birnn_dense_class(tkm.Model):
    def __init__(
            self,
            n_past=None,
            n_inp_ft=None,
            n_future=None,
            n_out_ft=None,
            config=None
    ):
        super(multi_birnn_dense_class, self).__init__()
        if config is None:
            config = _get_dict_mdits('Multi_BiRNN_Dense').config_birnn()
        self.n_past = n_past
        self.n_inp_ft = n_inp_ft
        self.n_future = n_future
        self.n_out_ft = n_out_ft
        self.config = config
        mdl = type_rnn(config['multi_rnn_layers']['type'])
        self.hidden_inp = []
        dimensions = config['multi_rnn_layers']['units']
        activations = config['multi_rnn_layers']['activations']
        sequences = config['multi_rnn_layers']['sequences']
        self.hidden_rnn_dict = dict()
        for i in range(n_inp_ft):
            dict_rnn = {}
            for j, (unit, act, seq) in enumerate(zip(dimensions, activations, sequences)):
                dict_rnn['' + str(j)] = rnn_drop(
                    mdl=mdl,
                    n_units=unit,
                    activation=act,
                    return_seq=seq,
                    bidirectional=config['multi_rnn_layers']['bidirectional']
                )
            self.hidden_rnn_dict['' + str(i)] = dict_rnn
        self.concat = tkl.Concatenate(axis=1)
        if config['dropout']['activate']:
            self.drop1 = tkl.Dropout(config['dropout']['rate'])
        self.hidden_rnn = mdl(
            units=config['rnn_layer']['units'],
            activation=config['rnn_layer']['activation'],
            return_sequences=config['rnn_layer']['sequences']
        )
        if config['dropout']['activate']:
            self.drop2 = tkl.Dropout(config['dropout']['rate'])
        if config['dense_layer']['activate']:
            self.hidden_dense = tkl.Dense(
                config['dense_layer']['units'],
                activation=config['dense_layer']['activation']
            )
        self.dense_out = dense_multi_out(n_future, n_out_ft, config['output_layer']['activation'])

    def call(self, inputs, training=True, **kwargs):
        head_list = []
        for _, dict_aux in self.hidden_rnn_dict.items():
            for i, (_, layer_rnn) in enumerate(dict_aux.items()):
                if i == 0:
                    y = layer_rnn(inputs)
                else:
                    y = layer_rnn(y)
            head_list.append(y)
        x = self.concat(head_list)
        x = tkl.Reshape((head_list[0].shape[1], self.n_inp_ft))(x)
        if self.config['dropout']['activate']:
            x = self.drop1(x)
        x = self.hidden_rnn(x)
        if self.config['dropout']['activate']:
            x = self.drop2(x)
        if self.config['dense_layer']['activate']:
            x = self.hidden_dense(x)
        x = self.dense_out(x)
        return x


