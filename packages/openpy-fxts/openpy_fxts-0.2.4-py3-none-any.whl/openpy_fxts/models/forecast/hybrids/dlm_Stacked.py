from openpy_fxts.preprocessing_data.forecast.prepare_data import pre_processing_data
from openpy_fxts.architectures.utils import callbacks, learning_curve
from openpy_fxts.architectures.utils import _values_preliminary
from openpy_fxts.architectures.layers.layers_class import StackedSciNet
from openpy_fxts.base_tf import tkm, tkl, tku


class RNN_Stacked:

    def __init__(self, config_data=None, config_mdl=None):
        self.config_data = config_data
        self.n_past = config_data['n_past']
        self.n_future = config_data['n_future']
        self.n_inp_ft = config_data['n_inp_ft']
        self.n_out_ft = config_data['n_out_ft']
        # Parameters for model
        self.optimizer = config_mdl['optimizer']
        self.loss = config_mdl['loss']
        self.metrics = config_mdl['metrics']
        self.batch_size = config_mdl['batch_size']  # Batch size for training.
        self.epochs = config_mdl['epochs']  # Number of epochs to train for.
        self.units = config_mdl['units']  # no of lstm units
        self.dropout = config_mdl['dropout']
        self.name_model = 'LSTM_Stacked'

    def build_model(self):
        input_layer = tkl.Input(shape=(self.n_past, self.n_inp_ft), name='Input')
        lstm1 = tkl.LSTM(
            64,
            activation='relu',
            return_sequences=True,
            input_shape=(self.n_past, self.n_inp_ft)
        )(input_layer)
        lstm2 = tkl.LSTM(64, activation='relu')(lstm1)
        dense1 = tkl.Dense(128)(lstm2)
        dropout = tkl.Dropout(0.3)(dense1)
        dense2 = tkl.Dense(self.n_future * self.n_out_ft, activation='relu')(dropout)
        output_layer = tkl.Reshape((self.n_future, self.n_out_ft))(dense2)
        output_layer = tkl.Conv1D(self.n_out_ft, 1, padding='same')(output_layer)
        # Connect input and output through the Model class
        model = tkm.Model(inputs=input_layer, outputs=output_layer, name='model')
        # Return the model
        return model

    def train_model(
            self,
            filepath: str = None,
            preliminary: bool = True
    ):
        data = pre_processing_data(self.config_data, train=True, valid=True)
        pre_processed = data.transformer_data()
        model = RNN_Stacked(self.config_data, self.config_mdl).build_model()
        model.compile(
            optimizer=self.optimizer,
            loss=self.loss,
            metrics=self.metrics
        )
        if self.config_data['view_summary']:
            model.summary()
        if self.config_data['plt_model']:
            if filepath is None:
                tku.plot_model(model, show_shapes=True)
            else:
                tku.plot_model(model, to_file=filepath, show_shapes=True, show_layer_names=True)
        # Training
        history = model.fit(
            pre_processed['train']['X'],
            pre_processed['train']['y'],
            epochs=self.epochs,
            validation_data=(
                pre_processed['valid']['X'],
                pre_processed['valid']['y']
            ),
            batch_size=self.batch_size,
            verbose=1,
            callbacks=callbacks(filepath, weights=True)
        )
        if self.config_data['plt_history']:
            learning_curve(history, self.name_model, self.config_data['time_init'], filepath=filepath)
        if preliminary:
            data = pre_processing_data(self.config_data, test=True)
            dict_test = data.transformer_data()
            _values_preliminary(model, dict_test, self.config_data)
        return model

    def prediction(
            self,
            model
    ):
        data = pre_processing_data(self.config_data, test=True)
        dict_test = data.transformer_data()
        yhat = _values_preliminary(model, dict_test, self.config_data)
        return yhat


class Stacked_SciNet:

    def __init__(self, config_data=None, config_mdl=None):
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
        self.units = config_mdl['units']  # no of lstm units
        self.dropout = config_mdl['dropout']
        self.name_model = 'Stacked_SciNet'

    def build_model(self):
        input_train = tkl.Input(shape=(self.n_past, self.n_inp_ft))
        output_train = tkl.Input(shape=(self.n_future, self.n_out_ft))

        predictions = StackedSciNet(
            horizon=self.n_future,
            features=self.n_out_ft,
            stacks=2,
            levels=1,
            h=4,
            kernel_size=5
        )(input_train)
        sciNet_model = tkm.Model(inputs=input_train, outputs=predictions)

        # Return the model
        return sciNet_model

    def train_model(
            self,
            filepath: str = None,
            preliminary: bool = True
    ):
        data = pre_processing_data(self.config_data, train=True, valid=True)
        pre_processed = data.transformer_data()
        model = Stacked_SciNet(self.config_data, self.config_mdl).build_model()
        model.compile(
            optimizer=self.optimizer,
            loss=self.loss,
            metrics=self.metrics
        )
        if self.config_data['view_summary']:
            model.summary()
        if self.config_data['plt_model']:
            if filepath is None:
                tku.plot_model(model, show_shapes=True)
            else:
                tku.plot_model(model, to_file=filepath, show_shapes=True, show_layer_names=True)
        # Training
        history = model.fit(
            pre_processed['train']['X'],
            pre_processed['train']['y'],
            epochs=self.epochs,
            validation_data=(
                pre_processed['valid']['X'],
                pre_processed['valid']['y']
            ),
            batch_size=self.batch_size,
            verbose=1,
            callbacks=callbacks(filepath, weights=True)
        )
        if self.config_data['plt_history']:
            learning_curve(history, self.name_model, self.config_data['time_init'], filepath=filepath)
        if preliminary:
            data = pre_processing_data(self.config_data, test=True)
            dict_test = data.transformer_data()
            _values_preliminary(model, dict_test, self.config_data)
        return model

    def prediction(
            self,
            model
    ):
        data = pre_processing_data(self.config_data, test=True)
        dict_test = data.transformer_data()
        yhat = _values_preliminary(model, dict_test, self.config_data)
        return yhat