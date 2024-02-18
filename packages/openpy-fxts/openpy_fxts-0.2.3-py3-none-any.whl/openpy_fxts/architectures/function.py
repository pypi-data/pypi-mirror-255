# -*- coding: utf-8 -*-
# @Time    : 29/05/2023
# @Author  : Ing. Jorge Lara
# @Email   : jlara@iee.unsj.edu.ar
# @File    : ------------
# @Software: PyCharm


import tensorflow as tf

tkc = tf.keras.callbacks
tku = tf.keras.utils


def learning_curve(history):
    import matplotlib.pyplot as plt

    plt.style.use('seaborn-dark-palette')
    plt.figure(figsize=(17, 7))
    plt.plot(history.history["loss"], label="training")
    plt.plot(history.history["val_loss"], label="validation")
    plt.xlabel("Epoch")
    plt.ylabel("Loss -Mean Squared Error")
    plt.legend()
    plt.show()


def callbacks(source, folder, name_model):
    import datetime

    callbacks_list = []

    log_dir = "logs\\" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    tensorboard_callback = tkc.TensorBoard(log_dir=log_dir, histogram_freq=1)
    callbacks_list.append(tensorboard_callback)
    # w_fn = '.\\architectures\\electricity_prediction-1-{}.h5'.format(datetime.datetime.now().strftime("%Y%m%d-%H%M%S"))

    early_stopping = tkc.EarlyStopping(
        monitor='val_loss',
        patience=5,
        verbose=1,
        mode='auto'
    )
    callbacks_list.append(early_stopping)
    # Change the cooldown to 1, if behances unexpectedly
    learning_rate_reduction = tkc.ReduceLROnPlateau(
        monitor='val_loss',
        patience=5,
        verbose=1,
        factor=0.2,
        min_lr=2.5e-5,
        cooldown=0
    )
    callbacks_list.append(learning_rate_reduction)
    file_path = source + '/' + folder + '/' + f"{name_model}" + "/weights-{epoch:02d}.hdf5"
    checkpoint_cb = tkc.ModelCheckpoint(
        filepath=file_path,
        monitor='val_loss',
        verbose=1,
        save_best_only=True,
        save_weights_only=True,
        mode='auto'
    )
    callbacks_list.append(checkpoint_cb)
    return callbacks_list
