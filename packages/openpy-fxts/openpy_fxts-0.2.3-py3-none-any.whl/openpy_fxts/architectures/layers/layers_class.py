# -*- coding: utf-8 -*-
# @Time    : 14/07/2023
# @Author  : Ing. Jorge Lara
# @Email   : jlara@iee.unsj.edu.ar
# @File    : ------------
# @Software: PyCharm

from typing import Tuple
from openpy_fxts.base_tf import tf, tkl, K, tkr, value_miss
from openpy_fxts.architectures.layers.attention_class import SeqSelfAttention


def type_rnn(name: str = None):
    if name == 'RNN':
        return tkl.SimpleRNN
    if name == 'LSTM':
        return tkl.LSTM
    if name == 'GRU':
        return tkl.GRU
    else:
        return tkl.GRU


class dense_drop(tkl.Layer):

    def __init__(
            self,
            n_units: int = None,
            list_act: str = None,
            l1=None,
            l2=None,
            use_drop:
            bool = False,
            rate: float = None
    ):
        super(dense_drop, self).__init__()
        self.is_drop = use_drop
        self.hidden_dense, self.hidden_drop = [], []
        for j, (unit, act) in enumerate(zip(n_units, list_act)):
            self.hidden_dense.append(tkl.Dense(units=unit, activation=act, kernel_regularizer=tkr.L1L2(l1=l1, l2=l2)))
            if use_drop:
                self.hidden_drop.append(tkl.Dropout(rate))

    def call(self, x):
        if self.is_drop:
            for _, (dense, drop) in enumerate(zip(self.hidden_dense, self.hidden_drop)):
                x = dense(x)
                x = drop(x)
        else:
            for _, (dense) in enumerate(self.hidden_dense):
                x = dense(x)
        return x


class multi_timedist_conv1d_flat(tkl.Layer):

    def __init__(
            self,
            filters: list = None,
            kernels: list = None,
            activations: str = None,
            paddings: str = None,
            dilation_rate: int = None,
            maxpooling_1d: bool = True,
            pool_size: int = 2,
            is_mask: bool = False

    ):
        super(multi_timedist_conv1d_flat, self).__init__()
        self.maxpooling_1d = maxpooling_1d
        self.is_mask = is_mask
        if is_mask:
            self.mask = tkl.Masking(mask_value=value_miss)
        self.hidden_timedist_conv1d = []
        for i, (f, k, a, p) in enumerate(zip(filters, kernels, activations, paddings)):
            if i == 0 and dilation_rate is None:
                self.hidden_timedist_conv1d.append(
                    tkl.TimeDistributed(tkl.Conv1D(filters=f, kernel_size=k, activation=a, padding=p, dilation_rate=2))
                )
            else:
                self.hidden_timedist_conv1d.append(
                    tkl.TimeDistributed(tkl.Conv1D(filters=f, kernel_size=k, activation=a, padding=p))
                )
        if maxpooling_1d:
            self.maxpool = tkl.TimeDistributed(tkl.MaxPooling1D(pool_size=pool_size))
        self.timedist_flatten = tkl.TimeDistributed(tkl.Flatten())

    def call(self, x):
        '''
        if self.is_mask:
            x = self.mask(x)
        '''
        for j, (layer) in enumerate(self.hidden_timedist_conv1d):
            if j == 0:
                x = layer(x)
            else:
                x = layer(x)
        if self.maxpooling_1d:
            x = self.maxpool(x)
        x = self.timedist_flatten(x)
        return x


