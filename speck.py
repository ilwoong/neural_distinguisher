#-*-coding:utf-8-*-

from cipher import Cipher
import numpy as np

##
# Speck 32/64 구현 클래스
class Speck(Cipher):

    ## 생성자
    # @param self 객체 포인터
    def __init__(self):
        self.WORDSIZE = 16
        self.WORDMASK = 2 ** self.WORDSIZE - 1
        self.NUM_ROUNDS = 22
        self.ALPHA = 7
        self.BETA = 2

    def name(self):
        return "Speck-32/64"

    ## 키스케쥴링
    # @param self 객체 포인터
    # @param mk 마스터 키
    # @param num_rounds 라운드 수
    def expand_key(self, mk, num_rounds):
        rks = [0 for i in range(num_rounds)]
        l = [0 for i in range(num_rounds + 2)]

        rks[0] = mk[0]
        l[0] = mk[1]
        l[1] = mk[2]
        l[2] = mk[3]

        for i in range(num_rounds - 1):
            l[i + 3] = (rks[i] + self.ror(l[i], self.ALPHA) ^ i) & self.WORDMASK
            rks[i + 1] = (self.rol(rks[i], self.BETA) ^ l[i + 3])

        return rks

    ## 한 라운드 암호화
    # @param self 객체 포인터
    # @param pt 암호화 할 평문
    # @param rk 라운드 키
    def encrypt_one_round(self, pt, rk):
        c0, c1 = np.copy(pt[0]), np.copy(pt[1])
        c1 = self.ror(c1, self.ALPHA)
        c1 = (c0 + c1) & self.WORDMASK
        c1 = c1 ^ rk

        c0 = self.rol(c0, self.BETA)
        c0 = c0 ^ c1

        return c0, c1

    ## 한 라운드 복호화
    # @param self 객체 포인터
    # @param ct 복호화 할 암호문
    # @param rk 라운드 키
    def decrypt_one_round(self, ct, rk):
        p0, p1 = np.copy(ct[0]), np.copy(ct[1])
        p0 = p1 ^ p0
        p0 = self.ror(p0, self.BETA)

        p1 = p1 ^ rk
        p1 = (p1 - p0) & self.WORDMASK
        p1 = self.rol(p1, self.ALPHA)

        return p0, p1

    ## 테스트벡터 확인
    # @param self 객체 포인터
    def check_testvector(self):
        key = (0x0100, 0x0908, 0x1110, 0x1918,)
        pt = (0x694c, 0x6574)
        ct = (0x42f2, 0xa868)

        super().check_testvector(key, pt, ct)