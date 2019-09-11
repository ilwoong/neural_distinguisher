import model
import numpy as np
import samples
import datetime

from math import log2
from time import time
from speck import Speck
from os import urandom

cipher = Speck()

## 평문 데이터 구조 생성
# @param num_samples 샘플 개수
# @param diff 입력 차분
# @return 평문, 평문 ^ diff 데이터 구조
def generate_plaintext_structure(num_samples, diff=(0x0000, 0x0040)):
    lhs0 = np.frombuffer(urandom(2 * num_samples), dtype=np.uint16)
    rhs0 = np.frombuffer(urandom(2 * num_samples), dtype=np.uint16)

    lhs1 = lhs0 ^ diff[0]
    rhs1 = rhs0 ^ diff[1]

    return lhs0, rhs0, lhs1, rhs1

## 키의 랭크 값을 계산
# @param net 모델
# @param l0, r0 평문
# @param l1, r1 평문 ^ diff
# @param rk 라운드 키
def rank_key(net, l0, r0, l1, r1, rk):    
    lhs0, rhs0 = cipher.decrypt_one_round((l0, r0), rk)
    lhs1, rhs1 = cipher.decrypt_one_round((l1, r1), rk)

    x = samples.convert_to_binary([lhs0, rhs0, lhs1, rhs1])
    v = net.predict(x, batch_size=10000)
    v = v / (1 - v)
    v = np.log2(v)

    return v.sum()

## 마지막 라운드 키 복구
# @param num_test 테스트 횟수
# @param target_round 대상 라운드 (5, 6, 7 만 가능)
def attack(num_test=5, target_round=6):
    # numpy 배열 출력을 hex 형식으로 변환
    np.set_printoptions(formatter={'int':hex})
    net = model.load_resnet(target_round - 1, 1)
    net.summary()

    for i in range(num_test):
        start = time()
        
        print("<<Test",i,">>")
        print("Recovery attack started: ", datetime.datetime.now())

        mk = np.frombuffer(urandom(8), dtype=np.uint16)
        rks = cipher.expand_key(mk, target_round)

        lhs0, rhs0, lhs1, rhs1 = generate_plaintext_structure(100)

        cl0, cr0 = cipher.encrypt((lhs0, rhs0), rks)
        cl1, cr1 = cipher.encrypt((lhs1, rhs1), rks)

        num_keys = 2**16
        rank = np.zeros(num_keys, dtype=np.float)

        # 2**16개의 키에 대해 랭크 계산
        for guess in range(num_keys):
            rank[guess]= rank_key(net, cl0, cr0, cl1, cr1, guess)
        
        # 랭크 기준으로 내림차순 정렬
        idx = np.argsort(rank)[::-1]

        elapsed = time() - start

        print("Recovery attack ended: ", datetime.datetime.now())
        print("Elapsed", elapsed)

        # 상위 3개 랭크 값을 가지는 추측 키 출력
        for j in range(4):
            print("Guessed", hex(idx[j]), ", Rank", rank[idx[j]])

        real_key = rks[target_round-1]
        real_key_rank = rank_key(net, cl0, cr0, cl1, cr1, real_key)
        
        print("Real key", hex(real_key), ", Rank", real_key_rank)
        print()
