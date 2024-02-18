from openpy_fxts.baseline_mdls import base_class


class TCN_BiRNN_class(base_class):

    def __init__(
            self,
            config_data=None,
            config_mdl=None,
            config_sim=None,
            config_arch=None,
            name_mdl='TCN_BiLSTM',
            type_mdl='Others',
            app='fxts'
    ):
        super().__init__(config_data, config_mdl, config_sim, config_arch, name_mdl, type_mdl, app)
        return


class Time2Vec_BiRNN_class(base_class):

    def __init__(
            self,
            config_data=None,
            config_mdl=None,
            config_sim=None,
            config_arch=None,
            name_mdl='Time2Vec_BiRNN',
            type_mdl='Others',
            app='fxts'
    ):
        super().__init__(config_data, config_mdl, config_sim, config_arch, name_mdl, type_mdl, app)
        return


