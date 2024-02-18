# -*- coding: utf-8 -*-
# @Time    : 21/07/2023
# @Author  : Ing. Jorge Lara
# @Email   : jlara@iee.unsj.edu.ar
# @File    : ------------
# @Software: PyCharm

from openpy_fxts.base_tf import tkm, tkl
from openpy_fxts.architectures.fxts.arch_dicts import _get_dict_fxts
from openpy_fxts.architectures.layers.layers_class import type_rnn, multi_rnn_drop, multi_conv1d_pool_flat_drop


class encdec_birnn(tkm.Model):

    def __init__(
            self,
            n_future=None,
            n_out_ft=None,
            config=None
    ):
        super(encdec_birnn, self).__init__()
        if config is None:
            config = _get_dict_fxts('EncDec_BiRNN').config_encdec()
        self.n_future = n_future,
        self.n_out_ft = n_out_ft,
        self.config = config
        self.encoder = multi_rnn_drop(
            mdl=type_rnn(config['encoder']['rnn_layers']['type']),
            units=config['encoder']['rnn_layers']['units'],
            activations=config['encoder']['rnn_layers']['activations'],
            sequences=config['encoder']['rnn_layers']['sequences'],
            bidirectional=config['encoder']['rnn_layers']['bidirectional'],
            use_drop=config['dropout']['activate'],
            rate=config['dropout']['rate']
        )
        self.rep_vec = tkl.RepeatVector(n_future)
        self.decoder = multi_rnn_drop(
            mdl=type_rnn(config['decoder']['rnn_layers']['type']),
            units=config['decoder']['rnn_layers']['units'],
            activations=config['decoder']['rnn_layers']['activations'],
            sequences=config['decoder']['rnn_layers']['sequences'],
            bidirectional=config['decoder']['rnn_layers']['bidirectional'],
            use_drop=config['dropout']['activate'],
            rate=config['dropout']['rate'])
        self.time_dense = tkl.TimeDistributed(tkl.Dense(n_out_ft))

    def call(self, inputs):
        encdec = self.encoder(inputs)
        encdec = self.rep_vec(encdec)
        encdec = self.decoder(encdec)
        encdec = self.time_dense(encdec)
        return encdec


class encdec_conv1d_birnn(tkm.Model):

    def __init__(
            self,
            n_future=None,
            n_out_ft=None,
            config=None
    ):
        super(encdec_conv1d_birnn, self).__init__()
        if config is None:
            config = _get_dict_fxts('EncDec_Conv1D_BiRNN').config_encdec()
        self.n_future = n_future,
        self.n_out_ft = n_out_ft,
        self.config = config
        self.encoder = multi_conv1d_pool_flat_drop(
            filters=config['encoder']['conv1d_layers']['filters'],
            kernels=config['encoder']['conv1d_layers']['kernels'],
            activations=config['encoder']['conv1d_layers']['activations'],
            paddings=config['encoder']['conv1d_layers']['paddings'],
            use_drop=config['dropout']['activate'],
            rate=config['dropout']['rate'],
            maxpooling_1d=True,
            pool_size=config['encoder']['conv1d_layers']['pool_size'],
            flatten=True
        )
        self.rep_vec = tkl.RepeatVector(n_future)
        self.decoder = multi_rnn_drop(
            mdl=type_rnn(config['decoder']['rnn_layers']['type']),
            units=config['decoder']['rnn_layers']['units'],
            activations=config['decoder']['rnn_layers']['activations'],
            sequences=config['decoder']['rnn_layers']['sequences'],
            bidirectional=config['decoder']['rnn_layers']['bidirectional'],
            use_drop=config['dropout']['activate'],
            rate=config['dropout']['rate']
        )
        self.time_dense = tkl.TimeDistributed(tkl.Dense(n_out_ft))

    def call(self, inputs):
        encdec = self.encoder(inputs)
        encdec = self.rep_vec(encdec)
        encdec = self.decoder(encdec)
        encdec = self.time_dense(encdec)
        return encdec