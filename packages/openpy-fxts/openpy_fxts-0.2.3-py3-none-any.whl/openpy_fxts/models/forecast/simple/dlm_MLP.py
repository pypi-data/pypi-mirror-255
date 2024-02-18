from openpy_fxts.baseline_mdls import base_class


class MLP_Dense_class(base_class):

    def __init__(
            self,
            config_data=None,
            config_mdl=None,
            config_sim=None,
            config_arch=None,
            name_mdl='MLP_Dense',
            type_mdl='MLP',
            app='fxts'
    ):
        super().__init__(config_data, config_mdl, config_sim, config_arch, name_mdl, type_mdl, app)
        return