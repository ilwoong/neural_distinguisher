import numpy as np
from os import urandom
from speck import Speck

## 데이터를 이진으로 변환
# @param arr 변환할 데이터
# @param 이진값으로 변환된 데이터
def convert_to_binary(arr):
    x = np.zeros((4 * Speck.WORDSIZE, len(arr[0])), dtype=np.uint8)
    
    for i in range(4 * Speck.WORDSIZE):
        idx = i // Speck.WORDSIZE
        offset = Speck.WORDSIZE - (i % Speck.WORDSIZE) - 1
        x[i] = (arr[idx] >> offset) & 1
    
    return x.transpose()

## 학습 데이터 생성
# @param num_samples 생성할 데이터의 수
# @param num_rounds Speck 32/64 대상 라운드 수
# @param diff 입력 차분
# @return x 암호문 쌍
# @return y 입력차분을 가지는 평문에서 생성된 암호문인지의 여부
def make_train_data(num_samples, num_rounds, diff=(0x0040, 0)):
    y = np.frombuffer(urandom(num_samples), dtype=np.uint8) & 1
    keys = np.frombuffer(urandom(8 * num_samples), dtype=np.uint16).reshape(4,-1)

    pt0l = np.frombuffer(urandom(2 * num_samples), dtype=np.uint16)
    pt0r = np.frombuffer(urandom(2 * num_samples), dtype=np.uint16)

    pt1l = pt0l ^ diff[0]
    pt1r = pt0r ^ diff[1]

    num_random_samples = np.sum(y==0)

    pt1l[y==0] = np.frombuffer(urandom(2 * num_random_samples), dtype=np.uint16)
    pt1r[y==0] = np.frombuffer(urandom(2 * num_random_samples), dtype=np.uint16)

    sp = Speck()
    
    rks = sp.expand_key(keys, num_rounds)

    ct0l, ct0r = sp.encrypt((pt0l, pt0r), rks)
    ct1l, ct1r = sp.encrypt((pt1l, pt1r), rks)

    x = convert_to_binary([ct0l, ct0r, ct1l, ct1r])
    
    return x, y