class multi_conv1d_pool_flat_drop(tkl.Layer):

    def __init__(
            self,
            filters: list = None,
            kernels: list = None,
            activations: str = None,
            paddings: str = None,
            dilation_rate: list = None,
            use_drop: bool = False,
            rate: float = 0.3,
            maxpooling_1d: bool = True,
            pool_simple: bool = True,
            pool_global: bool = False,
            pool_size: int = 2,
            flatten: bool = True,
            is_mask: bool = False
    ):
        super(multi_conv1d_pool_flat_drop, self).__init__()
        self.is_drop = use_drop
        self.flatten = flatten
        self.maxpooling_1d = maxpooling_1d
        self.is_mask = is_mask
        if is_mask:
            self.mask = tkl.Masking(mask_value=value_miss)
        self.conv1d = []
        for i, (f, k, a, p) in enumerate(zip(filters, kernels, activations, paddings)):
            if i == 0 and dilation_rate is None:
                self.conv1d.append(tkl.Conv1D(filters=f, kernel_size=k, activation=a, padding=p, dilation_rate=2))
            else:
                self.conv1d.append(tkl.Conv1D(filters=f, kernel_size=k, activation=a, padding=p))
        if maxpooling_1d:
            if pool_simple:
                self.maxpooling_1d = tkl.MaxPooling1D(pool_size)
            elif pool_global:
                self.maxpooling_1d = tkl.GlobalAveragePooling1D(pool_size)
            else:
                self.maxpooling_1d = tkl.MaxPooling1D(pool_size)
        if flatten:
            self.flatten = tkl.Flatten()
        if use_drop:
            self.drop = tkl.Dropout(rate)


    def call(self, x):
        if self.is_mask:
            x = self.mask(x)
        for layer in self.conv1d:
            x = layer(x)
        if self.maxpooling_1d:
            x = self.maxpooling_1d(x)
        if self.flatten:
            x = self.flatten(x)
        if self.is_drop:
            x = self.drop(x)
        return x


class dense_multi_out(tkl.Layer):
    def __init__(
            self,
            n_future: int = None,
            n_out_ft: int = None,
            activation: str = None
    ):
        super(dense_multi_out, self).__init__()
        self.dense_out = tkl.Dense(n_future * n_out_ft, activation=activation)
        self.reshape = tkl.Reshape((n_future, n_out_ft))

    def call(self, x):
        x = self.dense_out(x)
        x = self.reshape(x)
        return x


class dense_reshape_conv1d_multi_out(tkl.Layer):
    def __init__(
            self,
            n_future: int = None,
            n_out_ft: int = None,
            activation: str = None,
            padding: str = 'same'
    ):
        super(dense_reshape_conv1d_multi_out, self).__init__()
        self.dense_out = tkl.Dense(n_future * n_out_ft, activation=activation)
        self.reshape = tkl.Reshape((n_future, n_out_ft))
        self.conv1d = tkl.Conv1D(n_out_ft, 1, padding=padding)

    def call(self, x):
        x = self.dense_out(x)
        x = self.reshape(x)
        x = self.conv1d(x)
        return x


class multi_rnn_drop(tkl.Layer):
    def __init__(
            self,
            mdl: object = None,
            units: list = None,
            activations: list = None,
            sequences: list = None,
            bidirectional: bool = None,
            use_drop: bool = None,
            rate: float = None,
            is_mask: bool = False
    ):
        super(multi_rnn_drop, self).__init__()
        self.is_mask = is_mask
        if is_mask:
            self.mask = tkl.Masking(mask_value=value_miss)
        self.hidden_rnn = []
        for _, (n_units, act, seq) in enumerate(zip(units, activations, sequences)):
            self.hidden_rnn.append(
                rnn_drop(
                    mdl=mdl,
                    n_units=n_units,
                    activation=act,
                    return_seq=seq,
                    bidirectional=bidirectional,
                    use_drop=use_drop,
                    rate=rate
                )
            )

    def call(self, x):
        for j, (rnn) in enumerate(self.hidden_rnn):
            if j == 0:
                if self.is_mask:
                    x = self.mask(x)
                x = rnn(x)
            else:
                x = rnn(x)
        return x


class rnn_drop(tkl.Layer):
    def __init__(
            self,
            mdl: object = None,
            n_units: int = None,
            activation: str = None,
            return_seq: bool = False,
            bidirectional: bool = False,
            use_drop: bool = False,
            rate: float = 0.2
    ):
        super(rnn_drop, self).__init__()
        self.use_drop = use_drop
        if bidirectional:
            self.rnn = tkl.Bidirectional(mdl(units=n_units, activation=activation, return_sequences=return_seq))
        else:
            self.rnn = mdl(units=n_units, activation=activation, return_sequences=return_seq)
        if self.use_drop:
            self.drop = tkl.Dropout(rate=rate)

    def call(self, x):
        x = self.rnn(x)
        if self.use_drop:
            x = self.drop(x)
        return x


