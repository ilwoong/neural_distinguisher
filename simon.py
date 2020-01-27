#-*-coding:utf-8-*-

from cipher import Cipher 
import numpy as np

## Simon 32/64 구현
class Simon(Cipher):

    Z = [1,1,1,1,1,0,1,0,0,0,1,0,0,1,0,1,0,1,1,0,0,0,0,1,1,1,0,0,1,1,0,1,1,1,1,1,0,1,0,0,0,1,0,0,1,0,1,0,1,1,0,0,0,0,1,1,1,0,0,1,1,0]

    def __init__(self):
        self.WORDSIZE = 16
        self.WORDMASK = 2 ** self.WORDSIZE - 1
        self.NUM_ROUNDS = 32

    def name(self):
        return "Simon-32/64"

    ## 키 스케쥴링
    def expand_key(self, mk, num_rounds):
        rks = [0 for i in range(num_rounds)]

        rks[0] = mk[0]
        rks[1] = mk[1]
        rks[2] = mk[2]
        rks[3] = mk[3]

        for i in range(4, num_rounds):
            tmp = self.ror(rks[i-1], 3) ^ rks[i-3]
            tmp = tmp ^ self.ror(tmp, 1)
            rks[i] = (~rks[i-4] ^ tmp ^ self.Z[i-4] ^ 0x3) & self.WORDMASK
            
        return rks
    
    ## 한 라운드 암호화
    def encrypt_one_round(self, pt, rk):        
        lhs, rhs = np.copy(pt[0]), np.copy(pt[1])
        lhs = lhs ^ (self.rol(rhs, 1) & self.rol(rhs, 8)) ^ self.rol(rhs, 2) ^ rk
        
        return rhs, lhs
    
    ## 한 라운드 복호화
    def decrypt_one_round(self, ct, rk):
        lhs, rhs = np.copy(ct[0]), np.copy(ct[1])
        rhs = rhs ^ (self.rol(lhs, 1) & self.rol(lhs, 8)) ^ self.rol(lhs, 2) ^ rk
        
        return rhs, lhs

    ## 테스트벡터 확인
    def check_testvector(self):
        key = (0x0100, 0x0908, 0x1110, 0x1918,)
        pt = (0x6877, 0x6565)
        ct = (0xe9bb, 0xc69b)
        
        super().check_testvector(key, pt, ct)