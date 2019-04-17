import os

import tensorflow as tf

from model import model_fn

# * Resolution of capture
height = 300
width = 400

# * Training Parameters
on_colab = True
sample_count = 10000
num_parallel_calls = 4
batch_size = 1000
val_batch_size = 1000
epochs = 10
learning_rate = 1e-3
data_dir = ""
save_dir = ""
log_dir = ""
steps_per_epoch = sample_count // batch_size


def parse_fn(example):
    example_fmt = {
        'image/speed': tf.VarLenFeature(tf.float32),
        'image/label': tf.VarLenFeature(tf.float32),
        'image/encoded': tf.FixedLenFeature([], tf.string),
    }
    parsed = tf.parse_single_example(example, example_fmt)
    image_buffer = parsed['image/encoded']
    speed = tf.reshape(tf.sparse_tensor_to_dense(parsed['image/speed']), [1])
    label = tf.reshape(tf.sparse_tensor_to_dense(parsed['image/label']), [3])
    with tf.name_scope('decode_jpeg', [image_buffer], None):
        image = tf.image.decode_jpeg(image_buffer, channels=3)
        image = tf.image.convert_image_dtype(image, dtype=tf.float32)
        image = tf.image.per_image_standardization(image)
    image = tf.reshape(image, [height * width * 3])
    features = tf.concat([speed, image], axis=0)
    return features, label


def training_input_fn():
    files = tf.data.Dataset.list_files(
        os.path.join(data_dir, "train-*.tfrecord"))
    dataset = files.interleave(tf.data.TFRecordDataset)
    dataset = dataset.map(
        map_func=parse_fn, num_parallel_calls=num_parallel_calls)
    dataset = dataset.shuffle(buffer_size=5000)
    dataset = dataset.repeat()
    dataset = dataset.batch(batch_size=batch_size)
    dataset = dataset.prefetch(buffer_size=-1)
    return dataset


def validation_input_fn():
    files = tf.data.Dataset.list_files(
        os.path.join(data_dir, "validation-*.tfrecord"))
    dataset = files.interleave(tf.data.TFRecordDataset)
    dataset = dataset.map(
        map_func=parse_fn, num_parallel_calls=num_parallel_calls)
    dataset = dataset.repeat()
    dataset = dataset.batch(batch_size=val_batch_size)
    return dataset


def train():
    config = tf.ConfigProto()
    config.gpu_options.allow_growth = True
    config.log_device_placement = True
    sess = tf.Session(config=config)
    tf.keras.backend.set_session(sess)
    model = model_fn((height, width, 3), learning_rate)
    model.fit(training_input_fn, steps_per_epoch=steps_per_epoch, epochs=epochs,
              validation_data=validation_input_fn, validation_steps=1,
              callbacks=[tf.keras.callbacks.TensorBoard(log_dir=log_dir)])
