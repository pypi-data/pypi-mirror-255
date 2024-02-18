from openpy_fxts.base_tf import tkm, tkl, tf


class _encoder_lstm(tkm.Model):
    def __init__(self, n_future=None):
        super(_encoder_lstm, self).__init__()
        self.lstm = tkl.LSTM(256, return_state=True)
        self.rep_vec = tkl.RepeatVector(n_future)

    def call(self, inputs, training=True, **kwargs):
        encoder_outputs1 = self.lstm(inputs)
        encoder_states1 = encoder_outputs1[1:]
        decoder_inputs = self.rep_vec(encoder_outputs1[0])
        return [decoder_inputs, encoder_states1]


class _encoder_lstm2(tkm.Model):
    def __init__(self, n_future=None):
        super(_encoder_lstm2, self).__init__()
        self.encoder_l1 = tkl.LSTM(256, return_sequences=True, return_state=True)
        self.encoder_l2 = tkl.LSTM(256, return_state=True)
        self.rep_vec = tkl.RepeatVector(n_future)

    def call(self, inputs, training=True, **kwargs):
        encoder_outputs1 = self.encoder_l1(inputs)
        encoder_states1 = encoder_outputs1[1:]
        encoder_outputs2 = self.encoder_l2(encoder_outputs1[0])
        encoder_states2 = encoder_outputs2[1:]
        decoder_inputs = self.rep_vec(encoder_outputs2[0])
        return [decoder_inputs, encoder_states1, encoder_states2]


class _encoder_batch2_lstm2_drop2(tkm.Model):

    def __init__(self, n_future=None):
        super(_encoder_batch2_lstm2_drop2, self).__init__()
        self.batch = tkl.BatchNormalization()
        self.lstm1 = tkl.LSTM(256, return_sequences=True)
        self.drop = tkl.Dropout(0.2)
        self.lstm2 = tkl.LSTM(256, return_sequences=False)
        self.rep_vec = tkl.RepeatVector(n_future)

    def call(self, inputs, training=True, **kwargs):
        encoder_input = self.batch(inputs)
        encoder_h1 = self.lstm1(encoder_input)
        encoder_h1 = self.drop(encoder_h1)
        encoder_out = self.lstm2(encoder_h1)
        encoder_out = self.drop(encoder_out)

        encoder_out = self.rep_vec(encoder_out)
        return encoder_out


class _encoder_bilstm_state(tkm.Model):
    def __init__(self, n_future=None):
        super(_encoder_bilstm_state, self).__init__()
        self.bilstm = tkl.Bidirectional(tkl.LSTM(256, return_state=True))
        self.rep_vec = tkl.RepeatVector(n_future)

    def call(self, inputs, training=True, **kwargs):
        encoder_outputs1 = self.bilstm(inputs)
        encoder_states1 = encoder_outputs1[1:]
        decoder_inputs = self.rep_vec(encoder_outputs1[0])
        return [decoder_inputs, encoder_states1]


class _encoder_bilstm_state_sequence(tkm.Model):
    def __init__(self, n_future=None):
        super(_encoder_bilstm_state_sequence, self).__init__()
        self.bilstm = tkl.Bidirectional(tkl.LSTM(128, dropout=0.2, return_state=True, return_sequences=True))
        self.concat = tkl.concatenate()
        self.rep_vec = tkl.RepeatVector(n_future)

    def call(self, inputs, training=True, **kwargs):
        encoder_stack_h, encoder_last_h_fw, encoder_last_c_fw, encoder_last_h_bw, encoder_last_c_bw = self.bilstm(inputs)
        encoder_last_h = tf.concat([encoder_last_h_fw, encoder_last_h_bw])
        encoder_last_c = tf.concat([encoder_last_c_fw, encoder_last_c_bw])
        decoder_inputs = self.rep_vec(encoder_last_h)
        return [decoder_inputs, encoder_last_h_fw, encoder_last_c_fw, encoder_last_h_bw, encoder_last_c_bw]


class _encoder_bilstm2(tkm.Model):
    def __init__(self, n_future=None):
        super(_encoder_bilstm2, self).__init__()
        self.encoder_l1 = tkl.Bidirectional(tkl.LSTM(256, return_sequences=True, return_state=True))
        self.encoder_l2 = tkl.Bidirectional(tkl.LSTM(256, return_state=True))
        self.rep_vec = tkl.RepeatVector(n_future)

    def call(self, inputs, training=True, **kwargs):
        encoder_outputs1 = self.encoder_l1(inputs)
        encoder_states1 = encoder_outputs1[1:]
        encoder_outputs2 = self.encoder_l2(encoder_outputs1[0])
        encoder_states2 = encoder_outputs2[1:]
        decoder_inputs = self.rep_vec(encoder_outputs2[0])
        return [decoder_inputs, encoder_states1, encoder_states2]
    

class _encoder_conv1d(tkm.Model):
    def __init__(self, n_future=None):
        super(_encoder_conv1d, self).__init__()
        self.conv1d1 = tkl.Conv1D(filters=64, kernel_size=3, activation='relu', padding='causal', dilation_rate=2)
        self.conv1d2 = tkl.Conv1D(filters=64, kernel_size=3, activation='relu', padding='causal')
        self.conv1d3 = tkl.Conv1D(filters=64, kernel_size=3, activation='relu')
        self.max_pool1d = tkl.MaxPooling1D(pool_size=2)
        self.flatten = tkl.Flatten()
        self.rep_vec = tkl.RepeatVector(n_future)

    def call(self, inputs, training=True, **kwargs):
        x = self.conv1d1(inputs)
        x = self.conv1d2(x)
        x = self.conv1d3(x)
        x = self.max_pool1d(x)
        x = self.flatten(x)
        x = self.rep_vec(x)
        return x


class _encoder_multihead_conv1d_lstm(tkm.Model):
    def __init__(self, n_future=None, n_inp_ft=None, i=None):
        super(_encoder_multihead_conv1d_lstm, self).__init__()
        self.n_inp_ft = n_inp_ft
        self.i = i
        self.conv1d = tkl.Conv1D(filters=64, kernel_size=3, activation='relu')
        self.max_pool1d = tkl.MaxPooling1D(pool_size=2)
        self.flatten = tkl.Flatten()
        self.reshape = tkl.Reshape((self.i[0].shape[1], n_inp_ft))
        self.concat = tkl.Concatenate(axis=1)
        self.lstm = tkl.LSTM(256, activation='relu')
        self.rep_vec = tkl.RepeatVector(n_future)


    def call(self, inputs, training=True, **kwargs):
        head_list = []
        for i in range(0, self.n_inp_ft):
            x = self.conv1d(inputs)
            x = self.flatten(x)
            head_list.append(x)

        x = self.concat(head_list)
        self.i = x
        x = self.reshape(x)
        x = self.lstm(x)
        x = self.rep_vec(x)
        return x
