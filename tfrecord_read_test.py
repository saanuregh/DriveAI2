import tensorflow as tf

tf.enable_eager_execution()

path = "training_data/tfrecord/"

train_filenames = tf.data.Dataset.list_files(path +
                                             "train-*.tfrecord")
try:
    validation_filenames = tf.data.Dataset.list_files(
        path + "validation-*.tfrecord")
except:
    validation_filenames = None

feature_description = {
    'image/speed': tf.VarLenFeature(tf.float32),
    'image/label': tf.VarLenFeature(tf.float32),
    'image/encoded': tf.FixedLenFeature([], tf.string),
}


def _parse_function(example_proto):
    return tf.parse_single_example(example_proto, feature_description)


def assert_fn(filenames):
    count = 0
    raw_dataset = tf.data.TFRecordDataset(filenames)
    parsed_dataset = raw_dataset.map(_parse_function)
    for features in parsed_dataset:
        speed = tf.reshape(tf.sparse_tensor_to_dense(
            features['image/speed']), [1])
        label = tf.reshape(tf.sparse_tensor_to_dense(
            features['image/label']), [3])
        image = tf.image.decode_jpeg(features['image/encoded'], channels=3)
        assert image.shape == (300, 400, 3)
        assert speed.shape == (1,)
        assert label.shape == (3,)
        count += 1
    return count


print(f"Found {assert_fn(train_filenames)} training samples")
if validation_filenames:
    print(f"Found {assert_fn(validation_filenames)} validation samples")
