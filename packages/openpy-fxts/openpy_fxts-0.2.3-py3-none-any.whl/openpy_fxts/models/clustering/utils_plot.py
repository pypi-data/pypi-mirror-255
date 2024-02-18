# -*- coding: utf-8 -*-
# @Time    : 04/09/2023
# @Author  : Ing. Jorge Lara
# @Email   : jlara@iee.unsj.edu.ar
# @File    : utils_plot.py
# @Software: PyCharm

import seaborn as sns
import matplotlib.pyplot as plt


class plot_scenarios:
    
    def __init__(self, data):
        self.data = data

    def lineplot_SingleUser(self):
        self.data = self.data.reset_index()
        self.data[self.data.columns[0]] = self.data[self.data.columns[0]].apply(lambda x: x.strftime('%H:%M'))
        self.data.set_index(self.data.columns[0], inplace=True)
        g = sns.lineplot(x=self.data.index, y=self.data.columns[0], hue='date', data=self.data)
        g.set_xticklabels(g.get_xticklabels(), rotation=90)
        plt.show()

    def boxplot_SingleUser(self):
        self.data = self.data.reset_index()
        self.data[self.data.columns[0]] = self.data[self.data.columns[0]].apply(lambda x: x.strftime('%H:%M'))
        self.data.set_index(self.data.columns[0], inplace=True)
        g = sns.boxplot(x=self.data.index, y=self.data.columns[0], data=self.data)
        g.set_xticklabels(g.get_xticklabels(), rotation=90)
        plt.show()
