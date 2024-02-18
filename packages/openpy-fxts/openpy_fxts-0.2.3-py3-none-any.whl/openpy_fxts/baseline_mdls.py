import tensorflow as tf

from openpy_fxts.architectures.get_arch_mdls import get_architecture
from openpy_fxts.preprocessing_data.forecast.prepare_data import pre_processing_data
from openpy_fxts.architectures.utils import mdl_characteristics
from openpy_fxts.architectures.utils import callbacks
from openpy_fxts.architectures.utils import learning_curve
from openpy_fxts.architectures.utils import process_values_preliminary
from time import time

tkm = tf.keras.models
tkl = tf.keras.layers
tkloss = tf.keras.losses
tko = tf.keras.optimizers
tku = tf.keras.utils

sim_aux = {
    'view_summary': False,  # Summary for architecture select
    'metrics': True,
    'preliminary': False,
    'plt_model': False,  # Don't change to True, need review
    'plt_history': True,
    'plt_results': True,
    'plt_metrics': False,  # Don't change to True, need review
    'view_plots': False,
    'verbose': 1,
    'patience': 5,
    'time_init': time()
}

mdl_aux = {
    'optimizer': 'adam',
    'loss': 'mse',
    'metrics': ['accuracy'],  # Metrics to train
    'batch_size': 128,  # Batch size for training. { [32, 64],[*128, 256] }- Good starters
    'epochs': 100,  # Number of epochs to train for.
}


class base_model:

    def __init__(
            self,
            config_data=None,
            config_mdl=None,
            config_sim=None,
            config_arch=None,
            name_mdl=None,
            type_mdl=None,
            app=None
    ):
        if config_sim is None:
            config_sim = sim_aux
        if config_mdl is None:
            config_mdl = mdl_aux
        # Parameters for dataset
        self.config_data = config_data
        self.n_past = config_data['n_past']
        self.n_future = config_data['n_future']
        self.n_inp_ft = config_data['n_inp_ft']
        self.n_out_ft = config_data['n_out_ft']
        # Parameters for model
        self.config_mdl = config_mdl
        self.optimizer = config_mdl['optimizer']
        self.loss = config_mdl['loss']
        self.metrics = config_mdl['metrics']
        self.batch_size = config_mdl['batch_size']  # Batch size for training.
        self.epochs = config_mdl['epochs']  # Number of epochs to train for.
        # Parameters for simulation
        self.config_sim = config_sim
        self.verbose = config_sim['verbose']
        self.patience = config_sim['patience']
        self.plot_history = config_sim['plt_history']
        self.preliminary = config_sim['preliminary']
        self.config_arch = config_arch
        self.name_mdl = name_mdl
        self.type_mdl = type_mdl
        self.app = app

    def _architecture_model(self):
        get_arch = get_architecture(
            name_mdl=self.name_mdl,
            type_mdl=self.type_mdl,
            n_past=self.n_past,
            n_future=self.n_future,
            n_inp_ft=self.n_inp_ft,
            n_out_ft=self.n_out_ft,
            config_arch=self.config_arch,
            app=self.app
        )
        model = get_arch.select_model()
        return model

    def reshape_train_valid_for_fxts(self, pre_processed):
        # Training
        X_train = pre_processed['train']['X']
        y_train = pre_processed['train']['y']
        # Validation
        X_valid = pre_processed['valid']['X']
        y_valid = pre_processed['valid']['y']
        if self.type_mdl == 'MLP':
            if self.name_mdl == 'MLP_Dense':
                X_train_list, X_valid_list = [], []
                for i in range(X_train.shape[2]):
                    X_train_list.append(X_train[:, :, i])
                    X_valid_list.append(X_valid[:, :, i])
                return X_train_list, y_train, X_valid_list, y_valid
            if self.name_mdl == 'MLP_RNN':
                X_train_list, X_valid_list = [], []
                for i in range(X_train.shape[2]):
                    X_train_list.append(X_train[:, :, i])
                    X_valid_list.append(X_valid[:, :, i])
                return X_train_list, X_valid_list, X_valid, y_valid
        if self.type_mdl == 'Conv1D':
            if self.name_mdl == 'TimeDist_Conv1D_RNN':
                X_train = X_train.reshape(X_train.shape[0], X_train.shape[1], X_train.shape[2], 1)
                X_valid = X_valid.reshape(X_valid.shape[0], X_valid.shape[1], X_valid.shape[2], 1)
                return X_train, y_train, X_valid, y_valid
            else:
                return X_train, y_train, X_valid, y_valid
        else:
            return X_train, y_train, X_valid, y_valid

    def _training_mdl(self, filepath):
        pre_processed = pre_processing_data(
            self.config_data,
            train=True,
            valid=True
        ).transformer_data(
            dropnan=True
        )
        model = self._architecture_model()
        print(self.name_mdl)
        model.compile(
            optimizer=self.optimizer,
            loss=self.loss,
            metrics=self.metrics
        )
        mdl_characteristics(
            model,
            self.config_sim,
            filepath
        )
        X_train, y_train, X_valid, y_valid = self.reshape_train_valid_for_fxts(pre_processed)
        history = model.fit(
            x=X_train,
            y=y_train,
            validation_data=(
                X_valid,
                y_valid
            ),
            batch_size=self.batch_size,
            epochs=self.epochs,
            verbose=self.verbose,
            callbacks=callbacks(
                filepath,
                weights=True,
                verbose=self.verbose,
                patience=self.patience
            )
        )
        if self.plot_history:
            learning_curve(
                history=history,
                name_mdl=self.name_mdl,
                time_start=self.config_sim['time_init'],
                view_plots=self.config_sim['view_plots'],
                filepath=filepath
            )
        if self.preliminary:
            return process_values_preliminary(
                model=model,
                dict_test=pre_processing_data(
                    self.config_data,
                    test=True
                ).transformer_data(
                    dropnan=True
                ),
                config_data=self.config_data,
                config_sim=self.config_sim,
                name_mdl=self.name_mdl,
                type_mdl=self.type_mdl,
                app=self.app
            ).get_values(filepath)
        else:
            return None

    def _prediction_model(self, model_train, filepath):
        return process_values_preliminary(
            model=model_train,
            dict_test=pre_processing_data(
                self.config_data,
                test=True
            ).transformer_data(
                dropnan=True
            ),
            config_data=self.config_data,
            config_sim=self.config_sim,
            name_mdl=self.name_mdl,
            type_mdl=self.type_mdl,
            app=self.app
        ).get_values(filepath)


class base_class(base_model):

    def __init__(
            self,
            config_data=None,
            config_mdl=None,
            config_sim=None,
            config_arch=None,
            name_mdl=None,
            type_mdl=None,
            app=None
    ):
        super().__init__(config_data, config_mdl, config_sim, config_arch, name_mdl, type_mdl, app)

    def _build_mdl(self):
        return self._architecture_model()

    def training_mdl(
            self,
            filepath: str = None
    ):
        return self._training_mdl(filepath)

    def prediction_mdl(self, filepath: str = None):
        return self._prediction_model(self._build_mdl(), filepath)
