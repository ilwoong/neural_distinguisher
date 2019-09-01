import model

## DNN 모델 학습
# 5~8 라운드 distinguisher 모델을 학습한다.
def train_dnns(epochs=200, layers=3, lower_round=5, upper_round=8):
    for round in range(lower_round, upper_round):        
        model.train_dnn(epochs=epochs, num_rounds=round, num_layers=layers)

## ResNet 모델 학습
#  파라미터를 변화시켜가면서 모델을 학습한다.
def train_resnets(epochs=200, depth=1, lower_round=5, upper_round=8):
    for round in range(lower_round, upper_round):
        model.train_resnet(epochs = epochs, num_rounds = round, depth = depth)

## 전체 모델 학습
def train_all(epochs=1):
    train_dnns(epochs=epochs)
    train_resnets(epochs=epochs, depth=1)
    train_resnets(epochs=epochs, depth=10)
    