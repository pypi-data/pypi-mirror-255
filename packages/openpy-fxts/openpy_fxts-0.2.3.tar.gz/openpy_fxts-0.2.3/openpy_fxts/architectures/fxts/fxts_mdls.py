# -*- coding: utf-8 -*-
# @Time    : 06/07/2023
# @Author  : Ing. Jorge Lara
# @Email   : jlara@iee.unsj.edu.ar
# @File    : ------------
# @Software: PyCharm

from openpy_fxts.architectures.baseline_arch import base_arch
from openpy_fxts.base_tf import tkl, tkm

# MLP
# Simple
from openpy_fxts.architectures.fxts.simple.MLP_class import mlp_dense_class
# Conv1D
# Simple
from openpy_fxts.architectures.fxts.simple.Conv1D_class import conv1D_dense, multi_conv1D_dense
# Hybrids
from openpy_fxts.architectures.fxts.hybrids.Conv1D_others import conv1d_birnn_dense, timedist_conv1d_birnn_dense, \
    conv1d_birnn_attention_dense
# BiRNN
# Simple
from openpy_fxts.architectures.fxts.simple.RNN_class import birnn_dense_class, multi_birnn_dense_class
# Hybrids
from openpy_fxts.architectures.fxts.hybrids.BiRNN_others import birnn_conv1d_dense, birnn_timedist_dense_class, \
    birnn_bahdanau_attention_conv1d_dense, birnn_luong_attention_conv1d_dense, birnn_multihead_attention_conv1d_dense
# Others
from openpy_fxts.architectures.fxts.hybrids.Others import tcn_bilstm, time2vec_bilstm
# Encoder - Decoder
from openpy_fxts.architectures.fxts.hybrids.EncDec_hybrids import encdec_birnn, encdec_conv1d_birnn
# Models -> seq2seq
from openpy_fxts.architectures.fxts.hybrids.seq2seq.Hybrids import seq2seq_lstm, seq2seq_lstm2, seq2seq_lstm_batch_drop, \
    seq2seq_bilstm, seq2seq_bilstm2, seq2seq_conv1d_bilstm, seq2seq_multihead_conv1d_bilstm, \
    seq2seq_bilstm_with_attention, seq2seq_lstm_with_loung_attention


