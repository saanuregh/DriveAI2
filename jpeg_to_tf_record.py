# Copyright 2018 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
r"""Beam pipeline to create TFRecord files from JPEG files stored on GCS.

These are the TFRecord format expected by  the resnet and amoebanet models.
Example usage:
python -m jpeg_to_tf_record.py \
       --train_csv gs://cloud-ml-data/img/flower_photos/train_set.csv \
       --validation_csv gs://cloud-ml-data/img/flower_photos/eval_set.csv \
       --labels_file /tmp/labels.txt \
       --project_id $PROJECT \
       --output_dir gs://${BUCKET}/tpu/imgclass/data

The format of the CSV files is:
    URL-of-image,label
And the format of the labels_file is simply a list of strings one-per-line.
"""

from __future__ import print_function

import argparse
import datetime
import os
import shutil
import subprocess

import apache_beam as beam
import tensorflow as tf


def _int64_feature(value):
    """Wrapper for inserting int64 features into Example proto."""
    if not isinstance(value, list):
        value = [value]
    return tf.train.Feature(int64_list=tf.train.Int64List(value=value))


def _float_feature(value):
    """Wrapper for inserting float32 features into Example proto."""
    if not isinstance(value, list):
        value = [value]
    return tf.train.Feature(float_list=tf.train.FloatList(value=value))


def _bytes_feature(value):
    """Wrapper for inserting bytes features into Example proto."""
    return tf.train.Feature(bytes_list=tf.train.BytesList(value=[value]))


def _convert_to_example(image_buffer, speed, label):
    """Build an Example proto for an example.

    Args:
      image_buffer: string, JPEG encoding of RGB image
      speed:
      label:
    Returns:
      Example proto
    """

    example = tf.train.Example(
        features=tf.train.Features(
            feature={
                'image/speed': _float_feature(speed),
                'image/label': _float_feature(label),
                'image/encoded': _bytes_feature(image_buffer)
            }))
    return example


def _get_image_data(filename):
    """Process a single image file.

    Args:
      filename: string, path to an image file e.g., '/path/to/example.JPG'.
    Returns:
      image_buffer: string, JPEG encoding of RGB image.
    """
    # Read the image file.
    with tf.gfile.GFile(filename, 'rb') as ifp:
        image_data = ifp.read()
    return image_data


def convert_to_example(csvline):
    """Parse a line of CSV file and convert to TF Record.

    Args:
      csvline: line from input CSV file
    Yields:
      serialized TF example if the label is in categories
    """
    # steering_angle, throttle, brake, speed, filename = csvline.encode('ascii', 'ignore').split(',')
    steering_angle, throttle, brake, speed, filename = csvline.split(',')
    label = [float(steering_angle), float(throttle), float(brake)]
    image_buffer = _get_image_data(filename)
    example = _convert_to_example(image_buffer, float(speed), label)
    yield example.SerializeToString()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--train_csv',
        # pylint: disable=line-too-long
        help='Path to input.  Each line of input has two fields  image-file-name and label separated by a comma',
        required=True)
    # parser.add_argument(
    #     '--validation_csv',
    #     # pylint: disable=line-too-long
    #     help='Path to input.  Each line of input has two fields  image-file-name and label separated by a comma',
    #     required=True)
    parser.add_argument(
        '--project_id',
        help='ID (not name) of your project. Ignored by DirectRunner',
        required=True)
    parser.add_argument(
        '--runner',
        help='If omitted, uses DataFlowRunner if output_dir starts with gs://',
        default=None)
    parser.add_argument(
        '--output_dir', help='Top-level directory for TF Records', required=True)

    args = parser.parse_args()
    arguments = args.__dict__

    JOBNAME = (
            'preprocess-images-' + datetime.datetime.now().strftime('%y%m%d-%H%M%S'))

    PROJECT = arguments['project_id']
    OUTPUT_DIR = arguments['output_dir']

    # set RUNNER using command-line arg or based on output_dir path
    on_cloud = OUTPUT_DIR.startswith('gs://')
    if arguments['runner']:
        RUNNER = arguments['runner']
    else:
        RUNNER = 'DataflowRunner' if on_cloud else 'DirectRunner'

    # clean-up output directory since Beam will name files 0000-of-0004 etc.
    # and this could cause confusion if earlier run has 0000-of-0005, for eg
    if on_cloud:
        try:
            subprocess.check_call(
                'gsutil -m rm -r {}'.format(OUTPUT_DIR).split())
        except subprocess.CalledProcessError:
            pass
    else:
        shutil.rmtree(OUTPUT_DIR, ignore_errors=True)
        os.makedirs(OUTPUT_DIR)

    # set up Beam pipeline to convert images to TF Records
    options = {
        'staging_location': os.path.join(OUTPUT_DIR, 'tmp', 'staging'),
        'temp_location': os.path.join(OUTPUT_DIR, 'tmp'),
        'job_name': JOBNAME,
        'project': PROJECT,
        'teardown_policy': 'TEARDOWN_ALWAYS',
        'save_main_session': True
    }
    opts = beam.pipeline.PipelineOptions(flags=[], **options)

    with beam.Pipeline(RUNNER, options=opts) as p:
        # BEAM tasks
        # for step in ['train', 'validation']:
        for step in ['train']:
            _ = (
                    p
                    | '{}_read_csv'.format(step) >> beam.io.ReadFromText(arguments['{}_csv'.format(step)])
                    | '{}_convert'.format(step) >> beam.FlatMap(lambda line: convert_to_example(line))
                    | '{}_write_tfr'.format(step) >> beam.io.tfrecordio.WriteToTFRecord(os.path.join(OUTPUT_DIR, step)))
    print("DONE")
