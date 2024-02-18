from openpy_fxts.base_tf import tkm, tkl, tkr
# Encoders Models
from .encoder_mdl import _encoder_lstm, _encoder_lstm2, _encoder_batch2_lstm2_drop2, _encoder_bilstm_state, \
    _encoder_bilstm2
from .encoder_mdl import _encoder_conv1d, _encoder_multihead_conv1d_lstm
# Decoders Models
from .decoder_mdl import _decoder_lstm, _decoder_lstm2, _decoder_lstm2_bach_drop, _decoder_bilstm, _decoder_bilstm2
from .decoder_mdl import _decoder_bilstm_time_dist


class seq2seq_lstm(tkm.Model):
    def __init__(self, n_future=None, n_out_ft=None, config=None):
        super(seq2seq_lstm, self).__init__()
        self.encoder = _encoder_lstm(n_future)
        self.decoder = _decoder_lstm(n_out_ft)

    def call(self, inputs):
        seq2seq = self.encoder(inputs)
        seq2seq = self.decoder(seq2seq)
        return seq2seq


class seq2seq_lstm2(tkm.Model):
    def __init__(self, n_future=None, n_out_ft=None, config=None):
        super(seq2seq_lstm2, self).__init__()
        self.encoder = _encoder_lstm2(n_future)
        self.decoder = _decoder_lstm2(n_out_ft)

    def call(self, inputs):
        seq2seq = self.encoder(inputs)
        seq2seq = self.decoder(seq2seq)
        return seq2seq


class seq2seq_lstm_batch_drop(tkm.Model):

    def __init__(self, n_future=None, n_out_ft=None, config=None):
        super(seq2seq_lstm_batch_drop, self).__init__()
        self.encoder = _encoder_batch2_lstm2_drop2(n_future)
        self.decoder = _decoder_lstm2_bach_drop(n_out_ft)

    def call(self, inputs):
        seq2seq = self.encoder(inputs)
        seq2seq = self.decoder(seq2seq)
        return seq2seq


class seq2seq_bilstm(tkm.Model):
    def __init__(self, n_future=None, n_out_ft=None, config=None):
        super(seq2seq_bilstm, self).__init__()
        self.encoder = _encoder_bilstm_state(n_future)
        self.decoder = _decoder_bilstm(n_out_ft)

    def call(self, inputs):
        seq2seq = self.encoder(inputs)
        seq2seq = self.decoder(seq2seq)
        return seq2seq


class seq2seq_bilstm2(tkm.Model):
    def __init__(self, n_future=None, n_out_ft=None, config=None):
        super(seq2seq_bilstm2, self).__init__()
        self.encoder = _encoder_bilstm2(n_future)
        self.decoder = _decoder_bilstm2(n_out_ft)

    def call(self, inputs):
        seq2seq = self.encoder(inputs)
        seq2seq = self.decoder(seq2seq)
        return seq2seq


class seq2seq_conv1d_bilstm(tkm.Model):
    def __init__(self, n_future=None, n_out_ft=None, config=None):
        super(seq2seq_conv1d_bilstm, self).__init__()
        self.encoder = _encoder_conv1d(n_future)
        self.decoder = _decoder_bilstm_time_dist(n_out_ft)

    def call(self, inputs):
        model = self.encoder(inputs)
        model = self.decoder(model)
        return model


'''
class seq2seq_multihead_conv1d_bilstm(tkm.Model):
    def __init__(self, n_future=None, n_out_ft=None, n_inp_ft=None, config=None):
        super(seq2seq_multihead_conv1d_bilstm, self).__init__()
        self.encoder = _encoder_multihead_conv1d_lstm(n_future, n_inp_ft)
        self.decoder = _decoder_bilstm_time_dist(n_out_ft)

    def call(self, inputs):
        model = self.encoder(inputs)
        model = self.decoder(model)
        return model
'''


def seq2seq_multihead_conv1d_bilstm(n_past, n_inp_ft, n_future, n_out_ft, units=128, dropout=0.2):
    input_layer = tkl.Input(shape=(n_past, n_inp_ft))
    head_list = []
    for i in range(0, n_inp_ft):
        conv_layer_head = tkl.Conv1D(
            filters=64, kernel_size=3, activation='relu', padding='causal', dilation_rate=2
        )(input_layer)
        conv_layer_head = tkl.Conv1D(filters=64, kernel_size=3, activation='relu')(conv_layer_head)
        conv_layer_flatten = tkl.Flatten()(conv_layer_head)
        head_list.append(conv_layer_flatten)
    concat_cnn = tkl.Concatenate(axis=1)(head_list)
    reshape = tkl.Reshape((head_list[0].shape[1], n_inp_ft))(concat_cnn)
    lstm = tkl.LSTM(units, activation='relu')(reshape)
    repeat = tkl.RepeatVector(n_future)(lstm)
    lstm_2 = tkl.LSTM(units, activation='relu', return_sequences=True)(repeat)
    dropout = tkl.Dropout(dropout)(lstm_2)
    dense = tkl.Dense(n_out_ft, activation='linear')(dropout)
    model = tkm.Model(inputs=input_layer, outputs=dense)
    return model


