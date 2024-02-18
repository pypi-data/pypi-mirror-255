# -*- coding: utf-8 -*-
# @Time    : 10/07/2023
# @Author  : Ing. Jorge Lara
# @Email   : jlara@iee.unsj.edu.ar
# @File    : ------------
# @Software: PyCharm

from openpy_fxts.base_tf import tkm, tkl, value_miss,  reset_seeds, seed_value

reset_seeds(seed_value)


def rnn_dense(n_past, n_inp_ft, n_future, n_out_ft, config=None, drop=False, type: str ='GRU'):
    if type == 'RNN':
        mdl = tkl.RNN
    if type == 'GRU':
        mdl = tkl.GRU
    if type == 'LSTM':
        mdl = tkl.LSTM
    if config is None:
        config = {
            'layer_config': {
                'hidden_dimensions': [256, 256],
                'hidden_activations': ['relu', 'relu'],
                'hidden_sequences': [True, False]
            },
            'dropout': 0.3,
            'layer_out': 'relu'
        }
    dimensions = config['layer_config']['hidden_dimensions']
    activations = config['layer_config']['hidden_activations']
    sequences = config['layer_config']['hidden_sequences']
    input_train = tkl.Input(shape=(n_past, n_inp_ft))
    x = tkl.Masking(mask_value=value_miss)(input_train)
    for i, (unit, act, seq) in enumerate(zip(dimensions, activations, sequences)):
        x = mdl(units=unit, activation=act, return_sequences=seq)(x)
        if drop:
            x = tkl.Dropout(config['dropout'])(x)
    x = tkl.Dense(n_future * n_out_ft, activation=config['layer_out'])(x)
    x = tkl.Reshape((n_future, n_out_ft))(x)
    model = tkm.Model(inputs=input_train, outputs=x, name='GRU_Dense')
    return model
