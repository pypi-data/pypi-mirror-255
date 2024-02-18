# -*- coding: utf-8 -*-
# @Time    : 27/04/2023
# @Author  : Ing. Jorge Lara
# @Email   : jlara@iee.unsj.edu.ar
# @File    : ------------
# @Software: PyCharm

import tensorflow as tf
#from tf.keras.architectures import Model
#from tensorflow.keras.architectures import Model
#from tensorflow.keras.layers import Dense, Input, Flatten, Conv2D, MaxPool2D, LSTM, Bidirectional

# your config
config = {
    'learning_rate': 0.001,
    'lstm_neurons': 32,
    'lstm_activation': 'tanh',
    'dropout_rate': 0.08,
    'batch_size': 128,
    'dense_layers': [
        {'neurons': 32, 'activation': 'relu'},
        {'neurons': 32, 'activation': 'relu'},
    ]
}


# Subclassed API Model
class MySubClassed(tf.keras.Model):
    def __init__(self, output_size):
        super(MySubClassed, self).__init__()
        self.lstm = tf.keras.layers.LSTM(config['lstm_neurons'], activation=config['lstm_activation'])
        self.bn = tf.keras.layers.BatchNormalization()
        if 'dropout_rate' in config:
            self.dp1 = tf.keras.layers.Dropout(config['dropout_rate'])
            self.dp2 = tf.keras.layers.Dropout(config['dropout_rate'])
            self.dp3 = tf.keras.layers.Dropout(config['dropout_rate'])
        for layer in config['dense_layers']:
            self.dense1 = tf.keras.layers.Dense(layer['neurons'], activation=layer['activation'])
            self.bn1 = tf.keras.layers.BatchNormalization()
            self.dense2 = tf.keras.layers.Dense(layer['neurons'], activation=layer['activation'])
            self.bn2 = tf.keras.layers.BatchNormalization()
        self.out = tf.keras.layers.Dense(output_size, activation='sigmoid')

    def call(self, inputs, training=True, **kwargs):
        x = self.lstm(inputs)
        x = self.bn(x)

        if 'dropout_rate' in config:
            x = self.dp1(x)

        x = self.dense1(x)
        x = self.bn1(x)
        if 'dropout_rate' in config:
            x = self.dp2(x)

        x = self.dense2(x)
        x = self.bn2(x)
        if 'dropout_rate' in config:
            x = self.dp3(x)

        return self.out(x)

    # A convenient way to get model summary
    # and plot in subclassed api
    def build_graph(self, raw_shape):
        x = tf.keras.layers.Input(shape=(None, raw_shape), ragged=True)
        return tf.keras.Model(inputs=[x], outputs=self.call(x))

s = MySubClassed(output_size=1)
s.compile(
    loss='mse',
    metrics=['mse'],
    optimizer=tf.keras.optimizers.Adam(learning_rate=0.001)
)

raw_input = (16, 16, 16)
y = s(tf.ones(shape=(raw_input)))

print("weights:", len(s.weights))
print("trainable weights:", len(s.trainable_weights))

s.build_graph(16).summary()
tf.keras.utils.plot_model(
    s.build_graph(16),
    show_shapes=True,
    show_dtype=True,
    show_layer_names=True,
    rankdir="TB",
)


class LeNet5(tf.keras.Model):
    def __init__(self):
        super(LeNet5, self).__init__()
        #creating layers in initializer
        self.conv1 = tf.keras.layers.Conv2D(filters=6, kernel_size=(5, 5), padding="same", activation="relu")
        self.max_pool2x2 = tf.keras.layers.MaxPool2D(pool_size=(2, 2))
        self.conv2 = tf.keras.layers.Conv2D(filters=16, kernel_size=(5, 5), padding="same", activation="relu")
        self.conv3 = tf.keras.layers.Conv2D(filters=120, kernel_size=(5, 5), padding="same", activation="relu")
        self.flatten = tf.keras.layers.Flatten()
        self.fc2 = tf.keras.layers.Dense(units=84, activation="relu")
        self.fc3 = tf.keras.layers.Dense(units=10, activation="softmax")

    def call(self, input_tensor):
        #don't add layers here, need to create the layers in initializer, otherwise you will get the tf.Variable can only be created once error
        x = self.conv1(input_tensor)
        x = self.max_pool2x2(x)
        x = self.conv2(x)
        x = self.max_pool2x2(x)
        x = self.conv3(x)
        x = self.flatten(x)
        x = self.fc2(x)
        x = self.fc3(x)
        return x

