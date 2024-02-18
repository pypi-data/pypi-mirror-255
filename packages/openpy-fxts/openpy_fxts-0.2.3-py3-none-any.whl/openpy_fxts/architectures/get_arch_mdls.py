# -*- coding: utf-8 -*-
# @Time    : 06/07/2023
# @Author  : Ing. Jorge Lara
# @Email   : jlara@iee.unsj.edu.ar
# @File    : ------------
# @Software: PyCharm

from openpy_fxts.architectures.baseline_arch import base_arch
from openpy_fxts.architectures.fxts.fxts_mdls import fxts_mdls
from openpy_fxts.architectures.mdits.mdits_mdls import mdits_mdls


class get_architecture(base_arch):

    def __init__(self, name_mdl, type_mdl, n_past, n_future, n_inp_ft, n_out_ft, config_arch, app):
        super().__init__(name_mdl, type_mdl, n_past, n_future, n_inp_ft, n_out_ft, config_arch)
        self.app = app

    def select_model(self):

        if self.app == 'fxts':
            return fxts_mdls(
                self.name_mdl, self.type_mdl, self.n_past, self.n_future, self.n_inp_ft, self.n_out_ft, self.config_arch
            ).models()

        if self.app == 'mdits':
            return mdits_mdls(
                self.name_mdl, self.type_mdl, self.n_past, self.n_future, self.n_inp_ft, self.n_out_ft, self.config_arch
            ).models()


