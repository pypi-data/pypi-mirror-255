from tcn import TCN
from openpy_fxts.architectures.layers.layers_class import dense_multi_out, time2vec_birnn_layer, multi_time2vec_birnn, type_rnn
from openpy_fxts.base_tf import tkl, tkm
from openpy_fxts.architectures.mdits.arch_dicts import _get_dict_mdits


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
                    'activation': None
                }
            }
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
        self.dense_out = dense_multi_out(
            n_future,
            n_out_ft,
            config['output_layer']['activation']
        )

    def call(self, inputs, training=True, **kwargs):
        x = self.tcn(inputs)
        x = self.bilstm(x)
        x = self.dense_out(x)
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
            config = _get_dict_mdits('time2vec_bilstm')
        self.hidden_layers = multi_time2vec_birnn(
            mdl=type_rnn(config['rnn_layers']['type']),
            output_dims=config['time2vec']['units'],
            units=config['rnn_layers']['units'],
            rnn_acts=config['rnn_layers']['activations'],
            return_seq=config['rnn_layers']['sequences'],
            is_drop=config['dropout']['activate'],
            rate=config['dropout']['rate'],
        )
        self.hidden_time2vec_birnn = time2vec_birnn_layer(
            mdl=type_rnn(config['rnn_layers']['type']),
            output_dim=config['time2vec']['units'][-1],
            unit=n_out_ft,
            rnn_act='tanh',
            rnn_seq=False,
            is_drop=config['dropout']['activate'],
            rate=config['dropout']['rate'],
        )
        self.dense_out = dense_multi_out(
            n_future,
            n_out_ft,
            config['output_layer']['activation']
        )

    def call(self, inputs, training=True, **kwargs):
        x = self.hidden_layers(inputs)
        x = self.hidden_time2vec_birnn(x)
        x = self.dense_out(x)
        return x