# -*- coding: utf-8 -*-
# @Time    : 01/08/2023
# @Author  : Ing. Jorge Lara
# @Email   : jlara@iee.unsj.edu.ar
# @File    : ------------
# @Software: PyCharm

class base_arch:

    def __init__(
            self,
            name_mdl,
            type_mdl,
            n_past,
            n_future,
            n_inp_ft,
            n_out_ft,
            config_arch
    ):
        self.name_mdl = name_mdl
        self.type_mdl = type_mdl
        self.n_past = n_past
        self.n_future = n_future
        self.n_inp_ft = n_inp_ft
        self.n_out_ft = n_out_ft
        self.config_arch = config_arch
