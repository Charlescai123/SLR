# encoding: utf-8


from keras.layers import Dense,Dropout,Conv3D,Input,MaxPool3D,Flatten,Activation,BatchNormalization
from keras.regularizers import l2
from keras.models import Model,load_model

from keras.optimizers import SGD

#%%
def c3d_model(param):
    input_shape = param['input_shape']
    weight_decay = param['weight_decay']
    num_classes = param['num_classes']

    inputs = Input(input_shape)
    x = Conv3D(32, (3, 3, 3), strides=(1, 1, 1), padding='same',
               activation='relu', kernel_regularizer=l2(weight_decay))(inputs)
    x = MaxPool3D((2, 2, 1), strides=(2, 2, 1), padding='same')(x)

    x = BatchNormalization()(x)

    x = Conv3D(64, (3, 3, 3), strides=(1, 1, 1), padding='same',
               activation='relu', kernel_regularizer=l2(weight_decay))(x)
    x = MaxPool3D((2, 2, 2), strides=(2, 2, 2), padding='same')(x)

    x = BatchNormalization()(x)

    x = Conv3D(128, (3, 3, 3), strides=(1, 1, 1), padding='same',
               activation='relu', kernel_regularizer=l2(weight_decay))(x)
    x = MaxPool3D((2, 2, 2), strides=(2, 2, 2), padding='same')(x)
    
    x = Conv3D(256, (3, 3, 3), strides=(1, 1, 1), padding='same',
               activation='relu', kernel_regularizer=l2(weight_decay))(x)
    x = MaxPool3D((2, 2, 2), strides=(2, 2, 2), padding='same')(x)

    x = Conv3D(256, (3, 3, 3), strides=(1, 1, 1), padding='same',
               activation='relu', kernel_regularizer=l2(weight_decay))(x)
    x = MaxPool3D((2, 2, 2), strides=(2, 2, 2), padding='same')(x)

    x = BatchNormalization()(x)

    x = Flatten()(x)
    x = Dense(128, activation='relu', kernel_regularizer=l2(weight_decay))(x)
    x = Dropout(0.2)(x)
    x = Dense(64, activation='relu', kernel_regularizer=l2(weight_decay))(x)
    x = Dropout(0.2)(x)
    x = Dense(num_classes, kernel_regularizer=l2(weight_decay))(x)
    x = Activation('softmax')(x)

    model = Model(inputs, x)
    return model

