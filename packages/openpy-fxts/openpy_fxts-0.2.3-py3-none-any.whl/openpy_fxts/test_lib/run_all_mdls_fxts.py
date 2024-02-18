# -*- coding: utf-8 -*-
# @Time    : 10/07/2023
# @Author  : Ing. Jorge Lara
# @Email   : jlara@iee.unsj.edu.ar
# @File    : ------------
# @Software: PyCharm

import pandas as pd
import os
import pathlib
import openpy_fxts.models.forecast as fxts


class run_all_models:

    def __init__(
            self,
            config_data: dict = None,
            config_mdl: dict = None,
            config_sim: dict = None,
            config_arch: dict = None,
            source: str = None,
            type_mdl: str = None,
            name_mdl: str = None,
            train: int = None,
            test: int = None,
            folder: str = 'architectures',
            view: bool = False
    ):
        self.config_data = config_data
        self.config_mdl = config_mdl
        self.config_sim = config_sim
        self.config_arch = config_arch
        self.source = source
        self.type_mdl = type_mdl
        self.name_mdl = name_mdl
        self.train = train
        self.test = test
        self.folder = folder
        self.view = view
        name_folder, mttr_upd = fxts.date_init_final(self.config_data)
        self.name_folder = name_folder
        self.mttr_upd = mttr_upd

    def _run_train(self, object_class):
        mdl = object_class(self.config_data, self.config_mdl, self.config_sim, self.config_arch)
        if mdl.name_mdl is None:
            mdl.name_mdl = self.name_mdl
        print(mdl.name_mdl)
        path = pathlib.Path(self.source).joinpath(
            self.folder, mdl.type_mdl, mdl.name_mdl, self.mttr_upd, self.name_folder
        )
        return mdl.training_mdl(path)

    def _run_test(self, object_class):
        mdl = object_class(self.config_data, self.config_mdl, self.config_sim, self.config_arch)
        if mdl.name_mdl is None:
            mdl.name_mdl = self.name_mdl
        print(mdl.name_mdl)
        path = pathlib.Path(self.source).joinpath(
            self.folder, mdl.type_mdl, mdl.name_mdl, self.mttr_upd, self.name_folder
        )
        return mdl.prediction_mdl(path)

    def run_case_mdl(self, object_class):
        if self.train == 1 and self.test == 0:
            return self._run_train(object_class)
        if self.train == 0 and self.test == 1:
            return self._run_test(object_class)
        if self.train == 1 and self.test == 1:
            return self._run_test(object_class)

    def execute_case(self):
        # Simple - Hybrids models_fxts
        if self.type_mdl == 'MLP':
            return self._mlp()
        if self.type_mdl == 'BiRNN':
            return self._birnn()
        if self.type_mdl == 'Conv1D':
            return self._conv1d()
        if self.type_mdl == 'Others':
            return self._others()
        if self.type_mdl == 'EncDec':
            return self._encdec()
        else:
            return None
        '''
        if self.type_mdl == 'Stacked':
            return self._stacked()
        if self.type_mdl == 'seq2seq':
            return self._seq2seq()
        '''


    def _mlp(self):
        if self.name_mdl == 'MLP_Dense':
            return self.run_case_mdl(fxts.MLP_Dense_class)

    def _birnn(self):
        # Simple models_fxts
        if self.name_mdl == 'BiRNN_Dense':
            return self.run_case_mdl(fxts.BiRNN_Dense_class)
        if self.name_mdl == 'Multi_BiRNN_Dense':
            return self.run_case_mdl(fxts.Multi_BiRNN_Dense_class)
        # Hybrids models_fxts
        if self.name_mdl == 'BiRNN_Conv1D':
            return self.run_case_mdl(fxts.BiRNN_Conv1D_class)
        if self.name_mdl == 'BiRNN_TimeDist_Dense':
            return self.run_case_mdl(fxts.BiRNN_TimeDist_Dense_class)
        if self.name_mdl == 'BiRNN_Bahdanau_Attention_Conv1D':
            return self.run_case_mdl(fxts.BiRNN_Bahdanau_Attention_Conv1D_class)
        if self.name_mdl == 'BiRNN_Luong_Attention_Conv1D':
            return self.run_case_mdl(fxts.BiRNN_Luong_Attention_Conv1D_class)
        if self.name_mdl == 'BiRNN_MultiHeadAttention_Conv1D':
            return self.run_case_mdl(fxts.BiRNN_MultiHeadAttention_Conv1D_class)
        if self.name_mdl == 'BiRNN_MDN':
            pass
            #return self.run_case_mdl(fxts.BiRNN_MDN)

    def _conv1d(self):
        # Simple
        if self.name_mdl == 'Conv1D_Dense':
            return self.run_case_mdl(fxts.Conv1D_Dense_class)
        if self.name_mdl == 'Multi_Conv1D_Dense':
            return self.run_case_mdl(fxts.Multi_Conv1D_Dense_class)
        # Hybrids
        if self.name_mdl == 'Conv1D_BiRNN':
            return self.run_case_mdl(fxts.Conv1D_BiRNN_class)
        if self.name_mdl == 'TimeDist_Conv1D_BiRNN':
            return self.run_case_mdl(fxts.TimeDist_Conv1D_BiRNN_class)
        if self.name_mdl == 'Conv1D_BiRNN_Attention':
            return self.run_case_mdl(fxts.Conv1D_BiRNN_Attention_class)

    def _others(self):
        if self.name_mdl == 'TCN_BiRNN':
            return self.run_case_mdl(fxts.TCN_BiRNN_class)
        if self.name_mdl == 'Time2Vec_BiRNN':
            return self.run_case_mdl(fxts.Time2Vec_BiRNN_class)

    def _encdec(self):
        if self.name_mdl == 'EncDec_BiRNN':
            return self.run_case_mdl(fxts.EncDec_BiRNN_class)
        if self.name_mdl == 'EncDec_Conv1D_BiRNN':
            return self.run_case_mdl(fxts.EncDec_Conv1D_BiRNN_class)
    '''
    def _stacked(self):
        if self.name_mdl == 'BiRNN_Stacked':
            return self.run_case_mdl(forecast.RNN_Stacked)
        if self.name_mdl == 'BiRNN_Stacked':
            return self.run_case_mdl(forecast.BiLSTM_Stacked)
        if self.name_mdl == 'Stacked_SciNet':
            return self.run_case_mdl(forecast.Stacked_SciNet)

    def _seq2seq(self):
        if self.name_mdl == 'Seq2Seq_RNN':
            return self.run_case_mdl(forecast.Seq2Seq_RNN_class)
        if self.name_mdl == 'Seq2Seq_RNN2':
            return self.run_case_mdl(forecast.Seq2Seq_RNN2_class)
        if self.name_mdl == 'Seq2Seq_RNN_Batch_Drop':
            return self.run_case_mdl(forecast.Seq2Seq_RNN_Batch_Drop_class)
        if self.name_mdl == 'Seq2Seq_BiRNN':
            return self.run_case_mdl(forecast.Seq2Seq_BiRNN_class)
        if self.name_mdl == 'Seq2Seq_BiLSTM2':
            return self.run_case_mdl(forecast.Seq2Seq_BiRNN2_class)
        if self.name_mdl == 'Seq2Seq_Conv1D_BiRNN':
            return self.run_case_mdl(forecast.Seq2Seq_Conv1D_BiRNN_class)
        if self.name_mdl == 'Seq2Seq_Multi_Head_Conv1D_BiRNN':
            return self.run_case_mdl(forecast.Seq2Seq_Multi_Head_Conv1D_BiRNN_class)
        if self.name_mdl == 'Seq2Seq_RNN_with_Luong_Attention':
            return self.run_case_mdl(forecast.Seq2Seq_RNN_with_Luong_Attention_class)
        if self.name_mdl == 'Seq2Seq_BiRNN_with_Attention':
            return self.run_case_mdl(forecast.Seq2Seq_BiRNN_with_Attention_class)
        if self.name_mdl == 'Seq2Seq_Conv2D_RNN':
            return self.run_case_mdl(forecast.Seq2Seq_Conv2D_RNN_class)
    '''