class rnn_attention_conv1d(tkl.Layer):

    def __init__(
            self,
            mdl: object = None,
            bidirectional: bool = True,
            n_units: int = None,
            rnn_act: str = None,
            return_seq: str = None,
            att_type: str = None,
            kernel_reg: float = None,
            bias_reg: float = None,
            reg_weight: float = None,
            n_att: int = None,
            num_heads=None,
            key_dim=None,
            dropout=None,
            n_filters: int = None,
            kernel: int = None,
            conv_act: str = None,
            padding: str = None,
            simple_pool: bool = False,
            global_pool: bool = False,
            pool_size: int = None
    ):
        super(rnn_attention_conv1d, self).__init__()
        if bidirectional:
            self.rnn = tkl.Bidirectional(
                mdl(
                    units=n_units,
                    activation=rnn_act,
                    return_sequences=return_seq
                )
            )
        else:
            self.rnn = mdl(
                units=n_units,
                activation=rnn_act,
                return_sequences=return_seq
            )
        self.att_type = att_type
        if att_type == 'Bahdanau' or att_type == 'Luong':
            if att_type == 'Bahdanau':
                attention_type = SeqSelfAttention.ATTENTION_TYPE_ADD
            elif att_type == 'Luong':
                attention_type = SeqSelfAttention.ATTENTION_TYPE_MUL
            self.attention = SeqSelfAttention(
                attention_type=attention_type,
                kernel_regularizer=tkr.l2(kernel_reg),
                bias_regularizer=tkr.l1(bias_reg),
                attention_regularizer_weight=reg_weight,
                name=f'Attention{n_att}'
            )
        if att_type == 'MultiHeadAttention':
            self.attention = tkl.MultiHeadAttention(
                num_heads=num_heads,
                key_dim=key_dim,
                dropout=dropout
            )

        self.conv1d = tkl.Conv1D(
            filters=n_filters,
            kernel_size=kernel,
            activation=conv_act,
            padding=padding
        )
        if simple_pool:
            self.maxpool1d = tkl.MaxPool1D(pool_size)
        elif global_pool:
            self.maxpool1d = tkl.GlobalAveragePooling1D()
        else:
            self.maxpool1d = tkl.MaxPool1D()

    def call(self, x):
        x = self.rnn(x)
        if self.att_type == 'Bahdanau' or self.att_type == 'Luong':
            x = self.attention(x)
        if self.att_type == 'MultiHeadAttention':
            x = self.attention(x, x)
        x = self.conv1d(x)
        x = self.maxpool1d(x)
        return x


class multi_rnn_attention_conv1d(tkl.Layer):
    def __init__(
            self,
            mdl: object = None,
            bidirectional: bool = True,
            units: list = None,
            rnn_act: list = None,
            return_seq: list = None,
            att_type: str = None,
            kernel_reg: float = None,
            bias_reg: float = None,
            reg_weight: float = None,
            n_filters: list = None,
            kernels: list = None,
            conv_act: list = None,
            paddings: list = None,
            simple_pool: bool = None,
            global_pool: bool = None,
            pool_size: int = None
    ):
        super(multi_rnn_attention_conv1d, self).__init__()
        self.hidden_birnn_att_conv_layers = []
        for i, (unit, act_rnn, seq, ftr, knl, act_conv, pad) in enumerate(
                zip(units, rnn_act, return_seq, n_filters, kernels, conv_act, paddings)):
            self.hidden_birnn_att_conv_layers.append(
                rnn_attention_conv1d(
                    mdl=mdl,
                    bidirectional=bidirectional,
                    n_units=unit,
                    rnn_act=act_rnn,
                    return_seq=seq,
                    att_type=att_type,
                    kernel_reg=kernel_reg,
                    bias_reg=bias_reg,
                    reg_weight=reg_weight,
                    n_att=i,
                    n_filters=ftr,
                    kernel=knl,
                    conv_act=act_conv,
                    padding=pad,
                    simple_pool=simple_pool,
                    global_pool=global_pool,
                    pool_size=pool_size
                )
            )

    def call(self, x):
        for j, (birnn_att_conv) in enumerate(self.hidden_birnn_att_conv_layers):
            if j == 0:
                x = birnn_att_conv(x)
            else:
                x = birnn_att_conv(x)
        return x
        

