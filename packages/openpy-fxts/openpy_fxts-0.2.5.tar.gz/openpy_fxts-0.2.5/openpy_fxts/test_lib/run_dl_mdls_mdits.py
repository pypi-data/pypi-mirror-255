# -*- coding: utf-8 -*-
# @Time    : 10/07/2023
# @Author  : Ing. Jorge Lara
# @Email   : jlara@iee.unsj.edu.ar
# @File    : ------------
# @Software: PyCharm
import pandas as pd
import os
import pathlib
import openpy_fxts.models.imputation as its


def _convert_to_df(yhat, config_data, n_past):
    df_mask = pd.DataFrame(
        yhat.reshape(yhat.shape[0], yhat.shape[2]),
        index=config_data['dataset_orig'].iloc[n_past:].index,
        columns=config_data['y_colname']
    )
    df_miss = config_data['dataset_orig'][config_data['y_colname']]
    for i in df_miss.columns:
        df_miss[i][df_miss[i].isnull()] = df_mask[i].loc[df_miss[i].isnull()]
    df_miss.fillna(method="ffill")
    return df_miss


class run_all_models:

    def __init__(
            self,
            config_data_train: dict = None,
            config_data_test: dict = None,
            config_mdl: dict = None,
            config_sim: dict = None,
            config_arch: dict = None,
            source: str = None,
            type_mdl: str = None,
            name_mdl: str = None,
            train: int = None,
            test: int = None,
            folder: str = 'models_fxts',
            type_NaN: str = None,
            percentage: float = None,
            results: dict = None,
            view: bool = False
    ):
        self.config_data_train = config_data_train
        self.config_data_test = config_data_test
        self.config_mdl = config_mdl
        self.config_sim = config_sim
        self.config_arch = config_arch
        self.source = source
        self.type_mdl = type_mdl
        self.name_mdl = name_mdl
        self.train = train
        self.test = test
        self.folder = folder
        self.type_NaN = type_NaN
        self.percentage = percentage
        self.results = results
        self.view = view

    def exec_train(self, object_class):
        mdl = object_class(self.config_data_train, self.config_mdl, self.config_sim)
        print(mdl.name_mdl)
        path = pathlib.Path(self.source).joinpath(
            self.folder, self.type_NaN, f'pct_{self.percentage}', mdl.type_mdl, mdl.name_mdl
        )
        return mdl.training_mdl(path)

    def exec_test(self, object_class):
        mdl = object_class(self.config_data_test, self.config_mdl, self.config_sim)
        print(mdl.name_mdl)
        path = pathlib.Path(self.source).joinpath(
            self.folder, self.type_NaN, f'pct_{self.percentage}', mdl.type_mdl, mdl.name_mdl
        )
        new_model = mdl._build_mdl()
        list_files = [x for x in os.listdir(path) if 'weights' in x]
        '''
        aux_list = []
        characters = "weights-.hdf5"
        for file in list_files:
            for x in range(len(characters)):
                file = file.replace(characters[x], "")
            aux_list.append(file)
        '''
        print(f'Best Model => {list_files[-1]}')
        new_model.load_weights(str(path) + f'/{list_files[-1]}')
        yhat = mdl.prediction_mdl(new_model, path)
        self.results[mdl.name_mdl] = _convert_to_df(
            yhat,
            self.config_data_test,
            self.config_data_test['n_past']
        )
        if self.view:
            its.view.density_true_missing(
                self.config_data_test['dataset'][self.config_data_test['y_colname']],
                self.results,
                view=True,
                cumulative=False
            )
        return self.results

    def run_case_mdl(self, object_class):
        if self.train == 1 and self.test == 1:
            self.exec_train(object_class)
            return self.exec_test(object_class)
        if self.train == 1 and self.test == 0:
            return self.exec_train(object_class)
        if self.train == 0 and self.test == 1:
            return self.exec_test(object_class)

    def execute_case(self):
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

        if self.type_mdl == 'LSTM':
            return self._lstm()
        if self.type_mdl == 'BiLSTM':
            return self._bilstm()
        if self.type_mdl == 'GRU':
            return self._gru()
        if self.type_mdl == 'Stacked':
            return self._stacked()
        if self.type_mdl == 'Seq2Seq':
            return self._seq2seq()
        else:
            return None

    def _mlp(self):
        if self.name_mdl == 'MLP_Dense':
            return self.run_case_mdl(its.MLP_Dense_class)

    def _birnn(self):
        # Simple models_fxts
        if self.name_mdl == 'BiRNN_Dense':
            return self.run_case_mdl(its.BiRNN_Dense_class)
        if self.name_mdl == 'Multi_BiRNN_Dense':
            return self.run_case_mdl(its.Multi_BiRNN_Dense_class)
        # Hybrids models_fxts
        if self.name_mdl == 'BiRNN_Conv1D':
            return self.run_case_mdl(its.BiRNN_Conv1D_class)
        if self.name_mdl == 'BiRNN_TimeDist_Dense':
            return self.run_case_mdl(its.BiRNN_TimeDist_Dense_class)
        if self.name_mdl == 'BiRNN_Bahdanau_Attention_Conv1D':
            return self.run_case_mdl(its.BiRNN_Bahdanau_Attention_Conv1D_class)
        if self.name_mdl == 'BiRNN_Luong_Attention_Conv1D':
            return self.run_case_mdl(its.BiRNN_Luong_Attention_Conv1D_class)
        if self.name_mdl == 'BiRNN_MultiHeadAttention_Conv1D':
            return self.run_case_mdl(its.BiRNN_MultiHeadAttention_Conv1D_class)
        if self.name_mdl == 'BiRNN_MDN':
            pass
            #return self.run_case_mdl(fxts.BiRNN_MDN)

    def _encdec(self):
        if self.name_mdl == 'EncDec_BiRNN':
            return self.run_case_mdl(its.EncDec_BiRNN_class)
        if self.name_mdl == 'EncDec_Conv1D_BiRNN':
            return self.run_case_mdl(its.EncDec_Conv1D_BiRNN_class)

    def _lstm(self):
        if self.name_mdl == 'LSTM2_Dense':
            return self.run_case_mdl(its.LSTM2_Dense_class)

    def _bilstm(self):
        if self.name_mdl == 'BiLSTM_Dense':
            return self.run_case_mdl(its.BiLSTM_Dense_class)
        if self.name_mdl == 'BiLSTM_Conv1D':
            return self.run_case_mdl(its.BiLSTM_Conv1D_class)
        if self.name_mdl == 'BiLSTM_Bahdanau_Attention_Conv1D':
            return self.run_case_mdl(its.BiLSTM_Bahdanau_Attention_Conv1D_class)
        if self.name_mdl == 'BiLSTM_MultiHeadAttention_Conv1D':
            return self.run_case_mdl(its.BiLSTM_MultiHeadAttention_Conv1D_class)
        if self.name_mdl == 'BiLSTM_Luong_Attention_Conv1D':
            return self.run_case_mdl(its.BiLSTM_Luong_Attention_Conv1D_class)
        if self.name_mdl == 'BiLSTM_MDN':
            return self.run_case_mdl(its.BiLSTM_MDN)  #Review

    def _conv1d(self):
        # Simple
        if self.name_mdl == 'Conv1D_Dense':
            return self.run_case_mdl(its.Conv1D_Dense_class)
        if self.name_mdl == 'Multi_Conv1D_Dense':
            return self.run_case_mdl(its.Multi_Conv1D_Dense_class)
        # Hybrids
        if self.name_mdl == 'Conv1D_BiRNN':
            return self.run_case_mdl(its.Conv1D_BiRNN_class)
        if self.name_mdl == 'TimeDist_Conv1D_BiRNN':
            return self.run_case_mdl(its.TimeDist_Conv1D_BiRNN_class)
        if self.name_mdl == 'Conv1D_BiRNN_Attention':
            return self.run_case_mdl(its.Conv1D_BiRNN_Attention_class)

    def _gru(self):
        if self.name_mdl == 'GRU2_Dense':
            return self.run_case_mdl(its.GRU_Dense_class)

    def _others(self):
        if self.name_mdl == 'TCN_BiRNN':
            return self.run_case_mdl(its.TCN_BiRNN_class)
        if self.name_mdl == 'Time2Vec_BiRNN':
            return self.run_case_mdl(its.Time2Vec_BiRNN_class)

    def _stacked(self):
        if self.name_mdl == 'LSTM_Stacked':
            return self.run_case_mdl(its.LSTM_Stacked)
        if self.name_mdl == 'BiLSTM_Stacked':
            return self.run_case_mdl(its.BiLSTM_Stacked)
        if self.name_mdl == 'Stacked_SciNet':
            return self.run_case_mdl(its.Stacked_SciNet)

    def _seq2seq(self):
        if self.name_mdl == 'Seq2Seq_LSTM':
            return self.run_case_mdl(its.Seq2Seq_LSTM_class)
        if self.name_mdl == 'Seq2Seq_LSTM2':
            return self.run_case_mdl(its.Seq2Seq_LSTM2_class)
        if self.name_mdl == 'Seq2Seq_LSTM_Batch_Drop':
            return self.run_case_mdl(its.Seq2Seq_LSTM_Batch_Drop_class)
        if self.name_mdl == 'Seq2Seq_BiLSTM':
            return self.run_case_mdl(its.Seq2Seq_BiLSTM_class)
        if self.name_mdl == 'Seq2Seq_BiLSTM2':
            return self.run_case_mdl(its.Seq2Seq_BiLSTM2_class)
        if self.name_mdl == 'Seq2Seq_Conv1D_BiLSTM':
            return self.run_case_mdl(its.Seq2Seq_Conv1D_BiLSTM_class)
        if self.name_mdl == 'Seq2Seq_Multi_Head_Conv1D_BiLSTM':
            return self.run_case_mdl(its.Seq2Seq_Multi_Head_Conv1D_BiLSTM_class)
        if self.name_mdl == 'Seq2Seq_LSTM_with_Luong_Attention':
            return self.run_case_mdl(its.Seq2Seq_LSTM_with_Luong_Attention_class)
        if self.name_mdl == 'Seq2Seq_BiLSTM_with_Attention':
            return self.run_case_mdl(its.Seq2Seq_BiLSTM_with_Attention_class)
        if self.name_mdl == 'Seq2Seq_Conv2D_LSTM':
            return self.run_case_mdl(its.Seq2Seq_Conv2D_LSTM_class)
