from abc import *

class Cipher(metaclass=ABCMeta):
    WORDSIZE = 0
    WORDMASK = 0
    NUM_ROUNDS = 0

    @abstractmethod
    def name(self):
        pass

    @abstractmethod
    def expand_key(self, mk, num_rounds):
        pass

    @abstractmethod
    def encrypt_one_round(self, pt, rk):
        pass

    @abstractmethod
    def decrypt_one_round(self, pt, rk):
        pass

    ## 왼쪽 회전 연산
    # @param self 객체 포인터
    # @param value 회전 연산을 수행할 변수값
    # @param amount 회전량
    def rol(self, value, amount):
        return ((value << amount) | (value >> (self.WORDSIZE - amount))) & self.WORDMASK

    ## 오른쪽 회전 연산
    # @param self 객체 포인터
    # @param value 회전 연산을 수행할 변수값
    # @param amount 회전량
    def ror(self, value, amount):
        return ((value >> amount) | (value << (self.WORDSIZE - amount))) & self.WORDMASK

    ## 여러 라운드 암호화
    # @param self 객체 포인터
    # @param pt 암호화 할 평문
    # @param rk 라운드 키
    def encrypt(self, pt, rks):
        x, y = pt[0], pt[1]
        for rk in rks:
            x, y = self.encrypt_one_round((x, y), rk)
        return x, y

    ## 여러 라운드 복호화
    # @param self 객체 포인터
    # @param ct 복호화 할 암호문
    # @param rk 라운드 키
    def decrypt(self, ct, rks):
        x, y = ct[0], ct[1]
        for rk in reversed(rks):
            x, y = self.decrypt_one_round((x, y), rk)
        return x, y

    ## 테스트벡터 확인
    # @param self 객체 포인터
    def check_testvector(self, key, pt, ct):
        rks = self.expand_key(key, self.NUM_ROUNDS)
        enc = self.encrypt(pt, rks)
        dec = self.decrypt(ct, rks)

        if (enc == ct and dec == pt):
            print("testvector verified")

        if (enc != ct):
            print("encryption failed")
            print(' '.join(format(x, '04x') for x in ct))
            print(' '.join(format(x, '04x') for x in enc))

        if (dec != pt):
            print("decryption failed")
            print(' '.join(format(x, '04x') for x in pt))
            print(' '.join(format(x, '04x') for x in dec))

    