class multi_birnn_multihead_attention_conv1d(tkl.Layer):
    def __init__(
            self,
            mdl: object = None,
            bidirectional: bool = True,
            units: list = None,
            rnn_act: list = None,
            return_seq: list = None,
            att_type: str = None,
            num_heads: int = None,
            key_dim: int = None,
            dropout: float = None,
            n_filters: list = None,
            kernels: list = None,
            conv_act: list = None,
            paddings: list = None,
            simple_pool: bool = None,
            global_pool: bool = None,
            pool_size: int = None
    ):
        super(multi_birnn_multihead_attention_conv1d, self).__init__()
        self.hidden_birnn_att_conv_layers = []
        for i, (unit, act_rnn, seq, ftr, knl, act_conv, pad) in enumerate(
                zip(units, rnn_act, return_seq, n_filters, kernels, conv_act, paddings)):
            self.hidden_birnn_att_conv_layers.append(
                rnn_attention_conv1d(
                    mdl=mdl,
                    bidirectional=bidirectional,
                    n_units=unit,
                    rnn_act=act_rnn,
                    return_seq=seq,
                    att_type=att_type,
                    num_heads=num_heads,
                    key_dim=key_dim,
                    dropout=dropout,
                    n_filters=ftr,
                    kernel=knl,
                    conv_act=act_conv,
                    padding=pad,
                    simple_pool=simple_pool,
                    global_pool=global_pool,
                    pool_size=pool_size
                )
            )

    def call(self, x):
        for j, (birnn_att_conv) in enumerate(self.hidden_birnn_att_conv_layers):
            if j == 0:
                x = birnn_att_conv(x)
            else:
                x = birnn_att_conv(x)
        return x


class Time2Vec(tkl.Layer):

    def __init__(self, output_dim=None, **kwargs):
        self.output_dim = output_dim
        super(Time2Vec, self).__init__(**kwargs)

    def build(self, input_shape):
        self.W = self.add_weight(
            name='W',
            shape=(input_shape[-1], self.output_dim),
            initializer='uniform',
            trainable=True)

        self.P = self.add_weight(
            name='P',
            shape=(input_shape[1], self.output_dim),
            initializer='uniform',
            trainable=True
        )
        self.w = self.add_weight(
            name='w',
            shape=(input_shape[1], 1),
            initializer='uniform',
            trainable=True
        )
        self.p = self.add_weight(
            name='p',
            shape=(input_shape[1], 1),
            initializer='uniform',
            trainable=True
        )
        super(Time2Vec, self).build(input_shape)

    def call(self, x):
        original = self.w * x + self.p
        sin_trans = K.sin(K.dot(x, self.W) + self.P)
        return K.concatenate([sin_trans, original], -1)


class time2vec_birnn_layer(tkl.Layer):

    def __init__(
            self,
            mdl: object = None,
            output_dim: int = None,
            unit: int = None,
            rnn_act: int = None,
            rnn_seq: int = None,
            is_drop: bool = None,
            rate: float = None,
    ):
        super(time2vec_birnn_layer, self).__init__()
        self.is_drop = is_drop
        self.time2vec = Time2Vec(output_dim=output_dim)
        self.birnn = tkl.Bidirectional(
            mdl(
                units=unit,
                activation=rnn_act,
                return_sequences=rnn_seq
            )
        )
        if is_drop:
            self.drop = tkl.Dropout(rate)

    def call(self, x):
        x = self.time2vec(x)
        x = self.birnn(x)
        if self.is_drop:
            x = self.drop(x)
        return x


