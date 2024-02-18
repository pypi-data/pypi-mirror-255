# -*- coding: utf-8 -*-
# @Time    : 21/07/2023
# @Author  : Ing. Jorge Lara
# @Email   : jlara@iee.unsj.edu.ar
# @File    : ------------
# @Software: PyCharm

from openpy_fxts.baseline_mdls import base_class


class EncDec_BiRNN_class(base_class):

    def __init__(
            self,
            config_data=None,
            config_mdl=None,
            config_sim=None,
            config_arch=None,
            name_mdl='EncDec_BiRNN',
            type_mdl='EncDec',
            app='fxts'
    ):
        super().__init__(config_data, config_mdl, config_sim, config_arch, name_mdl, type_mdl, app)
        return


class EncDec_Conv1D_BiRNN_class(base_class):

    def __init__(
            self,
            config_data=None,
            config_mdl=None,
            config_sim=None,
            config_arch=None,
            name_mdl='EncDec_Conv1D_BiRNN',
            type_mdl='EncDec',
            app='fxts'
    ):
        super().__init__(config_data, config_mdl, config_sim, config_arch, name_mdl, type_mdl, app)
        return