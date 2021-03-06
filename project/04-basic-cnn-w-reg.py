import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # change to 2

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, regularizers
from tensorflow.keras.datasets import cifar10

class style():
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    UNDERLINE = '\033[4m'
    RESET = '\033[0m'

os.system('clear')

print(style.YELLOW + f'Tensorflow  version: {tf.__version__}\n')

(x_train, y_train), (x_test, y_test) = cifar10.load_data()

x_train = x_train.astype("float32")
x_train = x_train / 255

x_test = x_test.astype("float32")
x_test = x_test / 255

# image_shape = x_train.shape[1:]
# inputs = keras.Input(shape=image_shape)
# x = layers.Conv2D(32, 3, padding='valid', activation='relu')(inputs)
# x = layers.MaxPool2D(pool_size=(2,2))(x)
# x = layers.Conv2D(64, 3, activation='relu')(x)
# x = layers.MaxPool2D()(x)
# x = layers.Conv2D(128, 3, activation='relu')(x)
# x = layers.Flatten()(x)
# x = layers.Dense(64, activation='relu')(x)
# outputs = layers.Dense(10)(x)
# model = keras.Model(inputs=inputs, outputs=outputs)  # to build the whole n/w

# print(model.summary())

print(style.GREEN)

def my_model():
    inputs = keras.Input(shape=(32,32,3))

    x = layers.Conv2D(
        32, 3, 
        padding='same', 
        kernel_regularizer=regularizers.l2(0.01)
        )(inputs)
    x = layers.BatchNormalization()(x)
    x = keras.activations.relu(x) # Since we wanted to do Batch Norm before relu
    x = layers.MaxPool2D()(x)

    x = layers.Conv2D(64, 5, 
        padding='same',
        kernel_regularizer=regularizers.l2(0.01)
        )(x)
    x = layers.BatchNormalization()(x)
    x = keras.activations.relu(x)

    x = layers.Conv2D(128, 3, 
        padding='same', 
        kernel_regularizer=regularizers.l2(0.01)
    )(x)
    x = layers.BatchNormalization()(x)
    x = keras.activations.relu(x)

    x = layers.Flatten()(x)
    x = layers.Dense(64, 
        activation='relu', 
        kernel_regularizer=regularizers.l2(0.01), 
        name='dense_64'
        )(x)

    x = layers.Dropout(0.5)(x)

    outputs = layers.Dense(10, name='dense_10')(x)

    model = keras.Model(inputs = inputs, outputs = outputs)

    return model

model = my_model()

model.compile(
    loss=keras.losses.SparseCategoricalCrossentropy(from_logits=True), 
    optimizer = keras.optimizers.Adam(learning_rate=3e-4),
    metrics=['accuracy']
)

model.fit(x_train[:10000], y_train[:10000], batch_size=64, epochs=1, )
model.evaluate(x_test[:10000], y_test[:10000], batch_size=64, )

model.save('models/pretrained-cnn/')