class multi_time2vec_birnn(tkl.Layer):

    def __init__(
            self,
            mdl: object = None,
            output_dims: list = None,
            units: list = None,
            rnn_acts: list = None,
            return_seq: list = None,
            is_drop: bool = None,
            rate: float = None,
    ):
        super(multi_time2vec_birnn, self).__init__()
        self.hidden_time2vec = []
        for i, (dim, unit, act_rnn, seq,) in enumerate(zip(output_dims, units, rnn_acts, return_seq)):
            self.hidden_time2vec.append(
                time2vec_birnn_layer(
                    mdl=mdl,
                    output_dim=dim,
                    unit=unit,
                    rnn_act=act_rnn,
                    rnn_seq=seq,
                    is_drop=is_drop,
                    rate=rate
                )
            )

    def call(self, x):
        for j, (layer) in enumerate(self.hidden_time2vec):
            if j == 0:
                x = layer(x)
            else:
                x = layer(x)
        return x




class InnerConv1DBlock(tkl.Layer):

    def __init__(self, filters: int, h: float, kernel_size: int, neg_slope: float = .01, dropout: float = .5, **kwargs):
        if filters <= 0 or h <= 0:
            raise ValueError('filters and h must be positive')
        super(InnerConv1DBlock, self).__init__(**kwargs)
        self.conv1d = tkl.Conv1D(max(round(h * filters), 1), kernel_size, padding='same')
        self.leakyrelu = tkl.LeakyReLU(neg_slope)
        self.dropout = tkl.Dropout(dropout)
        self.conv1d2 = tkl.Conv1D(filters, kernel_size, padding='same')
        self.tanh = tf.keras.activations.tanh

    def call(self, input_tensor, training=None):
        x = self.conv1d(input_tensor)
        x = self.leakyrelu(x)

        if training:
            x = self.dropout(x)

        x = self.conv1d2(x)
        x = self.tanh(x)
        return x


class SciBlock(tkl.Layer):
    def __init__(self, features: int, kernel_size: int, h: int, **kwargs):
        """
        :param features: number of features in the output
        :param kernel_size: kernel size of the convolutional layers
        :param h: scaling factor for convolutional module
        """

        super(SciBlock, self).__init__(**kwargs)
        self.features = features
        self.kernel_size = kernel_size
        self.h = h

    def build(self, input_shape):
        self.conv1ds = {
            k: InnerConv1DBlock(
                filters=self.features,
                h=self.h,
                kernel_size=self.kernel_size,
                name=k
            ) for k in ['psi', 'phi', 'eta', 'rho']
        }  # regularize?
        super().build(input_shape)
        # [layer.build(input_shape) for layer in self.conv1ds.values()]  # unneeded?

    def call(self, inputs, training=None):
        F_odd, F_even = inputs[:, ::2], inputs[:, 1::2]

        # Interactive learning as described in the paper
        F_s_odd = F_odd * tf.math.exp(self.conv1ds['phi'](F_even))
        F_s_even = F_even * tf.math.exp(self.conv1ds['psi'](F_odd))

        F_prime_odd = F_s_odd + self.conv1ds['rho'](F_s_even)
        F_prime_even = F_s_even - self.conv1ds['eta'](F_s_odd)

        return F_prime_odd, F_prime_even


class Interleave(tkl.Layer):
    """A layer used to reverse the even-odd split operation."""

    def __init__(self, **kwargs):
        super(Interleave, self).__init__(**kwargs)

    def interleave(self, slices):
        if not slices:
            return slices
        elif len(slices) == 1:
            return slices[0]

        mid = len(slices) // 2
        even = self.interleave(slices[:mid])
        odd = self.interleave(slices[mid:])

        shape = tf.shape(even)
        return tf.reshape(tf.stack([even, odd], axis=3), (shape[0], shape[1] * 2, shape[2]))

    def call(self, inputs):
        return self.interleave(inputs)


