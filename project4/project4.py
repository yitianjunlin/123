import random
import time

IV = [0x7380166F, 0x4914B2B9, 0x172442D7, 0xDA8A0600,
      0xA96F30BC, 0x163138AA, 0xE38DEE4D, 0xB0FB0E4E]

def leftshift(s, l):
    l = l % 32
    return (((s << l) & 0xFFFFFFFF) | ((s & 0xFFFFFFFF) >> (32 - l)))

def FF(s1, s2, s3, i):
    if i >= 0 and i <= 15:
        return s1 ^ s2 ^ s3
    elif i >= 16 and i <= 63:
        return ((s1 & s2) | (s1 & s3) | (s2 & s3))

def GG(s1, s2, s3, i):
    if i >= 0 and i <= 15:
        return s1 ^ s2 ^ s3
    elif i >= 16 and i <= 63:
        return ((s1 & s2) | ((not s1) & s3))

def P0(s):
    return s ^ leftshift(s, 9) ^ leftshift(s, 17)

def P1(s):
    return s ^ leftshift(s, 15) ^ leftshift(s, 23)

def T(i):
    if i >= 0 and i <= 15:
        return 0x79cc4519
    elif i >= 16 and i <= 63:
        return 0x7a879d8a

def padding(message):
    m = bin(int(message, 16))[2:]
    if len(m) != len(message) * 4:
        m = '0' * (len(message) * 4 - len(m)) + m
    l = len(m)
    l_bin = '0' * (64 - len(bin(l)[2:])) + bin(l)[2:]
    m = m + '1'
    m = m + '0' * (448 - len(m) % 512) + l_bin
    m = hex(int(m, 2))[2:]
    return m

def ck(m):
    n = len(m) / 128
    M = []
    for i in range(int(n)):
        M.append(m[0 + 128 * i:128 + 128 * i])
    return M

def message_extension(M, n):
    C = []
    C1 = []
    for j in range(16):
        C.append(int(M[n][0 + 8 * j:8 + 8 * j], 16))
    for j in range(16, 68):
        C.append(P1(C[j - 16] ^ C[j - 9] ^ leftshift(C[j - 3], 15)) ^ leftshift(C[j - 13], 7) ^ C[j - 6])
    for j in range(64):
        C1.append(C[j] ^ C[j + 4])
    s1 = ''
    s2 = ''
    for x in C:
        s1 += (hex(x)[2:] + ' ')
    for x in C1:
        s2 += (hex(x)[2:] + ' ')
    return C, C1

def message_compress(V, M, i):
    A, B, C, D, E, F, G, H = V[i]
    W, W1 = message_extension(M, i)
    for j in range(64):
        SS1 = leftshift((leftshift(A, 12) + E + leftshift(T(j), j % 32)) % (2 ** 32), 7)
        SS2 = SS1 ^ leftshift(A, 12)
        TT1 = (FF(A, B, C, j) + D + SS2 + W1[j]) % (2 ** 32)
        TT2 = (GG(E, F, G, j) + H + SS1 + W[j]) % (2 ** 32)
        D = C
        C = leftshift(B, 9)
        B = A
        A = TT1
        H = G
        G = leftshift(F, 19)
        F = E
        E = P0(TT2)

    a, b, c, d, e, f, g, h = V[i]
    V1 = [a ^ A, b ^ B, c ^ C, d ^ D, e ^ E, f ^ F, g ^ G, h ^ H]
    return V1

# sm3实现
def SM3(M):
    n = len(M)
    V = []
    V.append(IV)
    for i in range(n):
        V.append(message_compress(V, M, i))
    return V[n]

start = time.perf_counter()
r = random.randint(0, pow(2, 64))
m = padding(str(r))
M = ck(m)
Mn = SM3(M)
print(Mn)
end = time.perf_counter()
print("时间：")
print(end-start)