input_layer = tf.keras.layers.Input(shape=(32,32,3,))
x = LeNet5()(input_layer)

model = tf.keras.Model(inputs=input_layer, outputs=x)
print(model.summary(expand_nested=True))

class LSTM_model(tf.keras.Model):

    def __init__(self, units: int = 50, activation: str ="tanh"):
        super(LSTM_model, self).__init__()
        self.lstm1 = tf.keras.layers.LSTM(
            units=units,
            activation=activation
        )

    def call(self, inputs):
        x = self.lstm1(inputs)
        return tf.keras.Model(inputs=[x], outputs=self.call(x))


class Conv1D_Dense_class(tf.keras.Model):

    def __init__(self,):
        super(Conv1D_Dense, self).__init__()
        self.conv1d = tf.keras.layers.Conv1D(filters=64, kernel_size=2, activation='relu')
        self.maxpool1d = tf.keras.layers.MaxPooling1D(pool_size=2)
        self.flatten = tf.keras.layers.Flatten()
        self.dense1b = tf.keras.layers.Dense(units=50, activation="relu")



def Conv1D_Dense(n_steps_in, n_features, n_output):

    model = tf.keras.Sequential()
    model.add(tf.keras.layers.Conv1D(filters=64, kernel_size=2, activation='relu', input_shape=(n_steps_in, n_features)))
    model.add(tf.keras.layers.MaxPooling1D(pool_size=2))
    model.add(tf.keras.layers.Flatten())
    model.add(tf.keras.layers.Dense(50, activation='relu'))
    model.add(tf.keras.layers.Dense(n_output))
    model.add(tf.keras.layers.Reshape())
    return model

# multivariate output multi-step 1d cnn example
from numpy import array
from numpy import hstack
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Flatten
from keras.layers.convolutional import Conv1D
from keras.layers.convolutional import MaxPooling1D

def split_sequences(sequences, n_steps_in, n_steps_out):
    X, y = list(), list()
    for i in range(len(sequences)):
        # find the end of this pattern
        end_ix = i + n_steps_in
        out_end_ix = end_ix + n_steps_out
        # check if we are beyond the dataset
        if out_end_ix > len(sequences):
            break
        # gather input and output parts of the pattern
        seq_x, seq_y = sequences[i:end_ix, :], sequences[end_ix:out_end_ix, :]
        X.append(seq_x)
        y.append(seq_y)
    return array(X), array(y)

# define input sequence
in_seq1 = array([10, 20, 30, 40, 50, 60, 70, 80, 90])
in_seq2 = array([15, 25, 35, 45, 55, 65, 75, 85, 95])
out_seq = array([in_seq1[i]+in_seq2[i] for i in range(len(in_seq1))])
# convert to [rows, columns] structure
in_seq1 = in_seq1.reshape((len(in_seq1), 1))
in_seq2 = in_seq2.reshape((len(in_seq2), 1))
out_seq = out_seq.reshape((len(out_seq), 1))
# horizontally stack columns
dataset = hstack((in_seq1, in_seq2, out_seq))
# choose a number of time steps
n_steps_in, n_steps_out = 3, 2
# convert into input/output
X, y = split_sequences(dataset, n_steps_in, n_steps_out)
print(X.shape, y.shape)

# flatten output
n_output = y.shape[1] * y.shape[2]
y = y.reshape((y.shape[0], n_output))
# the dataset knows the number of features, e.g. 2
n_features = X.shape[2]
# define model


model = Conv1D_Dense(n_steps_in, n_features, n_output)

model.compile(optimizer='adam', loss='mse')
# fit model
model.fit(X, y, epochs=7000, verbose=0)
# demonstrate prediction
x_input = array([[60, 65, 125], [70, 75, 145], [80, 85, 165]])
print(f'x_input:\n{x_input}')
x_input = x_input.reshape((1, n_steps_in, n_features))
yhat = model.predict(x_input, verbose=0)
print(f'yhat:\n{yhat}')