class SciNet(tkl.Layer):
    def __init__(
            self,
            horizon: int,
            features: int,
            levels: int,
            h: int,
            kernel_size: int,
            regularizer: Tuple[float, float] = (0, 0),
            **kwargs
    ):
        """
        :param horizon: number of time stamps in output
        :param features: number of features in output
        :param levels: height of the binary tree + 1
        :param h: scaling factor for convolutional module in each SciBlock
        :param kernel_size: kernel size of convolutional module in each SciBlock
        :param regularizer: activity regularization (not implemented)
        """

        if levels < 1:
            raise ValueError('Must have at least 1 level')
        super(SciNet, self).__init__(**kwargs)
        self.horizon = horizon
        self.features = features
        self.levels = levels
        self.interleave = Interleave()
        self.flatten = tkl.Flatten()
        self.dense = tkl.Dense(
            horizon * features,
            kernel_regularizer=tf.keras.regularizers.L1L2(0.001, 0.01),
            # activity_regularizer=L1L2(0.001, 0.01)
        )
        # self.regularizer = tkl.ActivityRegularization(l1=regularizer[0], l2=regularizer[1])

        # tree of sciblocks
        self.sciblocks = [SciBlock(features=features, kernel_size=kernel_size, h=h) for _ in range(2 ** levels - 1)]

    def build(self, input_shape):
        if input_shape[1] / 2 ** self.levels % 1 != 0:
            raise ValueError(
                f'timestamps {input_shape[1]} must be evenly divisible by a tree with {self.levels} levels'
            )
        super().build(input_shape)
        # [layer.build(input_shape) for layer in self.sciblocks]  # input_shape

    def call(self, inputs, training=None):
        # cascade input down a binary tree of sci-blocks
        lvl_inputs = [inputs]  # inputs for current level of the tree
        for i in range(self.levels):
            i_end = 2 ** (i + 1) - 1
            i_start = i_end - 2 ** i
            lvl_outputs = [
                output for j, tensor in zip(range(i_start, i_end), lvl_inputs) for output in self.sciblocks[j](tensor)
            ]
            lvl_inputs = lvl_outputs

        x = self.interleave(lvl_outputs)
        x += inputs

        # not sure if this is the correct way of doing it. The paper merely said to use a fully connected layer to
        # produce an output. Can't use TimeDistributed wrapper. It would force the layer's timestamps to match that of
        # the input -- something SCINet is supposed to solve
        x = self.flatten(x)
        x = self.dense(x)
        x = tf.reshape(x, (-1, self.horizon, self.features))

        return x


class StackedSciNet(tkl.Layer):
    def __init__(
            self,
            horizon: int,
            features: int,
            stacks: int,
            levels: int,
            h: int,
            kernel_size: int,
            regularizer: Tuple[float, float] = (0, 0),
            **kwargs
    ):
        """
        :param horizon: number of time stamps in output
        :param stacks: number of stacked SciNets
        :param levels: number of levels for each SciNet
        :param h: scaling factor for convolutional module in each SciBlock
        :param kernel_size: kernel size of convolutional module in each SciBlock
        :param regularizer: activity regularization (not implemented)
        """

        if stacks < 1:
            raise ValueError('Must have at least 1 stack')
        super(StackedSciNet, self).__init__(**kwargs)
        self.horizon = horizon
        self.scinets = [SciNet(
            horizon=horizon,
            features=features,
            levels=levels,
            h=h,
            kernel_size=kernel_size,
            regularizer=regularizer) for _ in range(stacks)
        ]
        # self.mse_fn = tf.keras.metrics.MeanSquaredError()
        # self.mae_fn = tf.keras.metrics.MeanAbsoluteError()

    # def build(self, input_shape):
    #     super().build(input_shape)
    #     [stack.build(input_shape) for stack in self.scinets]

    def call(self, inputs, targets=None, sample_weights=None, training=None):
        outputs = []
        for scinet in self.scinets:
            x = scinet(inputs)
            outputs.append(x)  # keep each stack's output for intermediate supervision
            inputs = tf.concat([x, inputs[:, x.shape[1]:, :]], axis=1)

        if targets is not None:
            # Calculate metrics
            # mse = self.mse_fn(targets, x, sample_weights)
            # mae = self.mae_fn(targets, x, sample_weights)
            # self.add_metric(mse, name='mean_squared_error')
            # self.add_metric(mae, name='mean_absolute_error')

            if training:
                # Calculate loss as sum of mean of norms of differences between output and input feature vectors for
                # each stack
                stacked_outputs = tf.stack(outputs)
                differences = stacked_outputs - targets
                loss = tf.linalg.normalize(differences, axis=1)[1]
                loss = tf.reshape(loss, (-1, self.horizon))
                loss = tf.reduce_sum(loss, 1)
                loss = loss / self.horizon
                loss = tf.reduce_sum(loss)
                self.add_loss(loss)

        return x

    def get_config(self):
        return super().get_config()


