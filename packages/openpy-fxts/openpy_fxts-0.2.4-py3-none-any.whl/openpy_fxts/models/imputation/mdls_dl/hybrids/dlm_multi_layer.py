# -*- coding: utf-8 -*-
# @Time    : 10/07/2023
# @Author  : Ing. Jorge Lara
# @Email   : jlara@iee.unsj.edu.ar
# @File    : ------------
# @Software: PyCharm

from openpy_fxts.preprocessing_data.forecast.prepare_data import pre_processing_data
from openpy_fxts.models.utils import _callbacks, _learning_curve
from openpy_fxts.models.utils import _process_values_preliminary
from openpy_fxts.models.utils import _mdl_caracteristic
import tensorflow as tf

tkm = tf.keras.models
tkl = tf.keras.layers
tkloss = tf.keras.losses
tko = tf.keras.optimizers
tku = tf.keras.utils


class Multi_Layer_Perceptron:

    def __init__(self, config_data=None, config_mdl=None, config_sim=None):
        # Parameters for dataset
        self.config_data = config_data
        self.n_past = config_data['n_past']
        self.n_future = config_data['n_future']
        self.n_inp_ft = config_data['n_inp_ft']
        self.n_out_ft = config_data['n_out_ft']
        # Parameters for neural network
        self.config_mdl = config_mdl
        self.optimizer = config_mdl['optimizer']
        self.loss = config_mdl['loss']
        self.metrics = config_mdl['metrics']
        self.batch_size = config_mdl['batch_size']  # Batch size for training.
        self.epochs = config_mdl['epochs']  # Number of epochs to train for.
        self.units = config_mdl['units']  # no of lstm units
        self.dropout = config_mdl['dropout']
        # Parameters for simulation
        self.config_sim = config_sim
        self.verbose = config_sim['verbose']
        self.patience = config_sim['patience']
        self.plot_history = config_sim['plt_history']
        self.preliminary = config_sim['preliminary']
        self.name_model = 'mlp'

    def build_model(self):
        n_input = self.n_past * self.n_inp_ft
        n_output = self.n_future * self.n_out_ft
        # Define model.
        model = tkm.Sequential()
        model.add(tkl.Dense(self.units, activation='relu', input_dim=n_input))
        model.add(tkl.Dense(n_output))
        return model

    def train_model(
            self,
            filepath: str = None,
    ):
        data_test = pre_processing_data(self.config_data, train=True, valid=True)
        pre_processed = data_test.transformer_data()
        model = Multi_Layer_Perceptron(self.config_data, self.config_mdl).build_model()
        model.compile(
            optimizer=self.optimizer,
            loss=self.loss,
            metrics=self.metrics
        )
        _mdl_caracteristic(model, self.config_sim, filepath)
        # Training
        X_train = pre_processed['train']['X']
        y_train = pre_processed['train']['y']
        X_train = X_train.reshape(X_train.shape[0], self.n_past * self.n_inp_ft)
        y_train = y_train.reshape(y_train.shape[0], self.n_future * self.n_out_ft)
        # Validation
        X_valid = pre_processed['valid']['X']
        y_valid = pre_processed['valid']['y']
        X_valid = X_valid.reshape(X_valid.shape[0], self.n_past * self.n_inp_ft)
        y_valid = y_valid.reshape(y_valid.shape[0], self.n_future * self.n_out_ft)

        history = model.fit(
            X_train,
            y_train,
            epochs=self.epochs,
            validation_data=(
                X_valid,
                y_valid
            ),
            batch_size=self.batch_size,
            verbose=self.verbose,
            callbacks=_callbacks(
                filepath,
                weights=True,
                verbose=self.verbose,
                patience=self.patience
            )
        )
        if self.config_data['plt_history']:
            _learning_curve(history, self.name_model, filepath, self.config_sim['time_init'])
        if self.config_data['preliminary']:
            data_test = pre_processing_data(self.config_data, test=True)
            dict_test = data_test.transformer_data()
            yhat = _process_values_preliminary(
                model,
                dict_test,
                self.config_data,
                self.config_sim,
                self.name_model
            ).get_values(type_mdl='Dense')
        return model

    def prediction(
            self,
            model
    ):
        data = pre_processing_data(self.config_data, test=True)
        dict_test = data.transformer_data()
        yhat =_process_values_preliminary(
            model,
            dict_test,
            self.config_data,
            self.config_sim,
            self.name_model
        ).get_values(type_mdl='Dense')
        return yhat