def seq2seq_bilstm_with_attention(n_past, n_inp_ft, n_future, n_out_ft, units=128, dropout=0.2):
    enc_inputs = tkl.Input(shape=(n_past, n_inp_ft))
    # ENCODER
    enc_stack_h, enc_last_h_fw, enc_last_c_fw, enc_last_h_bw, enc_last_c_bw = tkl.Bidirectional(
        tkl.LSTM(
            units, dropout=dropout, return_state=True, return_sequences=True
        )
    )(enc_inputs)
    # encoder_stack_h.shape=(None, 450, 256)
    encoder_last_h = tkl.concatenate([enc_last_h_fw, enc_last_h_bw])
    encoder_last_c = tkl.concatenate([enc_last_c_fw, enc_last_c_bw])
    # encoder_last_h.shape=(None, 256) ---> last hidden_state
    # encoder_last_c.shape(None, 256) ---> last cell state
    # DECODER
    dec_inputs = tkl.RepeatVector(n_future)(encoder_last_h)
    dec_stack_h = tkl.Bidirectional(
        tkl.LSTM(
            units, dropout=dropout, return_sequences=True
        )
    )(dec_inputs, initial_state=[enc_last_h_fw, enc_last_c_fw, enc_last_h_bw, enc_last_c_bw])
    # ATTENTION LAYER
    attention = tkl.dot([dec_stack_h, enc_stack_h], axes=[2, 2])
    attention = tkl.Activation('softmax')(attention)
    context = tkl.dot([attention, enc_stack_h], axes=[2, 1])
    dec_combined_context = tkl.concatenate([context, dec_stack_h])
    out = tkl.TimeDistributed(tkl.Dense(n_out_ft))(dec_combined_context)
    model = tkm.Model(inputs=enc_inputs, outputs=out, name='model')
    return model


def seq2seq_lstm_with_loung_attention(n_past, n_inp_ft, n_future, n_out_ft, units=128, dropout=0.2):

        input_train = tkl.Input(shape=(n_past, n_inp_ft))
        output_train = tkl.Input(shape=(n_future, n_out_ft))

        encoder_stack_h, encoder_last_h, encoder_last_c = tkl.LSTM(
            units,
            activation='elu',
            dropout=dropout,
            recurrent_dropout=0.2,
            return_state=True,
            return_sequences=True,
            kernel_regularizer=tkr.l2(0.01),
            recurrent_regularizer=tkr.l2(0.01),
            bias_regularizer=tkr.l2(0.01)
        )(input_train)
        encoder_last_h = tkl.BatchNormalization(momentum=0.6)(encoder_last_h)
        encoder_last_c = tkl.BatchNormalization(momentum=0.6)(encoder_last_c)
        # Repeat Vector
        decoder_input = tkl.RepeatVector(output_train.shape[1])(encoder_last_h)
        decoder_stack_h = tkl.LSTM(
            units,
            activation='elu',
            dropout=dropout,
            recurrent_dropout=0.2,
            return_state=False,
            return_sequences=True,
            kernel_regularizer=tkr.l2(0.01),
            recurrent_regularizer=tkr.l2(0.01),
            bias_regularizer=tkr.l2(0.01)
        )(decoder_input, initial_state=[encoder_last_h, encoder_last_c])
        attention = tkl.dot([decoder_stack_h, encoder_stack_h], axes=[2, 2])
        attention = tkl.Activation('softmax')(attention)
        context = tkl.dot([attention, encoder_stack_h], axes=[2, 1])
        context = tkl.BatchNormalization(momentum=0.6)(context)
        decoder_combined_context = tkl.concatenate([context, decoder_stack_h])
        out = tkl.TimeDistributed(tkl.Dense(output_train.shape[2]))(decoder_combined_context)
        built_model = tkm.Model(inputs=input_train, outputs=out, name='Seq2Seq_LSTM_with_Attention')
        return built_model
