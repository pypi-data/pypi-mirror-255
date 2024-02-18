# -*- coding: utf-8 -*-
# @Time    : 14/07/2023
# @Author  : Ing. Jorge Lara
# @Email   : jlara@iee.unsj.edu.ar
# @File    : ------------
# @Software: PyCharm

class _get_dict_fxts:

    def __init__(self, name_mdl):
        self.name_mdl = name_mdl

    def config_mlp(self):
        if self.name_mdl == 'MLP_Dense':
            return {
                'input_layer': {
                    'units': 128,
                    'activation': None,
                    'l1': None,
                    'l2': None
                },
                'dense_layers': {
                    'units': [128, 64, 32],
                    'activations': ['relu', 'relu', 'relu'],
                    'l1': None,
                    'l2': None
                },
                'dropout': {
                    'activate': True,
                    'rate': 0.3
                },
                'output_layer': {
                    'activation': None
                }
            }

    def config_conv1d(self):
        # Simple models_fxts
        if self.name_mdl == 'Conv1D_Dense':
            return {
                'conv1d_layers': {
                    'filters': [64, 32],
                    'kernels': [9, 3],
                    'activations': ['relu', 'relu'],
                    'paddings': ['causal', 'causal'],
                    'pool_size': 2,
                },
                'dropout': {
                    'activate': True,
                    'rate': 0.3
                },
                'dense_layer': {
                    'activate': False,
                    'units': 32,
                    'activation': 'relu'
                },
                'output_layer': {
                    'activation': None
                }
            }
        if self.name_mdl == 'Multi_Conv1D_Dense':
            return {
                'conv1d_layers': {
                    'filters': [64, 32],
                    'kernels': [9, 3],
                    'activations': ['relu', 'relu', 'relu'],
                    'paddings': ['causal', 'causal', 'causal'],
                    'pool_size': 2,
                },
                'dropout': {
                    'activate': True,
                    'rate': 0.3
                },
                'dense_layer': {
                    'activate': False,
                    'units': 32,
                    'activation': 'relu'
                },
                'output_layer': {
                    'activation': None
                }
            }
        # Hybrids models_fxts
        if self.name_mdl == 'Conv1D_BiRNN':
            return {
                'conv1d_layers': {
                    'filters': [64, 32],
                    'kernels': [9, 3],
                    'activations': ['relu', 'relu', 'relu'],
                    'paddings': ['causal', 'causal', 'causal'],
                    'pool_size': 2
                },
                'rnn_layers': {
                    'type': 'GRU',
                    'units': [64, 32],
                    'activations': ['relu', 'relu'],
                    'sequences': [True, False],
                    'bidirectional': True
                },
                'dropout': {
                    'activate': True,
                    'rate': 0.3
                },
                'pool_size': 2,
                'dense_layer': {
                    'activate': False,
                    'units': 32,
                    'activation': 'relu'
                },
                'output_layer': {
                    'activation': None
                }
            }
        if self.name_mdl == 'TimeDist_Conv1D_BiRNN':
            return {
                'conv1d_layers': {
                    'filters': [64, 32],
                    'kernels': [9, 3],
                    'activations': ['relu', 'relu'],
                    'paddings': ['causal', 'causal'],
                    'maxpooling': True,
                    'pool_size': 2

                },
                'rnn_layer': {
                    'type': 'GRU',
                    'units': 256,
                    'activation': 'relu',
                    'sequences': False,
                    'bidirectional': False
                },
                'dropout': {
                    'activate': True,
                    'rate': 0.3
                },
                'pool_size': 2,
                'dense_layer': {
                    'units': 128,
                    'activation': 'relu'
                },
                'output_layer': {
                    'activation': None
                }
            }
        if self.name_mdl == 'Conv1D_BiRNN_Attention':
            return {
                'conv1d_layers': {
                    'filters': [64, 32],
                    'kernels': [9, 3],
                    'activations': ['relu', 'relu'],
                    'paddings': ['causal', 'causal'],
                    'pool_size': 2
                },
                'rnn_layers': {
                    'type': 'GRU',
                    'units': [64, 32],
                    'activations': ['relu', 'relu'],
                    'sequences': [True, True],
                    'bidirectional': True

                },
                'dropout': {
                    'activate': True,
                    'rate': 0.3
                },
                'dense_layer': {
                    'activate': False,
                    'units': 32,
                    'activation': 'relu'
                },
                'output_layer': {
                    'activation': None
                }
            }

    def config_birnn(self):
        # Simple models_fxts
        if self.name_mdl == 'BiRNN_Dense':
            return {
                'rnn_layers': {
                    'type': 'GRU',
                    'units': [64, 32],
                    'activations': ['relu', 'relu'],
                    'sequences': [True, False],
                    'bidirectional': False
                },
                'dropout': {
                    'activate': True,
                    'rate': 0.3
                },
                'dense_layer': {
                    'activate': True,
                    'units': 128,
                    'activation': 'relu'
                },
                'output_layer': {
                    'activation': None
                }
            }
        if self.name_mdl == 'Multi_BiRNN_Dense':
            return {
                'multi_rnn_layers': {
                    'type': 'GRU',
                    'units': [64, 32],
                    'activations': ['relu', 'relu'],
                    'sequences': [True, False],
                    'bidirectional': True
                },
                'dropout': {
                    'activate': True,
                    'rate': 0.3
                },
                'rnn_layer': {
                    'units': 64,
                    'activation': 'relu',
                    'sequences': False
                },
                'dense_layer': {
                    'activate': True,
                    'units': 64,
                    'activation': 'relu'
                },
                'output_layer': {
                    'activation': None
                }
            }
        # Hybrid models_fxts
        if self.name_mdl == 'BiRNN_Conv1D':
            return {
                'rnn_layers': {
                    'type': 'GRU',
                    'units': [64, 32],
                    'activations': ['relu', 'relu'],
                    'sequences': [True, True],
                    'bidirectional': True
                },
                'conv1d_layers': {
                    'filters': [64, 32],
                    'kernels': [9, 2],
                    'activations': ['relu', 'relu'],
                    'paddings': ['causal', 'causal'],
                    'pool_size': 1
                },
                'dropout': {
                    'activate': True,
                    'rate': 0.3
                },
                'output_layer': {
                    'activation': None
                }
            }
        if self.name_mdl == 'BiRNN_TimeDist_Dense':
            return {
                'rnn_layer': {
                    'type': 'GRU',
                    'units': 64,
                    'activations': 'relu',
                    'sequences': True,
                    'bidirectional': True
                },
                'timedist_dense_layers': {
                    'units': [64, 32],
                    'activations': ['relu', 'relu']
                },
                'dropout': {
                    'activate': True,
                    'rate': 0.3
                },
                'dense_layer': {
                    'units': 64,
                    'activation': 'relu'
                },
                'output_layer': {
                    'activation': None
                }
            }
        if self.name_mdl == 'BiRNN_Bahdanau_Attention_Conv1D':
            return {
                'rnn_layers': {
                    'type': 'GRU',
                    'units': [64, 32],
                    'activations': ['relu', 'relu'],
                    'sequences': [True, True],
                    'bidirectional': True
                },
                'attention': {
                    'kernel_reg': 1e-4,
                    'bias_reg': 1e-4,
                    'reg_weight': 1e-4,
                },
                'conv1d_layers': {
                    'filters': [64, 32],
                    'kernels': [9, 2],
                    'activations': ['relu', 'relu', 'relu'],
                    'paddings': ['causal', 'causal', 'causal'],
                    'pool_size': 1
                },
                'dropout': {
                    'activate': True,
                    'rate': 0.3
                },
                'output_layer': {
                    'activation': None
                }
            }
        if self.name_mdl == 'BiRNN_Luong_Attention_Conv1D':
            return {
                'rnn_layers': {
                    'type': 'GRU',
                    'units': [64, 32],
                    'activations': ['relu', 'relu'],
                    'sequences': [True, True],
                    'bidirectional': True
                },
                'attention': {
                    'kernel_reg': 1e-4,
                    'bias_reg': 1e-4,
                    'reg_weight': 1e-4,
                },
                'conv1d_layers': {
                    'filters': [64, 32],
                    'kernels': [9, 2],
                    'activations': ['relu', 'relu'],
                    'paddings': ['causal', 'causal'],
                    'pool_size': 1
                },
                'dropout': {
                    'activate': True,
                    'rate': 0.3
                },
                'output_layer': {
                    'activation': None
                }
            }
        if self.name_mdl == 'BiRNN_MultiHeadAttention_Conv1D':
            return {
                'rnn_layers': {
                    'type': 'GRU',
                    'units': [64, 32],
                    'activations': ['relu', 'relu'],
                    'sequences': [True, True],
                    'bidirectional': True
                },
                'attention': {
                    'num_heads': 2,
                    'key_dim': 2,
                    'dropout': 0.1
                },
                'conv1d_layers': {
                    'filters': [64, 32],
                    'kernels': [9, 2],
                    'activations': ['relu', 'relu', 'relu'],
                    'paddings': ['causal', 'causal', 'causal'],
                    'pool_size': 1
                },
                'dropout': {
                    'activate': True,
                    'rate': 0.3
                },
                'output_layer': {
                    'activation': None
                }
            }

    def config_encdec(self):
        if self.name_mdl == 'EncDec_BiRNN':
            return {
                'encoder': {
                    'rnn_layers': {
                        'type': 'GRU',
                        'units': [64, 32],
                        'activations': ['relu', 'relu'],
                        'sequences': [True, False],
                        'bidirectional': True
                    }
                },
                'decoder': {
                    'rnn_layers': {
                        'type': 'GRU',
                        'units': [64, 32],
                        'activations': ['relu', 'relu'],
                        'sequences': [True, True],
                        'bidirectional': True
                    }
                },
                'dropout': {
                    'activate': True,
                    'rate': 0.3
                },
            }
        if self.name_mdl == 'EncDec_Conv1D_BiRNN':
            return {
                'encoder': {
                    'conv1d_layers': {
                        'filters': [64, 32],
                        'kernels': [9, 3],
                        'activations': ['relu', 'relu'],
                        'paddings': ['causal', 'causal'],
                        'pool_size': 2
                    },
                },
                'decoder': {
                    'rnn_layers': {
                        'type': 'GRU',
                        'units': [64, 32],
                        'activations': ['relu', 'relu'],
                        'sequences': [True, True],
                        'bidirectional': True
                    }
                },
                'dropout': {
                    'activate': True,
                    'rate': 0.3
                },
            }