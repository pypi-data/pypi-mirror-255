# -*- coding: utf-8 -*-
# @Time    : 06/07/2023
# @Author  : Ing. Jorge Lara
# @Email   : jlara@iee.unsj.edu.ar
# @File    : ------------
# @Software: PyCharm

import os
import numpy as np
import tensorflow as tf
import random as python_random

tkm = tf.keras.models
tkl = tf.keras.layers
tkloss = tf.keras.losses
tko = tf.keras.optimizers
tku = tf.keras.utils
K = tf.keras.backend
tkr = tf.keras.regularizers
tfk = tf.keras
tkc = tf.keras.callbacks
tkmtc = tf.keras.metrics

value_miss = 0
seed_lab = 44


seed_value = 1200
os.environ["PYTHONHASHSEED"] = str(seed_value)


def reset_seeds(seed_value):
    np.random.seed(seed_value)
    python_random.seed(seed_value)
    tf.random.set_seed(seed_value)
    tf.keras.utils.set_random_seed(seed_value)
