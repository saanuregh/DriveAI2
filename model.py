import tensorflow as tf


def model_fn(input_shape, learning_rate):
    img_input = tf.keras.layers.Input(shape=input_shape, name='ImageInput')
    img_model = tf.keras.layers.Conv2D(48, (7, 7), padding='valid', strides=(2, 2), activation='relu', name='Conv1')(
        img_input)
    img_model = tf.keras.layers.Conv2D(64, (7, 7), padding='valid', activation='relu', name='Conv2')(img_model)
    img_model = tf.keras.layers.AveragePooling2D((2, 2), strides=(2, 2), padding='same', name='Pool1')(img_model)
    img_model = tf.keras.layers.Conv2D(96, (5, 5), padding='valid', activation='relu', name='Conv3')(img_model)
    img_model = tf.keras.layers.Conv2D(128, (5, 5), padding='valid', activation='relu', name='Conv4')(img_model)
    img_model = tf.keras.layers.AveragePooling2D((2, 2), strides=(2, 2), padding='same', name='Pool2')(img_model)
    img_model = tf.keras.layers.Conv2D(192, (3, 3), padding='valid', activation='relu', name='Conv5')(img_model)
    img_model = tf.keras.layers.Conv2D(256, (3, 3), padding='valid', activation='relu', name='Conv6')(img_model)
    img_model = tf.keras.layers.AveragePooling2D((2, 2), strides=(2, 2), padding='same', name='Pool3')(img_model)
    img_model = tf.keras.layers.Conv2D(384, (3, 3), padding='valid', activation='relu', name='Conv7')(img_model)
    img_model = tf.keras.layers.Conv2D(512, (3, 3), padding='valid', activation='relu', name='Conv8')(img_model)
    img_model = tf.keras.layers.Flatten(name="Flatten")(img_model)

    speed_input = tf.keras.layers.Input(shape=(1,), name='SpeedInput')

    cct = tf.keras.layers.Concatenate(axis=1, name='Concatenate1')([img_model, speed_input])
    x = tf.keras.layers.Dense(4096, activation='relu', name='Dense1')(cct)
    x = tf.keras.layers.Dropout(0.5, name='Dropout1')(x)
    x = tf.keras.layers.Dense(3072, activation='relu', name='Dense2')(x)
    x = tf.keras.layers.Dropout(0.5, name='Dropout2')(x)
    x = tf.keras.layers.Dense(204, activation='relu', name='Dense3')(x)
    x = tf.keras.layers.Dropout(0.5, name='Dropout3')(x)
    x = tf.keras.layers.Dense(1024, activation='relu', name='Dense4')(x)
    x = tf.keras.layers.Dropout(0.5, name='Dropout4')(x)
    prediction = tf.keras.layers.Dense(3, name='Output')(x)

    model = tf.keras.models.Model(inputs=[img_input, speed_input], outputs=prediction)

    model.compile(optimizer=tf.keras.optimizers.Adam(lr=learning_rate),
                  loss='mean_squared_error',
                  metrics=['accuracy'])
    model.summary()

    return model
