import tensorflow_datasets as tfds
from tensorflow.keras.losses import SparseCategoricalCrossentropy
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, ReLU, Dropout
from tensorflow.keras import Input
from tensorflow.keras.datasets import mnist
from tensorflow.keras import layers, regularizers
from tensorflow import keras
from tensorboard.plugins.hparams import api as hp
import numpy as np
import matplotlib.pyplot as plt
from utils import style
import tensorflow as tf
import io
import os
import datetime
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # change to 2

os.system('clear')
print(style.YELLOW + f'Tensorflow  version: {tf.__version__}\n')
print(style.GREEN, end='')

class_names = ['Airplane', 'Automobile', 'Bird', 'Cat',
               'Deer', 'Dog', 'Frog', 'Horse', 'Ship', 'Truck']

(ds_train, ds_test), ds_info = tfds.load(
    'cifar10',
    split=['train', 'test'],
    shuffle_files=True,
    as_supervised=True,
    with_info=True,
)


def normalize_img(image, label):
    return tf.cast(image, tf.float32)/255.0, label


def augment(image, label):

    # convert 10% of images to greyscale
    percent_to_convert = 0.1  # 10%
    if tf.random.uniform((), minval=0, maxval=1) < percent_to_convert:
        image = tf.image.rgb_to_grayscale(image)

        # since grayscale has 1 channel, and input expects 3, we can duplicate
        image = tf.tile(image, [1, 1, 3])

    # Add random brightness
    image = tf.image.random_brightness(image, max_delta=0.1)

    #  flip left to right
    image = tf.image.random_flip_left_right(image)

    return image, label


AUTOTUNE = tf.data.experimental.AUTOTUNE
BATCH_SIZE = 32

# Setting up training dataset
ds_train = ds_train.map(normalize_img, num_parallel_calls=AUTOTUNE)
ds_train = ds_train.cache()
ds_train = ds_train.shuffle(ds_info.splits['train'].num_examples)
ds_train = ds_train.map(augment)
ds_train = ds_train.batch(BATCH_SIZE)
ds_train = ds_train.prefetch(AUTOTUNE)

# Setting up test dataset
ds_test = ds_train.map(normalize_img, num_parallel_calls=AUTOTUNE)
ds_test = ds_train.batch(BATCH_SIZE)
ds_test = ds_train.prefetch(AUTOTUNE)

class_names = ['Airplane', 'Automobile', 'Bird', 'Cat',
               'Deer', 'Dog', 'Frog', 'Horse', 'Ship', 'Truck']


def train_model_one_epoch(hparams):
    units = hparams[HP_NUM_UNITS]
    drop_rate = hparams[HP_DROPOUT]
    learning_rate = hparams[HP_LR]

    optimizer = Adam(learning_rate=learning_rate)

    model = keras.Sequential(
        [
            Input((32, 32, 3)),
            Conv2D(8, 3, padding='same', activation='relu'),
            Conv2D(16, 3, padding='same', activation='relu'),
            MaxPooling2D((2, 2)),
            Flatten(),
            Dense(units, activation='relu'),
            Dropout(drop_rate),
            Dense(10),
        ]
    )
    for batch_idx, (x, y) in enumerate(ds_train):
        with tf.GradientTape() as tape:
            y_pred = model(x, training=True)
            loss = loss_fn(y, y_pred)

        gradients = tape.gradient(loss, model.trainable_weights)
        optimizer.apply_gradients(zip(gradients, model.trainable_weights))
        acc_metric.update_state(y, y_pred)

    # writing to TB

    run_dir = f'logs/{datetime.now().strftime("%Y%m%d-%H%M%S")}/units_{units}_dropout_{drop_rate}_lr_{learning_rate}'

    with tf.summary.create_file_writer(run_dir).as_default():
        hp.hparams(hparams)
        accuracy = acc_metric.result()
        tf.summary.scalar('accuracy', accuracy, step=1)

    acc_metric.reset_states()


print(style.GREEN, end='')

loss_fn = keras.losses.SparseCategoricalCrossentropy(from_logits=True)
acc_metric = keras.metrics.SparseCategoricalAccuracy()

HP_NUM_UNITS = hp.HParam('num units', hp.Discrete([32, 64, 128]))
HP_DROPOUT = hp.HParam('dropout', hp.Discrete([0.1, 0.2, 0.3, 0.4, 0.5]))
HP_LR = hp.HParam('learning_rate', hp.Discrete([1e-3, 1e-4, 1e-5]))

for lr in HP_LR.domain.values:
    for units in HP_NUM_UNITS.domain.values:
        for rate in HP_DROPOUT.domain.values:
            hparams = {
                HP_LR: lr,
                HP_DROPOUT: rate,
                HP_NUM_UNITS: units,
            }
            print(f'Running epoch: units: {units}, Dropout: {rate}, LR: {lr}')
            train_model_one_epoch(hparams)
