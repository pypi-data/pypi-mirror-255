# -*- coding: utf-8 -*-
# @Time    : 06/07/2023
# @Author  : Ing. Jorge Lara
# @Email   : jlara@iee.unsj.edu.ar
# @File    : ------------
# @Software: PyCharm

from openpy_fxts.architectures.baseline_arch import base_arch
from openpy_fxts.base_tf import tkl, tkm, value_miss
# Simple
# models_fxts -> MLP
from openpy_fxts.architectures.mdits.simple.MLP_class import mlp_dense_class

# models_fxts -> BiRNN
# Simple
from openpy_fxts.architectures.mdits.simple.RNN_class import birnn_dense_class, multi_birnn_dense_class
# Hybrids
from openpy_fxts.architectures.mdits.hybrids.BiRNN_others import birnn_conv1d_dense, birnn_timedist_dense_class, \
    birnn_bahdanau_attention_conv1d_dense, birnn_luong_attention_conv1d_dense, birnn_multihead_attention_conv1d_dense
# Models -> Conv1D
# Simple
from openpy_fxts.architectures.mdits.simple.Conv1D_class import conv1D_dense, multi_conv1D_dense
# Hybrids
from openpy_fxts.architectures.mdits.hybrids.Conv1D_others import conv1d_birnn_dense
from openpy_fxts.architectures.mdits.hybrids.Conv1D_others import timedist_conv1d_birnn_dense
from openpy_fxts.architectures.mdits.hybrids.Conv1D_others import conv1d_birnn_attention_dense
# models_fxts -> Others
from openpy_fxts.architectures.mdits.hybrids.class_mdls.Others import tcn_bilstm
from openpy_fxts.architectures.mdits.hybrids.class_mdls.Others import time2vec_bilstm
# models_fxts -> EncDec
from openpy_fxts.architectures.mdits.hybrids.EncDec_hybrids import encdec_birnn, encdec_conv1d_birnn


# models_fxts -> LSTM
from openpy_fxts.architectures.mdits.hybrids.class_mdls.LSTM_others import lstm2_dense
# models_fxts -> BiLSTM
from openpy_fxts.architectures.mdits.hybrids.class_mdls.BiLSTM_others import bilstm_dense
from openpy_fxts.architectures.mdits.hybrids.class_mdls.BiLSTM_others import bilstm_conv1d_dense
from openpy_fxts.architectures.mdits.hybrids.class_mdls.BiLSTM_others import bilstm_bahdanau_attention_conv1d_dense
from openpy_fxts.architectures.mdits.hybrids.class_mdls.BiLSTM_others import bilstm_multihead_attention_conv1d_dense
from openpy_fxts.architectures.mdits.hybrids.class_mdls.BiLSTM_others import bilstm_luong_attention_conv1d_dense
# models_fxts -> Conv1D
from openpy_fxts.architectures.mdits.hybrids.class_mdls.Conv1D_others import conv1D_lstm_dense
from openpy_fxts.architectures.mdits.hybrids.class_mdls.Conv1D_others import conv1D_bilstm_dense
from openpy_fxts.architectures.mdits.hybrids.class_mdls.Conv1D_others import conv1D_bilstm_attention_dense
# models_fxts -> GRU
from openpy_fxts.architectures.mdits.hybrids.class_mdls.GRU_others import gru2_dense
# models_fxts -> Stacked
from openpy_fxts.architectures.mdits.hybrids.class_mdls.Stacked_others import lstm_stacked
from openpy_fxts.architectures.mdits.hybrids.class_mdls.Stacked_others import bilstm_stacked
from openpy_fxts.architectures.mdits.hybrids.class_mdls.Stacked_others import stackedscinet
# models_fxts -> Seq2Seq
from openpy_fxts.architectures.mdits.hybrids.class_mdls.Seq2Seq_hybrids import seq2seq_lstm
from openpy_fxts.architectures.mdits.hybrids.class_mdls.Seq2Seq_hybrids import seq2seq_lstm2
from openpy_fxts.architectures.mdits.hybrids.class_mdls.Seq2Seq_hybrids import seq2seq_lstm_batch_drop
from openpy_fxts.architectures.mdits.hybrids.class_mdls.Seq2Seq_hybrids import seq2seq_bilstm
from openpy_fxts.architectures.mdits.hybrids.class_mdls.Seq2Seq_hybrids import seq2seq_bilstm2
from openpy_fxts.architectures.mdits.hybrids.class_mdls.Seq2Seq_hybrids import seq2seq_conv1d_bilstm
from openpy_fxts.architectures.mdits.hybrids.class_mdls.Seq2Seq_hybrids import seq2seq_multihead_conv1d_bilstm  # Function
from openpy_fxts.architectures.mdits.hybrids.class_mdls.Seq2Seq_hybrids import seq2seq_bilstm_with_attention  # Function
from openpy_fxts.architectures.mdits.hybrids.class_mdls.Seq2Seq_hybrids import seq2seq_lstm_with_loung_attention  # Function


