import tensorflow as tf

tkm = tf.keras.models
tkl = tf.keras.layers
tko = tf.keras.optimizers


def model_E1D1(n_in, n_out, n_features, units: int = 100):
    # E1D1
    # n_features ==> no of features at each timestep in the datasets.
    #
    encoder_inputs = tkl.Input(shape=(n_in, n_features))
    encoder_l1 = tkl.LSTM(units, return_state=True)
    encoder_outputs1 = encoder_l1(encoder_inputs)
    encoder_states1 = encoder_outputs1[1:]
    #
    decoder_inputs = tkl.RepeatVector(n_out)(encoder_outputs1[0])
    #
    decoder_l1 = tkl.LSTM(units, return_sequences=True)(decoder_inputs, initial_state=encoder_states1)
    decoder_outputs1 = tkl.TimeDistributed(tkl.Dense(n_features))(decoder_l1)
    #
    model_e1d1 = tf.keras.models.Model(encoder_inputs, decoder_outputs1)
    return model_e1d1


def model_E2D2(n_in, n_out, n_features, units: int = 100):
    # E2D2
    # n_features ==> no of features at each timestep in the datasets.
    #
    encoder_inputs = tkl.Input(shape=(n_in, n_features))
    encoder_l1 = tkl.LSTM(units, return_sequences=True, return_state=True)
    encoder_outputs1 = encoder_l1(encoder_inputs)
    encoder_states1 = encoder_outputs1[1:]
    encoder_l2 = tkl.LSTM(units, return_state=True)
    encoder_outputs2 = encoder_l2(encoder_outputs1[0])
    encoder_states2 = encoder_outputs2[1:]
    #
    decoder_inputs = tf.keras.layers.RepeatVector(n_out)(encoder_outputs2[0])
    #
    decoder_l1 = tkl.LSTM(units, return_sequences=True)(decoder_inputs, initial_state=encoder_states1)
    decoder_l2 = tkl.LSTM(units, return_sequences=True)(decoder_l1, initial_state=encoder_states2)
    decoder_outputs2 = tkl.TimeDistributed(tkl.Dense(n_features))(decoder_l2)
    #
    model_e2d2 = tf.keras.models.Model(encoder_inputs, decoder_outputs2)
    return model_e2d2


def model_2LSTM_2Drop_Dense(
        n_timesteps: int = None,
        n_features: int = None,
        n_outputs: int = None,
        units: int = 200,
        dropout: float = 0.2,
        optimizer=tko.RMSprop(learning_rate=0.01),
        # optimizer=tko.Adam(learning_rate=0.01),
        summary: bool = True
):
    """
    Model LSTM-Dropout-LSTM-Dropout-Dense-Reshape

    :param n_timesteps:
    :param n_features:
    :param n_outputs:
    :param units:
    :param dropout:
    :param optimizer:
    :param summary:
    :return:
    """
    # Define model.
    name_model = 'LSTM2_Drop2_Dense'
    model = tkm.Sequential()
    model.add(tkl.LSTM(units, input_shape=(n_timesteps, n_features), return_sequences=True))
    model.add(tkl.Dropout(dropout))
    model.add(tkl.LSTM(units, activation='relu'))
    model.add(tkl.Dropout(dropout))
    model.add(tkl.Dense((n_outputs * n_features), activation='linear'))
    model.add(tkl.Reshape((n_outputs, n_features)))
    # model.compile(loss='mse', optimizer='adam')
    model.compile(optimizer=optimizer, loss='mse')
    if summary:
        print(model.summary())
    # Fit network.
    return model, name_model
