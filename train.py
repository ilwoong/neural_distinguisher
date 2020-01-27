import model
import samples
import tensorflow as tf
from simon import Simon
from speck import Speck

## DNN 모델 학습
# 5~8 라운드 distinguisher 모델을 학습한다.
def train_dnns(epochs=200, samples=10**7, layers=3, lower_round=5, upper_round=8):
    for round in range(lower_round, upper_round):        
        model.train_dnn(epochs=epochs, num_samples=samples, num_rounds=round, num_layers=layers)

## ResNet 모델 학습
#  파라미터를 변화시켜가면서 모델을 학습한다.
def train_resnets(train, test, epochs=200, depth=1, lower_round=5, upper_round=8):
    for round in range(lower_round, upper_round):
        model.train_resnet(epochs = epochs, train=train, test=test, num_rounds = round, depth = depth)

## 전체 모델 학습
def train_all(epochs=200, samples=10**7):
    train_dnns(epochs=epochs, samples=samples)
    #train_resnets(epochs=epochs, samples=samples, depth=1)
    #train_resnets(epochs=epochs, samples=samples, depth=10)

with tf.device('/device:GPU:0'):
    epochs = 200
        
    cipher = Speck()
    round = 5
    diff = (0x0000, 0x0040)
    prefix = "speck"    

    train, test = samples.generate_samples(10**7, round, diff=diff, cipher=cipher)
    model.train_resnet(epochs=epochs, train=train, test=test, num_rounds=round, depth=1, prefix=prefix)
    model.train_resnet(epochs=epochs, train=train, test=test, num_rounds=round, depth=5, prefix=prefix)
    model.train_resnet(epochs=epochs, train=train, test=test, num_rounds=round, depth=10, prefix=prefix)
