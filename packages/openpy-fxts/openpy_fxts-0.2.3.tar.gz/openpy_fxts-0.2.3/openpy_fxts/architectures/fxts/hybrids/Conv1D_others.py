from openpy_fxts.base_tf import tkm, tkl
from openpy_fxts.architectures.layers.layers_class import dense_multi_out, rnn_drop, type_rnn
from openpy_fxts.architectures.layers.layers_class import multi_rnn_drop, multi_conv1d_pool_flat_drop, multi_timedist_conv1d_flat
from openpy_fxts.architectures.layers.attention_class import attention
from openpy_fxts.architectures.fxts.arch_dicts import _get_dict_fxts


class conv1d_birnn_dense(tkm.Model):

    def __init__(
            self,
            n_future=None,
            n_out_ft=None,
            config=None
    ):
        super(conv1d_birnn_dense, self).__init__()
        if config is None:
            config = _get_dict_fxts('Conv1D_BiRNN').config_conv1d()
        self.n_future = n_future,
        self.n_out_ft = n_out_ft,
        self.config = config
        self.multi_hidden_conv1d = multi_conv1d_pool_flat_drop(
            filters=config['conv1d_layers']['filters'],
            kernels=config['conv1d_layers']['kernels'],
            activations=config['conv1d_layers']['activations'],
            paddings=config['conv1d_layers']['paddings'],
            use_drop=config['dropout']['activate'],
            rate=config['dropout']['rate'],
            maxpooling_1d=True,
            pool_size=config['conv1d_layers']['pool_size'],
            flatten=False
        )
        self.multi_hidden_rnn = multi_rnn_drop(
            mdl=type_rnn(config['rnn_layers']['type']),
            units=config['rnn_layers']['units'],
            activations=config['rnn_layers']['activations'],
            sequences=config['rnn_layers']['sequences'],
            bidirectional=config['rnn_layers']['bidirectional'],
            use_drop=config['dropout']['activate'],
            rate=config['dropout']['rate']
        )
        if config['dense_layer']['activation']:
            self.dense_layer = tkl.Dense(
                units=config['dense_layer']['units'],
                activation=config['dense_layer']['activation']
            )
            self.drop = tkl.Dropout(rate=config['dropout']['rate'])
        self.dense_out = dense_multi_out(
            n_future,
            n_out_ft,
            config['output_layer']['activation']
        )

    def call(self, inputs, training=True, **kwargs):
        x = self.multi_hidden_conv1d(inputs)
        x = self.multi_hidden_rnn(x)
        if self.config['dense_layer']['activation']:
            x = self.dense_layer(x)
            x = self.drop(x)
        x = self.dense_out(x)
        return x


class timedist_conv1d_birnn_dense(tkm.Model):

    def __init__(
            self,
            n_future=None,
            n_out_ft=None,
            config=None
    ):
        super(timedist_conv1d_birnn_dense, self).__init__()
        if config is None:
            config = _get_dict_fxts('TimeDist_Conv1D_BiRNN').config_conv1d()
        self.n_future = n_future,
        self.n_out_ft = n_out_ft,
        self.config = config
        self.multi_hidden_conv1d = multi_timedist_conv1d_flat(
            filters=config['conv1d_layers']['filters'],
            kernels=config['conv1d_layers']['kernels'],
            activations=config['conv1d_layers']['activations'],
            paddings=config['conv1d_layers']['paddings'],
            maxpooling_1d=config['conv1d_layers']['maxpooling'],
            pool_size=config['conv1d_layers']['pool_size']
        )
        self.rnn_layer = rnn_drop(
            mdl=type_rnn(config['rnn_layer']['type']),
            n_units=config['rnn_layer']['units'],
            activation=config['rnn_layer']['activation'],
            return_seq=config['rnn_layer']['sequences'],
            bidirectional=config['rnn_layer']['bidirectional']
        )
        if config['dropout']['activate']:
            self.drop = tkl.Dropout(rate=config['dropout']['rate'])
        self.dense_layer = tkl.Dense(
            units=config['dense_layer']['units'],
            activation=config['dense_layer']['activation']
        )
        self.dense_out = dense_multi_out(
            n_future,
            n_out_ft,
            config['output_layer']['activation']
        )

    def call(self, inputs, training=True, **kwargs):
        x = self.multi_hidden_conv1d(inputs)
        x = self.rnn_layer(x)
        if self.config['dropout']['activate']:
            x = self.drop(x)
        x = self.dense_layer(x)
        x = self.dense_out(x)
        return x


class conv1d_birnn_attention_dense(tkm.Model):

    def __init__(
            self,
            n_future=None,
            n_out_ft=None,
            config=None
    ):
        super(conv1d_birnn_attention_dense, self).__init__()
        if config is None:
            config = _get_dict_fxts('Conv1D_BiRNN_Attention').config_conv1d()
        self.n_future = n_future,
        self.n_out_ft = n_out_ft,
        self.config = config
        self.hidden_conv1d = multi_conv1d_pool_flat_drop(
            filters=config['conv1d_layers']['filters'],
            kernels=config['conv1d_layers']['kernels'],
            activations=config['conv1d_layers']['activations'],
            paddings=config['conv1d_layers']['paddings'],
            use_drop=config['dropout']['activate'],
            rate=config['dropout']['rate'],
            maxpooling_1d=True,
            pool_size=config['conv1d_layers']['pool_size'],
            flatten=False
        )
        self.multi_hidden_birnn = multi_rnn_drop(
            mdl=type_rnn(config['rnn_layers']['type']),
            units=config['rnn_layers']['units'],
            activations=config['rnn_layers']['activations'],
            sequences=config['rnn_layers']['sequences'],
            bidirectional=config['rnn_layers']['bidirectional'],
            use_drop=config['dropout']['activate'],
            rate=config['dropout']['rate'])
        self.attention = attention()
        self.flatten = tkl.Flatten()
        if config['dense_layer']['activation']:
            self.dense_layer = tkl.Dense(
                units=config['dense_layer']['units'],
                activation=config['dense_layer']['activation']
            )
            self.drop = tkl.Dropout(rate=config['dropout']['rate'])
        self.dense_out = dense_multi_out(
            n_future,
            n_out_ft,
            config['output_layer']['activation']
        )

    def call(self, inputs, training=True, **kwargs):
        x = self.hidden_conv1d(inputs)
        x = self.multi_hidden_birnn(x)
        x = self.attention(x)
        x = self.flatten(x)
        if self.config['dense_layer']['activation']:
            x = self.dense_layer(x)
            x = self.drop(x)
        x = self.dense_out(x)
        return x