class mdits_mdls(base_arch):

    def __init__(self, name_mdl, type_mdl, n_past, n_future, n_inp_ft, n_out_ft, config_arch):
        super().__init__(name_mdl, type_mdl, n_past, n_future, n_inp_ft, n_out_ft, config_arch)

    def models(self):
        if self.type_mdl == 'MLP':
            return self._mlp_mdls()
        if self.type_mdl == 'Conv1D':
            return self._conv1d_mdls()
        if self.type_mdl == 'BiRNN':
            return self._birnn_mdls()
        if self.type_mdl == 'Others':
            return self._others_mdls()
        if self.type_mdl == 'EncDec':
            return self._encdec_mdls()
        if self.type_mdl == 'LSTM':
            return self._lstm_mdls()
        if self.type_mdl == 'GRU':
            return self._gru_mdls()
        if self.type_mdl == 'BiLSTM':
            return self._bilstm_mdls()
        if self.type_mdl == 'Stacked':
            return self._stacked_mdls()
        if self.type_mdl == 'Seq2Seq':
            return self._seq2seq_mdls()

    def _mlp_mdls(self):
        input_layer = []
        for i in range(self.n_inp_ft):
            input_layer.append(tkl.Input(shape=(self.n_past,)))
        if self.name_mdl == 'MLP_Dense':
            x = mlp_dense_class(self.n_past, self.n_inp_ft, self.n_future, self.n_out_ft, self.config_arch)(input_layer)
            return tkm.Model(inputs=input_layer, outputs=x, name=self.name_mdl)

    def _birnn_mdls(self):
        input_layer = tkl.Input(shape=(self.n_past, self.n_inp_ft))
        input_layer = tkl.Masking(mask_value=value_miss)(input_layer)
        # Simple
        if self.name_mdl == 'BiRNN_Dense':
            x = birnn_dense_class(self.n_future, self.n_out_ft, self.config_arch)(input_layer)
            return tkm.Model(inputs=input_layer, outputs=x, name=self.name_mdl)
        if self.name_mdl == 'Multi_BiRNN_Dense':
            x = multi_birnn_dense_class(
                self.n_past, self.n_inp_ft, self.n_future, self.n_out_ft, self.config_arch
            )(input_layer)
            return tkm.Model(inputs=input_layer, outputs=x, name=self.name_mdl)
        # Hybrids
        if self.name_mdl == 'BiRNN_Conv1D':
            x = birnn_conv1d_dense(self.n_future, self.n_out_ft, self.config_arch)(input_layer)
            return tkm.Model(inputs=[input_layer], outputs=x, name=self.name_mdl)
        if self.name_mdl == 'BiRNN_TimeDist_Dense':
            x = birnn_timedist_dense_class(self.n_future, self.n_out_ft, self.config_arch)(input_layer)
            return tkm.Model(inputs=input_layer, outputs=x, name=self.name_mdl)
        if self.name_mdl == 'BiRNN_Bahdanau_Attention_Conv1D':
            x = birnn_bahdanau_attention_conv1d_dense(self.n_future, self.n_out_ft, self.config_arch)(input_layer)
            return tkm.Model(inputs=input_layer, outputs=x, name=self.name_mdl)
        if self.name_mdl == 'BiRNN_Luong_Attention_Conv1D':
            x = birnn_luong_attention_conv1d_dense(self.n_future, self.n_out_ft, self.config_arch)(input_layer)
            return tkm.Model(inputs=input_layer, outputs=x, name=self.name_mdl)
        if self.name_mdl == 'BiRNN_MultiHeadAttention_Conv1D':
            x = birnn_multihead_attention_conv1d_dense(self.n_future, self.n_out_ft, self.config_arch)(input_layer)
            return tkm.Model(inputs=input_layer, outputs=x, name=self.name_mdl)

    def _others_mdls(self):
        input_layer = tkl.Input(shape=(self.n_past, self.n_inp_ft))
        input_layer = tkl.Masking(mask_value=value_miss)(input_layer)
        if self.name_mdl == 'TCN_BiRNN':
            x = tcn_bilstm(self.n_future, self.n_out_ft, self.config_arch)(input_layer)
            return tkm.Model(inputs=input_layer, outputs=x)
        if self.name_mdl == 'Time2Vec_BiRNN':
            x = time2vec_bilstm(self.n_future, self.n_out_ft, self.config_arch)(input_layer)
            return tkm.Model(inputs=input_layer, outputs=x)

    def _encdec_mdls(self):
        input_layer = tkl.Input(shape=(self.n_past, self.n_inp_ft))
        if self.name_mdl == 'EncDec_BiRNN':
            x = encdec_birnn(self.n_future, self.n_out_ft, self.config_arch)(input_layer)
            return tkm.Model(inputs=input_layer, outputs=x, name=self.name_mdl)
        if self.name_mdl == 'EncDec_Conv1D_BiRNN':
            x = encdec_conv1d_birnn(self.n_future, self.n_out_ft, self.config_arch)(input_layer)
            return tkm.Model(inputs=input_layer, outputs=x, name=self.name_mdl)

    def _lstm_mdls(self):
        input_layer = tkl.Input(shape=(self.n_past, self.n_inp_ft))
        if self.name_mdl == 'LSTM2_Dense':
            x = lstm2_dense(self.n_future, self.n_out_ft, self.config_arch)(input_layer)
            return tkm.Model(inputs=input_layer, outputs=x)

    def _gru_mdls(self):
        input_layer = tkl.Input(shape=(self.n_past, self.n_inp_ft))
        if self.name_mdl == 'GRU2_Dense':
            x = gru2_dense(self.n_future, self.n_out_ft, self.config_arch)(input_layer)
            return tkm.Model(inputs=input_layer, outputs=x)

    def _bilstm_mdls(self):
        input_layer = tkl.Input(shape=(self.n_past, self.n_inp_ft))
        if self.name_mdl == 'BiLSTM_Dense':
            x = bilstm_dense(self.n_future, self.n_out_ft, self.config_arch)(input_layer)
            return tkm.Model(inputs=[input_layer], outputs=x)
        if self.name_mdl == 'BiLSTM_Conv1D':
            x = bilstm_conv1d_dense(self.n_future, self.n_out_ft, self.config_arch)(input_layer)
            return tkm.Model(inputs=[input_layer], outputs=x)
        if self.name_mdl == 'BiLSTM_Bahdanau_Attention_Conv1D':
            x = bilstm_bahdanau_attention_conv1d_dense(self.n_future, self.n_out_ft, self.config_arch)(input_layer)
            return tkm.Model(inputs=input_layer, outputs=x)
        if self.name_mdl == 'BiLSTM_MultiHeadAttention_Conv1D':
            x = bilstm_multihead_attention_conv1d_dense(self.n_future, self.n_out_ft, self.config_arch)(input_layer)
            return tkm.Model(inputs=input_layer, outputs=x)
        if self.name_mdl == 'BiLSTM_Luong_Attention_Conv1D':
            x = bilstm_luong_attention_conv1d_dense(self.n_future, self.n_out_ft, self.config_arch)(input_layer)
            return tkm.Model(inputs=input_layer, outputs=x)

    def _conv1d_mdls(self):
        input_layer = tkl.Input(shape=(self.n_past, self.n_inp_ft))
        # Simple
        if self.name_mdl == 'Conv1D_Dense':
            x = conv1D_dense(self.n_future, self.n_out_ft, self.config_arch)(input_layer)
            return tkm.Model(inputs=input_layer, outputs=x, name=self.name_mdl)
        if self.name_mdl == 'Multi_Conv1D_Dense':
            x = multi_conv1D_dense(
                self.n_inp_ft, self.n_future, self.n_out_ft, self.config_arch
            )(input_layer)
            return tkm.Model(inputs=input_layer, outputs=x, name=self.name_mdl)
        # Hybrids
        if self.name_mdl == 'Conv1D_BiRNN':
            x = conv1d_birnn_dense(self.n_future, self.n_out_ft, self.config_arch)(input_layer)
            return tkm.Model(inputs=input_layer, outputs=x, name=self.name_mdl)
        if self.name_mdl == 'TimeDist_Conv1D_BiRNN':
            input_layer = tkl.Input(shape=(self.n_past, self.n_inp_ft, 1))
            input_layer = tkl.Masking(mask_value=value_miss)(input_layer)
            x = timedist_conv1d_birnn_dense(self.n_future, self.n_out_ft, self.config_arch)(input_layer)
            return tkm.Model(inputs=input_layer, outputs=x, name=self.name_mdl)
        if self.name_mdl == 'Conv1D_BiRNN_Attention':
            x = conv1d_birnn_attention_dense(self.n_future, self.n_out_ft, self.config_arch)(input_layer)
            return tkm.Model(inputs=[input_layer], outputs=x, name=self.name_mdl)


        if self.name_mdl == 'Conv1D_LSTM':
            x = conv1D_lstm_dense(self.n_future, self.n_out_ft, self.config_arch)(input_layer)
            return tkm.Model(inputs=input_layer, outputs=x)
        if self.name_mdl == 'Conv1D_BiLSTM':
            x = conv1D_bilstm_dense(self.n_future, self.n_out_ft, self.config_arch)(input_layer)
            return tkm.Model(inputs=input_layer, outputs=x)
        if self.name_mdl == 'Conv1D_BiLSTM_Attention':
            x = conv1D_bilstm_attention_dense(self.n_future, self.n_out_ft, self.config_arch)(input_layer)
            return tkm.Model(inputs=[input_layer], outputs=x)

    def _stacked_mdls(self):
        input_layer = tkl.Input(shape=(self.n_past, self.n_inp_ft))
        if self.name_mdl == 'LSTM_Stacked':
            x = lstm_stacked(self.n_future, self.n_out_ft, self.config_arch)(input_layer)
            return tkm.Model(inputs=input_layer, outputs=x)
        if self.name_mdl == 'BiLSTM_Stacked':
            x = bilstm_stacked(self.n_future, self.n_out_ft, self.config_arch)(input_layer)
            return tkm.Model(inputs=input_layer, outputs=x)
        if self.name_mdl == 'Stacked_SciNet':
            x = stackedscinet(self.n_future, self.n_out_ft, self.config_arch)(input_layer)
            return tkm.Model(inputs=input_layer, outputs=x)

    def _seq2seq_mdls(self):
        input_layer = tkl.Input(shape=(self.n_past, self.n_inp_ft))
        if self.name_mdl == 'Seq2Seq_LSTM':
            x = seq2seq_lstm(self.n_future, self.n_out_ft, self.config_arch)(input_layer)
            return tkm.Model(inputs=input_layer, outputs=x)
        if self.name_mdl == 'Seq2Seq_LSTM2':
            x = seq2seq_lstm2(self.n_future, self.n_out_ft, self.config_arch)(input_layer)
            return tkm.Model(inputs=input_layer, outputs=x)
        if self.name_mdl == 'Seq2Seq_LSTM_Batch_Drop':
            x = seq2seq_lstm_batch_drop(self.n_future, self.n_out_ft, self.config_arch)(input_layer)
            return tkm.Model(inputs=input_layer, outputs=x)
        if self.name_mdl == 'Seq2Seq_BiLSTM':
            x = seq2seq_bilstm(self.n_future, self.n_out_ft, self.config_arch)(input_layer)
            return tkm.Model(inputs=input_layer, outputs=x)
        if self.name_mdl == 'Seq2Seq_BiLSTM2':
            x = seq2seq_bilstm2(self.n_future, self.n_out_ft, self.config_arch)(input_layer)
            return tkm.Model(inputs=input_layer, outputs=x)
        if self.name_mdl == 'Seq2Seq_Conv1D_BiLSTM':
            x = seq2seq_conv1d_bilstm(self.n_future, self.n_out_ft, self.config_arch)(input_layer)
            return tkm.Model(inputs=input_layer, outputs=x)
        if self.name_mdl == 'Seq2Seq_Multi_Head_Conv1D_BiLSTM':
            return seq2seq_multihead_conv1d_bilstm(self.n_past, self.n_inp_ft, self.n_future, self.n_out_ft)
        if self.name_mdl == 'Seq2Seq_BiLSTM_with_Attention':
            return seq2seq_bilstm_with_attention(self.n_past, self.n_inp_ft, self.n_future, self.n_out_ft)
        if self.name_mdl == 'Seq2Seq_LSTM_with_Luong_Attention':
            return seq2seq_lstm_with_loung_attention(self.n_past, self.n_inp_ft, self.n_future, self.n_out_ft)
