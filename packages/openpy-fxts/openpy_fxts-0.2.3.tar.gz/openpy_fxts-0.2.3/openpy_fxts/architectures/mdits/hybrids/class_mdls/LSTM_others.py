# -*- coding: utf-8 -*-
# @Time    : 10/07/2023
# @Author  : Ing. Jorge Lara
# @Email   : jlara@iee.unsj.edu.ar
# @File    : ------------
# @Software: PyCharm

from openpy_fxts.base_tf import tkm, tkl, value_miss


class lstm2_dense(tkm.Model):

    def __init__(
            self,
            n_future=None,
            n_out_ft=None,
            config=None
    ):
        super(lstm2_dense, self).__init__()
        if config is None:
            config = {
                'lstm': {
                    'units': 256,
                    'activation': 'relu'
                },
                'dropout': 0.2,
                'dense': {
                    'activation': 'linear'
                }
            }
        self.mask = tkl.Masking(mask_value=value_miss)
        self.lstm1 = tkl.LSTM(units=config['lstm']['units'], return_sequences=True)
        self.drop1 = tkl.Dropout(config['dropout'])
        self.lstm2 = tkl.LSTM(units=config['lstm']['units'], activation=config['lstm']['activation'])
        self.drop2 = tkl.Dropout(config['dropout'])
        self.dense1 = tkl.Dense(n_future * n_out_ft, activation=config['dense']['activation'])
        self.dense2 = tkl.Reshape((n_future, n_out_ft))

    def call(self, inputs, training=True, **kwargs):
        x = self.mask(inputs)
        x = self.lstm1(x)
        x = self.drop1(x)
        x = self.lstm2(x)
        x = self.drop2(x)
        x = self.dense1(x)
        x = self.dense2(x)
        return x


def lstm2_dense_model(
        n_past=None,
        n_inp_ft=None,
        n_future=None,
        n_out_ft=None):
    input_layer = tkl.Input(shape=(n_past, n_inp_ft))
    mask = tkl.Masking(mask_value=-1)(input_layer)
    lstm1 = tkl.LSTM(units=256, return_sequences=True)(mask)
    drop1 = tkl.Dropout(0.3)(lstm1)
    lstm2 = tkl.LSTM(units=256, activation='relu')(drop1)
    drop2 = tkl.Dropout(0.3)(lstm2)
    dense = tkl.Dense(units=(n_future * n_out_ft), activation='linear')(drop2)
    out_layer = tkl.Reshape((n_future, n_out_ft))(dense)
    return tkm.Model(inputs=input_layer, outputs=out_layer)
