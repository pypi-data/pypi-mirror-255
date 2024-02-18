# -*- coding: utf-8 -*-
# @Time    : 10/07/2023
# @Author  : Ing. Jorge Lara
# @Email   : jlara@iee.unsj.edu.ar
# @File    : ------------
# @Software: PyCharm

from openpy_fxts.baseline_mdls import base_class


class BiLSTM_Dense_class(base_class):

    def __init__(
            self,
            config_data=None,
            config_mdl=None,
            config_sim=None,
            config_arch=None,
            name_mdl='BiLSTM_Dense',
            type_mdl='BiLSTM',
            app='mdits'
    ):
        super().__init__(config_data, config_mdl, config_sim, config_arch, name_mdl, type_mdl, app)
        return


class BiLSTM_Conv1D_class(base_class):

    def __init__(
            self,
            config_data=None,
            config_mdl=None,
            config_sim=None,
            config_arch=None,
            name_mdl='BiLSTM_Conv1D',
            type_mdl='BiLSTM',
            app='mdits'
    ):
        super().__init__(config_data, config_mdl, config_sim, config_arch, name_mdl, type_mdl, app)
        return


class BiLSTM_Bahdanau_Attention_Conv1D_class(base_class):

    def __init__(
            self,
            config_data=None,
            config_mdl=None,
            config_sim=None,
            config_arch=None,
            name_mdl='BiLSTM_Bahdanau_Attention_Conv1D',
            type_mdl='BiLSTM',
            app='mdits'
    ):
        super().__init__(config_data, config_mdl, config_sim, config_arch, name_mdl, type_mdl, app)
        return


class BiLSTM_MultiHeadAttention_Conv1D_class(base_class):

    def __init__(
            self,
            config_data=None,
            config_mdl=None,
            config_sim=None,
            config_arch=None,
            name_mdl='BiLSTM_MultiHeadAttention_Conv1D',
            type_mdl='BiLSTM',
            app='mdits'
    ):
        super().__init__(config_data, config_mdl, config_sim, config_arch, name_mdl, type_mdl, app)
        return


class BiLSTM_Luong_Attention_Conv1D_class(base_class):

    def __init__(
            self,
            config_data=None,
            config_mdl=None,
            config_sim=None,
            config_arch=None,
            name_mdl='BiLSTM_Luong_Attention_Conv1D',
            type_mdl='BiLSTM',
            app='mdits'
    ):
        super().__init__(config_data, config_mdl, config_sim, config_arch, name_mdl, type_mdl, app)
        return