class fxts_mdls(base_arch):

    def __init__(self, name_mdl, type_mdl, n_past, n_future, n_inp_ft, n_out_ft, config_arch):
        super().__init__(name_mdl, type_mdl, n_past, n_future, n_inp_ft, n_out_ft, config_arch)

    def models(self):
        # Simple - Hybrids models_fxts
        if self.type_mdl == 'MLP':
            return self._mlp_mdls()
        if self.type_mdl == 'BiRNN':
            return self._birnn_mdls()
        if self.type_mdl == 'Conv1D':
            return self._conv1d_mdls()
        if self.type_mdl == 'Others':
            return self._others_mdls()
        if self.type_mdl == 'Stacked':
            return self._stacked_mdls()
        if self.type_mdl == 'EncDec':
            return self._encdec_mdls()
        if self.type_mdl == 'seq2seq':
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
            x = timedist_conv1d_birnn_dense(self.n_future, self.n_out_ft, self.config_arch)(input_layer)
            return tkm.Model(inputs=input_layer, outputs=x, name=self.name_mdl)
        if self.name_mdl == 'Conv1D_BiRNN_Attention':
            x = conv1d_birnn_attention_dense(self.n_future, self.n_out_ft, self.config_arch)(input_layer)
            return tkm.Model(inputs=[input_layer], outputs=x, name=self.name_mdl)

    def _others_mdls(self):
        input_layer = tkl.Input(shape=(self.n_past, self.n_inp_ft))
        if self.name_mdl == 'TCN_BiRNN':
            x = tcn_bilstm(self.n_future, self.n_out_ft, self.config_arch)(input_layer)
            return tkm.Model(inputs=input_layer, outputs=x, name=self.name_mdl)
        if self.name_mdl == 'Time2Vec_BiRNN':
            x = time2vec_bilstm(self.n_future, self.n_out_ft, self.config_arch)(input_layer)
            return tkm.Model(inputs=input_layer, outputs=x, name=self.name_mdl)

    def _stacked_mdls(self):
        input_layer = tkl.Input(shape=(self.n_past, self.n_inp_ft))
        if self.name_mdl == 'LSTM_Stacked':
            x = lstm_stacked(self.n_future, self.n_out_ft, self.config_arch)(input_layer)
            return tkm.Model(inputs=input_layer, outputs=x, name=self.name_mdl)
        if self.name_mdl == 'BiRNN_Stacked':
            x = bilstm_stacked(self.n_future, self.n_out_ft, self.config_arch)(input_layer)
            return tkm.Model(inputs=input_layer, outputs=x, name=self.name_mdl)
        if self.name_mdl == 'Stacked_SciNet':
            x = stackedscinet(self.n_future, self.n_out_ft, self.config_arch)(input_layer)
            return tkm.Model(inputs=input_layer, outputs=x, name=self.name_mdl)

    def _encdec_mdls(self):
        input_layer = tkl.Input(shape=(self.n_past, self.n_inp_ft))
        if self.name_mdl == 'EncDec_BiRNN':
            x = encdec_birnn(self.n_future, self.n_out_ft, self.config_arch)(input_layer)
            return tkm.Model(inputs=input_layer, outputs=x, name=self.name_mdl)
        if self.name_mdl == 'EncDec_Conv1D_BiRNN':
            x = encdec_conv1d_birnn(self.n_future, self.n_out_ft, self.config_arch)(input_layer)
            return tkm.Model(inputs=input_layer, outputs=x, name=self.name_mdl)

    def _seq2seq_mdls(self):
        input_layer = tkl.Input(shape=(self.n_past, self.n_inp_ft))
        if self.name_mdl == 'Seq2Seq_BiRNN':
            x = seq2seq_lstm(self.n_future, self.n_out_ft, self.config_arch)(input_layer)
            return tkm.Model(inputs=input_layer, outputs=x, name=self.name_mdl)
        if self.name_mdl == 'Seq2Seq_LSTM2':
            x = seq2seq_lstm2(self.n_future, self.n_out_ft, self.config_arch)(input_layer)
            return tkm.Model(inputs=input_layer, outputs=x, name=self.name_mdl)
        if self.name_mdl == 'Seq2Seq_RNN_Batch_Drop':
            x = seq2seq_lstm_batch_drop(self.n_future, self.n_out_ft, self.config_arch)(input_layer)
            return tkm.Model(inputs=input_layer, outputs=x, name=self.name_mdl)
        if self.name_mdl == 'Seq2Seq_BiRNN':
            x = seq2seq_bilstm(self.n_future, self.n_out_ft, self.config_arch)(input_layer)
            return tkm.Model(inputs=input_layer, outputs=x, name=self.name_mdl)
        if self.name_mdl == 'Seq2Seq_BiLSTM2':
            x = seq2seq_bilstm2(self.n_future, self.n_out_ft, self.config_arch)(input_layer)
            return tkm.Model(inputs=input_layer, outputs=x, name=self.name_mdl)
        if self.name_mdl == 'Seq2Seq_Conv1D_BiRNN':
            x = seq2seq_conv1d_bilstm(self.n_future, self.n_out_ft, self.config_arch)(input_layer)
            return tkm.Model(inputs=input_layer, outputs=x, name=self.name_mdl)
        if self.name_mdl == 'Seq2Seq_Multi_Head_Conv1D_BiRNN':
            return seq2seq_multihead_conv1d_bilstm(self.n_past, self.n_inp_ft, self.n_future, self.n_out_ft)
        if self.name_mdl == 'Seq2Seq_BiRNN_with_Attention':
            return seq2seq_bilstm_with_attention(self.n_past, self.n_inp_ft, self.n_future, self.n_out_ft)
        if self.name_mdl == 'Seq2Seq_RNN_with_Luong_Attention':
            return seq2seq_lstm_with_loung_attention(self.n_past, self.n_inp_ft, self.n_future, self.n_out_ft)
