from openpy_fxts.base_tf import tkm, tkl


class _decoder_lstm(tkm.Model):
    def __init__(self, n_out_ft=None):
        super(_decoder_lstm, self).__init__()
        self.lstm = tkl.LSTM(256, return_sequences=True)
        self.time_dense = tkl.TimeDistributed(tkl.Dense(n_out_ft))

    def call(self, inputs, training=True, **kwargs):
        decoder = self.lstm(inputs[0], initial_state=inputs[1])
        decoder = self.time_dense(decoder)
        return decoder


class _decoder_lstm2(tkm.Model):
    def __init__(self, n_out_ft=None):
        super(_decoder_lstm2, self).__init__()
        self.decoder_l1 = tkl.LSTM(256, return_sequences=True)
        self.decoder_l2 = tkl.LSTM(256, return_sequences=True)
        self.time_dense = tkl.TimeDistributed(tkl.Dense(n_out_ft))

    def call(self, inputs, training=True, **kwargs):
        decoder_l1 = self.decoder_l1(inputs[0], initial_state=inputs[1])
        decoder_l2 = self.decoder_l2(decoder_l1, initial_state=inputs[2])
        decoder = self.time_dense(decoder_l2)
        return decoder


class _decoder_lstm2_bach_drop(tkm.Model):

    def __init__(self, n_out_ft=None):
        super(_decoder_lstm2_bach_drop, self).__init__()
        self.batch = tkl.BatchNormalization()
        self.lstm1 = tkl.LSTM(256, return_sequences=True)
        self.drop = tkl.Dropout(0.2)
        self.time_dense = tkl.TimeDistributed(tkl.Dense(n_out_ft))

    def call(self, inputs, training=True, **kwargs):
        decoder_inputs = self.batch(inputs)
        decoder_out = self.lstm1(decoder_inputs)
        decoder_out = self.drop(decoder_out)
        decoder_out = self.batch(decoder_out)
        decoder_out = self.time_dense(decoder_out)
        return decoder_out


class _decoder_bilstm(tkm.Model):
    def __init__(self, n_out_ft=None):
        super(_decoder_bilstm, self).__init__()
        self.bilstm = tkl.Bidirectional(tkl.LSTM(256, return_sequences=True))
        self.time_dense = tkl.TimeDistributed(tkl.Dense(n_out_ft))

    def call(self, inputs, training=True, **kwargs):
        decoder = self.bilstm(inputs[0], initial_state=inputs[1])
        decoder = self.time_dense(decoder)
        return decoder


class _decoder_bilstm2(tkm.Model):
    def __init__(self, n_out_ft=None):
        super(_decoder_bilstm2, self).__init__()
        self.decoder_l1 = tkl.Bidirectional(tkl.LSTM(256, return_sequences=True))
        self.decoder_l2 = tkl.Bidirectional(tkl.LSTM(256, return_sequences=True))
        self.time_dense = tkl.TimeDistributed(tkl.Dense(n_out_ft))

    def call(self, inputs, training=True, **kwargs):
        decoder_l1 = self.decoder_l1(inputs[0], initial_state=inputs[1])
        decoder_l2 = self.decoder_l2(decoder_l1, initial_state=inputs[2])
        decoder = self.time_dense(decoder_l2)
        return decoder


class _decoder_bilstm_time_dist(tkm.Model):
    def __init__(self, n_out_ft=None):
        super(_decoder_bilstm_time_dist, self).__init__()
        self.bilstm = tkl.Bidirectional(tkl.LSTM(256, activation='relu', return_sequences=True))
        self.time_dense1 = tkl.TimeDistributed(tkl.Dense(256, activation='relu'))
        self.time_dense2 = tkl.TimeDistributed(tkl.Dense(n_out_ft, activation='relu'))

    def call(self, inputs, training=True, **kwargs):
        x = self.bilstm(inputs)
        x = self.time_dense1(x)
        x = self.time_dense2(x)
        return x

class _decoder_bilstm(tkm.Model):
    def __init__(self, n_out_ft=None):
        super(_decoder_bilstm, self).__init__()
        self.bilstm = tkl.Bidirectional(tkl.LSTM(256, return_sequences=True))
        self.time_dense = tkl.TimeDistributed(tkl.Dense(n_out_ft))

    def call(self, inputs, training=True, **kwargs):
        decoder = self.bilstm(inputs[0], initial_state=inputs[1])
        decoder = self.time_dense(decoder)
        return decoder

