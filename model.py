import speck
import samples
import numpy as np
import tensorflow.keras as keras

from tensorflow.keras.callbacks import ModelCheckpoint, LearningRateScheduler
from tensorflow.keras.regularizers import l2

def cyclic_lr_gohr(num_epochs, high, low):
    result = lambda i: low + ((num_epochs - 1) - i % num_epochs)/(num_epochs-1) * (high - low)
    return result

def cyclic_lr(n, alpha, beta):
    result = lambda i: alpha + ((n - i) % (n + 1)) / n * (beta - alpha)
    return result

def make_checkpoint(value):
    result = ModelCheckpoint(value, monitor='val_loss', save_best_only = True)
    return result

def prediction_head(in_layer, reg_param=0.0001):
    flat = keras.layers.Flatten()(in_layer)
    
    dense = keras.layers.Dense(64, kernel_regularizer=l2(reg_param)) (flat)
    dense = keras.layers.BatchNormalization() (dense)
    dense = keras.layers.Activation('relu') (dense)

    dense = keras.layers.Dense(64, kernel_regularizer=l2(reg_param)) (dense)
    dense = keras.layers.BatchNormalization() (dense)
    dense = keras.layers.Activation('relu') (dense)
    
    out = keras.layers.Dense(1, activation='sigmoid', kernel_regularizer=l2(reg_param))(dense)

    return out

## Speck32/64 Neural Distinguisher를 위한 모델 생성
#
# @param num_blocks 입력 블록의 개수
# @param word_size 기본 연산의 단위 워드 비트 수
# @param depth ResNet의 깊이
# @param num_filters Convolution 계층의 필터 개수
# @param kernel_size Convolution 계층의 커널 크기
# @param reg_param kernel regularizer의 입력 파라미터
# 
# @return 모델
def make_resnet(num_blocks = 2, word_size = 16, depth = 5, num_filters = 32, kernel_size = 3, reg_param=0.00001):
    inp = keras.layers.Input(shape=(num_blocks * word_size * 2, ))
    rs = keras.layers.Reshape((2 * num_blocks, word_size))(inp)
    perm = keras.layers.Permute((2, 1))(rs)

    conv0 = keras.layers.Conv1D(num_filters, kernel_size=1, padding='same', kernel_regularizer=l2(reg_param))(perm)
    conv0 = keras.layers.BatchNormalization()(conv0)
    conv0 = keras.layers.Activation('relu')(conv0)

    shortcut = conv0
    
    for i in range(depth):
        conv1 = keras.layers.Conv1D(num_filters, kernel_size = kernel_size, padding='same', kernel_regularizer=l2(reg_param)) (shortcut)
        conv1 = keras.layers.BatchNormalization() (conv1)
        conv1 = keras.layers.Activation('relu') (conv1)
        conv2 = keras.layers.Conv1D(num_filters, kernel_size = kernel_size, padding='same', kernel_regularizer=l2(reg_param)) (conv1)
        conv2 = keras.layers.BatchNormalization() (conv2)
        conv2 = keras.layers.Activation('relu') (conv2)
        shortcut = keras.layers.Add()([shortcut, conv2])

    #inp = input_layer()
    #res = resnet_towers()

    out = prediction_head(shortcut)
    
    model = keras.Model(inputs=inp, outputs=out)

    return model

## Speck32/64 Neural Distinguisher 학습
# @param num_epochs 학습에 사용할 epochs
# @param num_rounds 목표 라운드
# @param depth ResNet의 깊이
def train_resnet(epochs, num_samples=10**7, num_rounds = 5, depth = 1, reg_param = 0.00001):
    model = make_resnet(depth = depth, reg_param = reg_param)
    model.compile(optimizer='adam', loss='mse', metrics=['acc'])

    model.summary()

    x_train, y_train = samples.make_train_data(num_samples, num_rounds)
    x_test, y_test = samples.make_train_data(int(num_samples/10), num_rounds)

    filename = "r" + str(num_rounds) + '_d' + str(depth)

    check = make_checkpoint('best_resnet_' + filename + ".h5")

    lr = LearningRateScheduler(cyclic_lr(9, 0.0001, 0.002))

    h = model.fit(
            x_train, y_train, 
            epochs=epochs,
            batch_size=5000,
            validation_data=(x_test, y_test),
            callbacks=[lr, check],
    )
    print("Best validaation accuracy: ", np.max(h.history['val_acc']))
    
    return model, h

## DNN을 이용한 모델 생성
#
# @param num_blocks 블록 개수
# @param word_size 연산 단위 워드 길이 (비트)
# @param num_layers 신경망의 은닉계층 개수
# @param activation 활성함수 종료
def make_dnn(num_blocks = 2, word_size = 16, num_layers = 2, activation = 'relu'):
    model = keras.Sequential([
        keras.layers.InputLayer(input_shape=(num_blocks * word_size * 2,)),        
    ])
    
    for i in range(num_layers):
        model.add(keras.layers.Dense(64, activation=activation))

    model.add(keras.layers.Dense(1, activation='sigmoid'))

    return model

## DNN 모델 학습
#
# @param epochs 학습에 사용할 epoch 수
# @param num_rounds 대상 라운드 수
# @param num_layers 신경망의 은닉 계층 개수
def train_dnn(epochs = 10, num_rounds = 5, num_layers = 2):
    model = make_dnn(num_layers = num_layers)    
    model.compile(optimizer='adam', loss='mse', metrics=['acc'])

    model.summary()

    x_train, y_train = samples.make_train_data(10**7, num_rounds)
    x_test, y_test = samples.make_train_data(10**6, num_rounds)

    lr = LearningRateScheduler(cyclic_lr(9, 0.0001, 0.002))
    check = make_checkpoint('best_dnn_r' + str(num_rounds) + "_l" + str(num_layers) + ".h5")

    h = model.fit(
            x_train, y_train, 
            epochs=epochs,
            batch_size=5000,
            validation_data=(x_test, y_test),
            callbacks=[lr, check]
    )
    print("Best validaation accuracy: ", np.max(h.history['val_acc']))

    return model

## ResNet 모델 불러오기
# @param round 라운드 수
# @param depth Residual Layer의 깊이
# @return 파라미터에 해당하는 ResNet 모델
def load_resnet(round, depth):
    net = make_resnet(depth = depth)
    path = 'trained_models/best_resnet_r' + str(round) + '_d' + str(depth) + '.h5'
    net.load_weights(path)
    return net

## DNN 모델 불러오기
# @param round 라운드 수
# @return 파라미터에 해당하는 DNN 모델
def load_dnn(round):
    net = make_dnn(num_layers=3)
    path = 'trained_models/best_dnn_r' + str(round) + '_l' + str(3) + '.h5'
    net.load_weights(path)
    return net