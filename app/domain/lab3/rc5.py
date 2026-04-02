# Variant 24 w = 64, r = 20, b = 8
# RC5-64/20/8

from __future__ import annotations
import math
from pathlib import Path
from app.domain.lab2.md5 import MD5
import time
from app.domain.lab1.linear_compare_algo import LinearCompareAlgo

class RC5:

    w = 64 # length of word
    r = 20 # number of rounds
    b = 8 # length of a key byte

    word_mask = (1 << w) - 1
    word_bytes = w // 8
    block_bytes = 2 * word_bytes

    P = 0xB7E151628AED2A6B
    Q = 0x9E3779B97F4A7C15

    def __init__(self, key: bytes):
        if len(key) != self.b:
            raise ValueError(f"key must be exactly {self.b} bytes long")

        self.key = key
        self.s = self.key_expansion(key)


    @staticmethod
    def cyclic_shift_left(x: int, s: int, w: int = 64) -> int:
        mask = (1 << w) - 1
        s %= w
        return ((x << s) | (x >> (w - s))) & mask

    @staticmethod
    def cyclic_shift_right(x: int, s: int, w: int = 64) -> int:
        mask = (1 << w) - 1
        s %= w
        return ((x >> s) | (x << (w - s))) & mask

    @staticmethod
    def xor_bytes(a: bytes, b: bytes) -> bytes:
        return bytes(x ^ y for x, y in zip(a, b))

    @staticmethod
    def divide_block(block: bytes) -> tuple[int, int]:
        if len(block) != 16:
            raise ValueError(f"Block must be exactly 16 bytes long")
        A = int.from_bytes(block[:RC5.word_bytes], byteorder="little")
        B = int.from_bytes(block[RC5.word_bytes:], byteorder="little")
        return A, B

    @staticmethod
    def join_block(A: int, B: int) -> bytes:
        return (A.to_bytes(8, byteorder="little") + B.to_bytes(8, byteorder="little"))

    def key_expansion(self, key: bytes) -> list[int]:
        u = self.word_bytes
        c = max(1, math.ceil(len(key) / u))
        t = 2 * (self.r + 1)

        L = [0] * c
        for i in range(len(key) -1, -1, -1):
            L[i // u] = ((L[i // u] << 8) + key[i]) & self.word_mask

        s = [0] * t
        s[0] = self.P
        for i in range(1, t):
            s[i] = (s[i - 1] + self.Q) & self.word_mask

        a = b = 0
        i = j = 0
        n = 3 * max(t, c)

        for _ in range(n):
            a = s[i] = self.cyclic_shift_left((s[i] + a + b) & self.word_mask, 3, self.w)
            b = L[j] = self.cyclic_shift_left((L[j] + a + b) & self.word_mask, (a + b), self.w)
            i = (i + 1) % t
            j = (j + 1) % c

        return s

    def encrypt(self, block: bytes) -> bytes:
        A, B = self.divide_block(block)

        A = (A + self.s[0]) & self.word_mask
        B = (B + self.s[1]) & self.word_mask

        for i in range(1, self.r + 1):
            A = (self.cyclic_shift_left(A ^ B, B, self.w) + self.s[2 * i]) & self.word_mask
            B = (self.cyclic_shift_left(B ^ A, A, self.w) + self.s[2 * i + 1]) & self.word_mask

        return self.join_block(A, B)

    def decrypt(self, block: bytes) -> bytes:
        A, B = self.divide_block(block)

        for i in range(self.r, 0, -1):
            B = self.cyclic_shift_right((B - self.s[2 * i + 1]) & self.word_mask, A, self.w) ^ A
            A = self.cyclic_shift_right((A - self.s[2 * i]) & self.word_mask, B, self.w) ^ B

        B = (B - self.s[1]) & self.word_mask
        A = (A - self.s[0]) & self.word_mask

        return self.join_block(A, B)

    def pad(self, data: bytes) -> bytes:
        pad_len = self.block_bytes - (len(data) % self.block_bytes)
        if pad_len == 0:
            pad_len = self.block_bytes
        return data + bytes([pad_len] * pad_len)

    def unpad(self, data: bytes) -> bytes:
        if not data or len(data) % self.block_bytes != 0:
            raise ValueError("Invalid padded data length")

        pad_len = data[-1]
        if pad_len < 1 or pad_len > self.block_bytes:
            raise ValueError("Invalid padding")

        if data[-pad_len:] != bytes([pad_len] * pad_len):
            raise ValueError("Invalid padding bytes")

        return data[:-pad_len]
    def encrypt_iv(self, iv: bytes) -> bytes:
        if len(iv) != self.block_bytes:
            raise ValueError("IV must be 16 bytes")
        return self.encrypt(iv)

    def decrypt_iv(self, encrypted_iv: bytes) -> bytes:
        if len(encrypted_iv) != self.block_bytes:
            raise ValueError("Encrypted IV must be 16 bytes")
        return self.decrypt(encrypted_iv)

    def encrypt_cbc(self, plaintext: bytes, iv: bytes) -> bytes:
        if len(iv) != self.block_bytes:
            raise ValueError("IV must be 16 bytes")

        plaintext = self.pad(plaintext)
        result = bytearray()
        prev = iv

        for i in range(0, len(plaintext), self.block_bytes):
            block = plaintext[i : i + self.block_bytes]
            xored = self.xor_bytes(block, prev)
            cipher_block = self.encrypt(xored)
            result.extend(cipher_block)
            prev = cipher_block

        return bytes(result)

    def decrypt_cbc(self, ciphertext: bytes, iv: bytes) -> bytes:
        if len(iv) != self.block_bytes:
            raise ValueError("IV must be 16 bytes")

        if len(ciphertext) % self.block_bytes != 0:
            raise ValueError("Ciphertext length must be multiple of block size")

        result = bytearray()
        prev = iv

        for i in range(0, len(ciphertext), self.block_bytes):
            cipher_block = ciphertext[i:i + self.block_bytes]
            decrypted = self.decrypt(cipher_block)
            plain_block = self.xor_bytes(decrypted, prev)
            result.extend(plain_block)
            prev = cipher_block

        return self.unpad(bytes(result))

    @classmethod
    def key_from_password(cls, password: str) -> bytes:
        password_bytes = password.encode("utf-8")

        digest = MD5.md5(password_bytes)

        if not isinstance(digest, (bytes, bytearray)) or len(digest) != 16:
            raise ValueError("md5_func must return 16-byte digest")

        return bytes(digest[8:16])

    @classmethod
    def from_password(cls, password: str) -> "RC5":
        key = cls.key_from_password(password)
        return cls(key)

    @staticmethod
    def generate_iv_bytes(n: int) -> bytes:
        seed = int(time.time_ns()) % (2 ** 31)

        gen = LinearCompareAlgo(
            m=2 ** 31,
            a=1103515245,
            c=12345,
            seed=seed
        )
        result = bytearray()

        for _ in range(n):
            value = gen.next_int()
            result.append(value & 0xFF)
        return bytes(result)

    def encrypt_file(self, input_path: str, output_path: str, iv_generator_func) -> None:
        input_path = Path(input_path)
        output_path = Path(output_path)

        plaintext = input_path.read_bytes()

        iv = iv_generator_func(self.block_bytes)
        if not isinstance(iv, (bytes, bytearray)) or len(iv) != self.block_bytes:
            raise ValueError(f"iv_generator_func must return {self.block_bytes} bytes")

        encrypted_iv = self.encrypt_iv(bytes(iv))
        ciphertext = self.encrypt_cbc(plaintext, bytes(iv))

        output_path.write_bytes(encrypted_iv + ciphertext)

    def decrypt_file(self, input_path: str, output_path: str) -> None:
        input_path = Path(input_path)
        output_path = Path(output_path)

        data = input_path.read_bytes()

        if len(data) < self.block_bytes:
            raise ValueError("Encrypted file is too short")

        encrypted_iv = data[:self.block_bytes]
        ciphertext = data[self.block_bytes:]

        if len(ciphertext) % self.block_bytes != 0:
            raise ValueError("Invalid encrypted file length")

        iv = self.decrypt_iv(encrypted_iv)
        plaintext = self.decrypt_cbc(ciphertext, iv)

        output_path.write_bytes(plaintext)