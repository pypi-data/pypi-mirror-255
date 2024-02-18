from openpy_fxts.base_tf import tkm, tkl
from openpy_fxts.architectures.layers.layers_class import multi_conv1d_pool_flat_drop, dense_multi_out
from openpy_fxts.architectures.fxts.arch_dicts import _get_dict_fxts


class conv1D_dense(tkm.Model):

    def __init__(
            self,
            n_future: int = None,
            n_out_ft: int = None,
            config: dict = None
    ):
        super(conv1D_dense, self).__init__()
        if config is None:
            config = _get_dict_fxts('Conv1D_Dense').config_conv1d()
        self.n_future = n_future,
        self.n_out_ft = n_out_ft,
        self.config = config
        self.multi_conv1d = multi_conv1d_pool_flat_drop(
            filters=config['conv1d_layers']['filters'],
            kernels=config['conv1d_layers']['kernels'],
            activations=config['conv1d_layers']['activations'],
            paddings=config['conv1d_layers']['paddings'],
            use_drop=config['dropout']['activate'],
            rate=config['dropout']['rate'],
            maxpooling_1d=True,
            pool_size=config['conv1d_layers']['pool_size']
        )
        if config['dense_layer']['activation']:
            self.dense_layer = tkl.Dense(
                units=config['dense_layer']['units'], 
                activation=config['dense_layer']['activation']
            )
        if config['dropout']['activate']:
            self.drop = tkl.Dropout(rate=config['dropout']['rate'])
        self.dense_out = dense_multi_out(
            n_future,
            n_out_ft,
            config['output_layer']['activation']
        )

    def call(self, inputs, training=True, **kwargs):
        x = self.multi_conv1d(inputs)
        if self.config['dense_layer']['activation']:
            x = self.dense_layer(x)
            if self.config['dropout']['activate']:
                x = self.drop(x)
        x = self.dense_out(x)
        return x


class multi_conv1D_dense(tkm.Model):

    def __init__(
            self,
            n_inp_ft: int = None,
            n_future: int = None,
            n_out_ft: int = None,
            config: dict = None
    ):
        super(multi_conv1D_dense, self).__init__()
        if config is None:
            config = _get_dict_fxts('Multi_Conv1D_Dense').config_conv1d()
        self.n_inp_ft = n_inp_ft
        self.n_future = n_future,
        self.n_out_ft = n_out_ft,
        self.config = config
        filters = config['conv1d_layers']['filters']
        kernels = config['conv1d_layers']['kernels']
        activations = config['conv1d_layers']['activations']
        paddings = config['conv1d_layers']['paddings']
        self.hidden_layers = []
        for i in range(n_inp_ft):
            self.hidden_layers.append(
                multi_conv1d_pool_flat_drop(
                    filters=filters,
                    kernels=kernels,
                    activations=activations,
                    paddings=paddings,
                    use_drop=config['dropout']['activate'],
                    rate=config['dropout']['rate'],
                    maxpooling_1d=True,
                    pool_size=config['conv1d_layers']['pool_size']
                )
            )
        self.concat = tkl.Concatenate(axis=1)
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
        head_list = []
        for i, (layer_conv1d) in enumerate(self.hidden_layers):
            head = layer_conv1d(inputs)
        head_list.append(head)
        x = self.concat(head_list)
        if self.config['dense_layer']['activation']:
            x = self.dense_layer(x)
            x = self.drop(x)
        x = self.dense_out(x)
        return x