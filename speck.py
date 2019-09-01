##
# Speck 32/64 구현 클래스
class Speck:

    WORDSIZE = 16
    ALPHA = 7
    BETA = 2

    ## 생성자
    # @param self 객체 포인터
    def __init__(self):
        self.mask = 2 ** self.WORDSIZE - 1
    
    ## 왼쪽 회전 연산
    # @param self 객체 포인터
    # @param value 회전 연산을 수행할 변수값
    # @param amount 회전량
    def rol(self, value, amount):
        return (((value << amount) & self.mask) | (value >> (self.WORDSIZE - amount)))

    ## 오른쪽 회전 연산
    # @param self 객체 포인터
    # @param value 회전 연산을 수행할 변수값
    # @param amount 회전량
    def ror(self, value, amount):
        return (((value >> amount) & self.mask) | (value << (self.WORDSIZE - amount)))

    ## 키스케쥴링
    # @param self 객체 포인터
    # @param mk 마스터 키
    # @param num_rounds 라운드 수
    def expand_key(self, mk, num_rounds):
        rks = [0 for i in range(num_rounds)]
        rks[0] = mk[len(mk) - 1]
        l = list(reversed(mk[:len(mk) - 1]))
        for i in range(num_rounds - 1):
            l[i%3], rks[i+1] = self.encrypt_one_round((l[i%3], rks[i]), i)
        return rks

    ## 한 라운드 암호화
    # @param self 객체 포인터
    # @param pt 암호화 할 평문
    # @param rk 라운드 키
    def encrypt_one_round(self, pt, rk):
        c0, c1 = pt[0], pt[1]
        c0 = self.ror(c0, self.ALPHA)
        c0 = (c0 + c1) & self.mask
        c0 = c0 ^ rk
        c1 = self.rol(c1, self.BETA)
        c1 = c1 ^ c0

        return c0, c1

    ## 한 라운드 복호화
    # @param self 객체 포인터
    # @param ct 복호화 할 암호문
    # @param rk 라운드 키
    def decrypt_one_round(self, ct, rk):
        p0, p1 = ct[0], ct[1]
        p1 = p1 ^ p0
        p1 = self.ror(p1, self.BETA)
        p0 = p0 ^ rk
        p0 = (p0 - p1) & self.mask
        p0 = self.rol(p0, self.ALPHA)

        return p0, p1

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
    def check_testvector(self):
        key = (0x1918,0x1110,0x0908,0x0100)
        pt = (0x6574, 0x694c)
        ks = self.expand_key(key, 22)
        ct = self.encrypt(pt, ks)

        if (ct == (0xa868, 0x42f2)):
          print("Testvector verified.")
          return(True);

        else:
          print("Testvector not verified.")
          return(False);
