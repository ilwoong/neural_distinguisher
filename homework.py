import model
import samples
import numpy as np
import datetime
import struct

from speck import Speck
from time import time
from os import urandom
from os import system

cipher = Speck()

## uint16 데이터 두개를 하나의 hex 문자열로 변환
# @param lhs 16비트 데이터
# @param rhs 16비트 데이터
# @param hex 문자열
def to_byte_order_hex_string(lhs, rhs):
    pt = [lhs, rhs]
    pt = np.array(pt).view(np.uint8)
    hexstr = ""
    for data in pt:
        hexstr += hex(data)[2:].zfill(2)
    return hexstr

## hex 문자열을 두 개의 uint16 데이터로 분리
# @param hexstr hex 문자열
# @return lhs, rhs 두 개의 16비트 데이터
def to_uint16_array(hexstr):
    lhs = bytearray.fromhex(hexstr[:4])
    rhs = bytearray.fromhex(hexstr[4:])

    lhs = lhs[0] | (lhs[1] << 8)
    rhs = rhs[0] | (rhs[1] << 8)

    return lhs, rhs

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

## 평문 데이터 구조 생성
# @param num_samples 샘플 개수
# @param diff 입력 차분
# @return 평문, 평문 ^ diff 데이터 구조
def generate_plaintext_structure(num_samples, diff=(0x0000, 0x0040)):
    lhs0, rhs0, lhs1, rhs1= [], [], [], []

    #TODO 선택 평문 공격을 할수 있도록 평문을 잘 생성하는 코드를 여기에 작성

    return lhs0, rhs0, lhs1, rhs1

## 평문 구조 저장하기
# 파일의 각 줄에 [평문0 평문1] 형태로 파일에 저장한다.
# @param lhs0 평문0의 첫번째 word
# @param rhs0 평문0의 두번째 word
# @param lhs1 평문1의 첫번째 word
# @param rhs1 평문1의 첫번째 word
def save_plaintext_structure(lhs0, rhs0, lhs1, rhs1, path = "plaintext_structure.txt"):
    fd = open(path, "w")

    for i in range(len(lhs0)):
        pt0 = to_byte_order_hex_string(lhs0[i], rhs0[i])
        pt1 = to_byte_order_hex_string(lhs1[i], rhs1[i])
        print(pt0, pt1)
        fd.write(pt0)
        fd.write(' ')
        fd.write(pt1)
        fd.write('\n')
        print()

    fd.close()

## 암호문 구조 읽어오기
# 파일의 각 줄에 [암호문0 암호문1] 형태로 저장되어 있는 암호문 구조를 읽어서 
# python 구현의 speck에 사용할 수 있도록 데이터를 변환한다.
# @param path 파일 경로
def load_ciphertext_structure(path="ciphertext_structure.txt"):
    fd = open(path, "r")

    lhs0, rhs0, lhs1, rhs1= [], [], [], []

    while True:
        line = fd.readline()
        if not line:
            break
        tokens = line.split()
        
        l0, r0 = to_uint16_array(tokens[0])
        l1, r1 = to_uint16_array(tokens[1])

        lhs0.append(l0)
        rhs0.append(r0)
        lhs1.append(l1)
        rhs1.append(r1)

    fd.close()
    return lhs0, rhs0, lhs1, rhs1

## 7라운드 Speck32/64 키 복구 공격
# 5라운드 distinguisher 혹은 6라운드 distinguisher 사용 가능
def recover_7round_key():
    start = time()

    print("Recovery attack started: ", datetime.datetime.now())

    #TODO 키 복구 공격 코드 여기에 작성

    elapsed = time() - start

    print("Recovery attack ended: ", datetime.datetime.now())
    print("Elapsed", elapsed)

    #TODO 상위 5개 랭크 값을 가지는 추측 키 출력
    
    print()


np.set_printoptions(formatter={'int':hex})

# 테스트 샘플 개수 설정, 자유롭게 설정할 것
num_samples = 100 

# 1. 선택 평문 공격을 위한 평문쌍 생성
lhs0, rhs0, lhs1, rhs1 = generate_plaintext_structure(num_samples)
save_plaintext_structure(lhs0, rhs0, lhs1, rhs1)

# 2. 생성된 plaintext_structure.txt 를 SpeckOracle을 이용하여 암호문 쌍 생성
system("SpeckOracle plaintext_structure.txt ciphertext_structure.txt")

# 3. 생성된 ciphertext_structure.txt 파일을 이용하여 키 복구 공격
recover_7round_key()