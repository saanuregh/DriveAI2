import tensorflow as tf

tf.enable_eager_execution()

filenames = ["training_data/tfrecord/train-00000-of-00001"]
raw_dataset = tf.data.TFRecordDataset(filenames)

feature_description = {
    'image/speed': tf.VarLenFeature(tf.float32),
    'image/label': tf.VarLenFeature(tf.float32),
    'image/encoded': tf.FixedLenFeature([], tf.string),
}


def _parse_function(example_proto):
    # Parse the input tf.Example proto using the dictionary above.
    return tf.parse_single_example(example_proto, feature_description)


parsed_image_dataset = raw_dataset.map(_parse_function)

for image_features in parsed_image_dataset:
    speed = tf.reshape(tf.sparse_tensor_to_dense(
        image_features['image/speed']), [1])
    label = tf.reshape(tf.sparse_tensor_to_dense(
        image_features['image/label']), [3])
    image = tf.image.decode_jpeg(image_features['image/encoded'], channels=3)
    print(image.shape, speed, label)
