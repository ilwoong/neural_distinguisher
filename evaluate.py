from speck import Speck
import samples
import model
import numpy as np

## 정확도 측정
# @param net 정확도를 측정하고자 하는 모델 
# @param x 암호문 쌍
# @param y 암호문 쌍이 지정된 입력 차분을 가진 평문으로부터 만들어졌는지의 여부
# @return 정확도
def get_accuracy(net, x, y):
    z = net.predict(x, batch_size=100000).flatten()
    zbin = (z > 0.5)
    acc = np.sum(zbin == y) / len(z)
    return acc

## ResNet 평가
# 기존에 학습된 모델을 불러와 정확도를 평가한다.
# @param resnet_depth Residual Layer의 깊이
def evaluate_resnet(resnet_depth = 1, lower_round=5, upper_round=8):
    num_samples = 10**6
    for num_rounds in range(lower_round, upper_round):
        net = model.load_resnet(num_rounds, resnet_depth)
        x, y = samples.make_train_data(num_samples, num_rounds)
        acc = get_accuracy(net, x, y)
        print("Round: ", num_rounds, " Accuracy: ", acc)

## DNN 평가
# 기존에 학습된 모델을 불러와 정확도를 평가한다.
def evaluate_dnn(lower_round=5, upper_round=8):
    num_samples = 10**6
    for num_rounds in range(lower_round, upper_round):
        net = model.load_dnn(num_rounds)
        x, y = samples.make_train_data(num_samples, num_rounds)
        acc = get_accuracy(net, x, y)
        print("Round: ", num_rounds, " Accuracy: ", acc)

## ResNet과 DNN 모델을 불러와 정확도를 출력한다.
def evaluate_models():
    print("Result of depth 1 ResNet")
    evaluate_resnet(resnet_depth = 1, lower_round=5, upper_round=6)
