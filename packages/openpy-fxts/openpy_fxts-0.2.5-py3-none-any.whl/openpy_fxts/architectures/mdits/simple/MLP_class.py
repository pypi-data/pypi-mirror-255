# -*- coding: utf-8 -*-
# @Time    : 10/07/2023
# @Author  : Ing. Jorge Lara
# @Email   : jlara@iee.unsj.edu.ar
# @File    : ------------
# @Software: PyCharm

from openpy_fxts.base_tf import tkm, tkl, tf
from openpy_fxts.architectures.mdits.arch_dicts import _get_dict_mdits
from openpy_fxts.architectures.layers.layers_class import dense_multi_out, dense_drop
from openpy_fxts.base_tf import value_miss


class mask_dense(tkl.Layer):
    def __init__(self, units, activation):
        super().__init__()
        self.mask = tkl.Masking(mask_value=value_miss)
        self.dense = tkl.Dense(units=units, activation=activation)

    def call(self, inputs):
        x = self.mask(inputs)
        x = self.dense(x)
        return x


class mlp_dense_class(tkm.Model):

    def __init__(
            self,
            n_past=None,
            n_inp_ft=None,
            n_future=None,
            n_out_ft=None,
            config=None
    ):
        super(mlp_dense_class, self).__init__()
        if config is None:
            config = _get_dict_mdits('MLP_Dense').config_mlp()
        self.n_past = n_past
        self.n_inp_ft = n_inp_ft
        self.n_future = n_future
        self.n_out_ft = n_out_ft
        self.config = config
        self.hidden_input = []
        for _ in range(n_inp_ft):
            self.hidden_input.append(
                mask_dense(
                    units=config['input_layer']['units'],
                    activation=config['input_layer']['activation']
                )
            )
        self.hidden_dense = dense_drop(
            n_units=config['dense_layers']['units'],
            list_act=config['dense_layers']['activations'],
            use_drop=config['dropout']['activate'],
            rate=config['dropout']['rate']
        )
        self.dense_out = dense_multi_out(n_future, n_out_ft, config['output_layer']['activation'])

    def call(self, inputs, training=True, **kwargs):
        x_input = []
        for i, (layer_input) in enumerate(self.hidden_input):
            x_input.append(layer_input(inputs[i]))
        x = tkl.concatenate(x_input)
        x = self.hidden_dense(x)
        x = self.dense_out(x)
        return x




class _dense_drop_block(tkl.Layer):
    def __init__(self, units, activation, regularizer, dropout):
        super().__init__()
        self.dense = tkl.Dense(units=units, activation=activation, kernel_regularizer=tkr.L2(regularizer))
        self.dropout = tkl.Dropout(dropout)

    def call(self, inputs):
        x = self.dense(inputs)
        x = self.dropout(x)
        return x


class mlp_dense(tf.keras.Model):
    def __init__(
            self,
            n_future=None,
            n_out_ft=None,
            config=None
    ):
        super(mlp_dense, self).__init__()

        if config is None:
            config = {
                'layer_config': {
                    'hidden_dimensions': [50, 25, 25],
                    'hidden_activations': ['relu', 'relu', 'relu'],
                    'hidden_regularization': [None, None, None],
                },
                'dropout': 0.2,
                'layer_out': 'relu'
            }
        hidden_dimensions = config['layer_config']['hidden_dimensions']
        hidden_activations = config['layer_config']['hidden_activations']
        hidden_regularization = config['layer_config']['hidden_regularization']

        self.mask = tkl.Masking(mask_value=value_miss)
        self.hidden_layers = dict()
        for i, (unit, act, reg) in enumerate(zip(hidden_dimensions, hidden_activations, hidden_regularization)):
            self.hidden_layers['hidden_' + str(i)] = _dense_drop_block(unit, act, reg, config['dropout'])
        self.dense_out = tkl.Dense(n_future * n_out_ft, activation=config['layer_out'])

    def call(self, inputs, training=True, **kwargs):
        x = self.mask(inputs)
        for _, layer in self.hidden_layers.items():
            x = layer(x)
        x = self.dense_out(x)
        return x
