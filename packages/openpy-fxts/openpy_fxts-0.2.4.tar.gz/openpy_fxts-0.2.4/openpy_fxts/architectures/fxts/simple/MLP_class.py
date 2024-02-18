# -*- coding: utf-8 -*-
# @Time    : 14/07/2023
# @Author  : Ing. Jorge Lara
# @Email   : jlara@iee.unsj.edu.ar
# @File    : ------------
# @Software: PyCharm

from openpy_fxts.base_tf import tkm, tkl, tkr
from openpy_fxts.architectures.fxts.arch_dicts import _get_dict_fxts
from openpy_fxts.architectures.layers.layers_class import dense_multi_out, dense_drop


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
            config = _get_dict_fxts('MLP_Dense').config_mlp()
        self.n_past = n_past
        self.n_inp_ft = n_inp_ft
        self.n_future = n_future
        self.n_out_ft = n_out_ft
        self.config = config
        self.hidden_input = []
        for _ in range(n_inp_ft):
            self.hidden_input.append(
                tkl.Dense(
                    units=config['input_layer']['units'],
                    activation=config['input_layer']['activation'],
                    kernel_regularizer=tkr.L1L2(
                        l1=config['input_layer']['l1'],
                        l2=config['input_layer']['l2']
                    )
                )
            )
        self.hidden_dense = dense_drop(
            n_units=config['dense_layers']['units'],
            list_act=config['dense_layers']['activations'],
            l1=config['dense_layers']['l1'],
            l2=config['dense_layers']['l2'],
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