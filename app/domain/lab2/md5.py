from __future__ import annotations
import math
import struct
from dataclasses import dataclass

def _left_rotate(x: int, amount: int) -> int:
    x &= 0xFFFFFFFF
    return ((x << amount) | (x >> (32 - amount))) & 0xFFFFFFFF

_S = (
    7, 12, 17, 22,  7, 12, 17, 22,  7, 12, 17, 22,  7, 12, 17, 22,
    5,  9, 14, 20,  5,  9, 14, 20,  5,  9, 14, 20,  5,  9, 14, 20,
    4, 11, 16, 23,  4, 11, 16, 23,  4, 11, 16, 23,  4, 11, 16, 23,
    6, 10, 15, 21,  6, 10, 15, 21,  6, 10, 15, 21,  6, 10, 15, 21,
)

_T = tuple(int((1 << 32) * abs(math.sin(i + 1))) & 0xFFFFFFFF for i in range(64))

def _F(b: int, c: int, d: int) -> int:
    return (b & c) | (~b & d)

def _G(b: int, c: int, d: int) -> int:
    return (b & d) | (c & ~d)

def _H(b: int, c: int, d: int) -> int:
    return b ^ c ^ d

def _I(b: int, c: int, d: int) -> int:
    return c ^ (b | ~d)

@dataclass
class MD5:
    _a: int = 0x67452301
    _b: int = 0xEFCDAB89
    _c: int = 0x98BADCFE
    _d: int = 0x10325476
    _count_bits: int = 0
    _buffer: bytes = b""

    def update(self, data: bytes) -> "MD5":
        if not data:
            return self

        self._count_bits = (self._count_bits + (len(data) * 8)) & 0xFFFFFFFFFFFFFFFF
        self._buffer += data

        while len(self._buffer) >= 64:
            block = self._buffer[:64]
            self._buffer = self._buffer[64:]
            self._process_block(block)

        return self

    def _process_block(self, block: bytes) -> None:
        x = list(struct.unpack("<16I", block))

        a, b, c, d = self._a, self._b, self._c, self._d

        for i in range(64):
            if 0 <= i <= 15:
                f = _F(b, c, d)
                g = i
            elif 16 <= i <= 31:
                f = _G(b, c, d)
                g = (1 + 5 * i) % 16
            elif 32 <= i <= 47:
                f = _H(b, c, d)
                g = (5 + 3 * i) % 16
            else:
                f = _I(b, c, d)
                g = (7 * i) % 16

            temp = (a + f + _T[i] + x[g]) & 0xFFFFFFFF
            temp = _left_rotate(temp, _S[i])
            temp = (temp + b) & 0xFFFFFFFF

            a, d, c, b = d, c, b, temp

        self._a = (self._a + a) & 0xFFFFFFFF
        self._b = (self._b + b) & 0xFFFFFFFF
        self._c = (self._c + c) & 0xFFFFFFFF
        self._d = (self._d + d) & 0xFFFFFFFF

    def digest(self) -> bytes:
        clone = MD5(self._a, self._b, self._c, self._d, self._count_bits, self._buffer)

        pad = b"\x80"
        pad_len = (56 - ((len(clone._buffer) + 1) % 64)) % 64
        pad += b"\x00" * pad_len

        length_bytes = struct.pack("<Q", clone._count_bits)

        clone.update(pad + length_bytes)

        return struct.pack("<4I", clone._a, clone._b, clone._c, clone._d)

    def hexdigest(self) -> str:
        return self.digest().hex()

    @staticmethod
    def md5(data: bytes) -> bytes:
        return MD5().update(data).digest()

    @staticmethod
    def md5_hex(data: bytes) -> str:
        return MD5().update(data).hexdigest()