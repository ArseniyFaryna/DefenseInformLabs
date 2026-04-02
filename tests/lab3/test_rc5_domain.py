from __future__ import annotations
from pathlib import Path
import pytest
from app.domain.lab3.rc5 import RC5


@pytest.fixture
def rc5() -> RC5:
    return RC5(b"12345678")


def test_init_valid_key():
    cipher = RC5(b"12345678")
    assert cipher.key == b"12345678"
    assert len(cipher.s) == 2 * (cipher.r + 1)


def test_init_invalid_key_length():
    with pytest.raises(ValueError, match="key must be exactly 8 bytes long"):
        RC5(b"1234")


def test_cyclic_shift_left():
    x = 0x0123456789ABCDEF
    shifted = RC5.cyclic_shift_left(x, 8, 64)
    assert shifted == 0x23456789ABCDEF01


def test_cyclic_shift_right():
    x = 0x0123456789ABCDEF
    shifted = RC5.cyclic_shift_right(x, 8, 64)
    assert shifted == 0xEF0123456789ABCD


def test_xor_bytes():
    a = bytes([0xFF, 0x00, 0xAA])
    b = bytes([0x0F, 0xF0, 0xAA])
    assert RC5.xor_bytes(a, b) == bytes([0xF0, 0xF0, 0x00])


def test_divide_block_valid():
    block = bytes(range(16))
    A, B = RC5.divide_block(block)

    assert A == int.from_bytes(block[:8], byteorder="little")
    assert B == int.from_bytes(block[8:], byteorder="little")


def test_divide_block_invalid_length():
    with pytest.raises(ValueError, match="Block must be exactly 16 bytes long"):
        RC5.divide_block(b"short")


def test_join_block():
    A = 0x0123456789ABCDEF
    B = 0xFEDCBA9876543210

    block = RC5.join_block(A, B)

    assert len(block) == 16
    assert block[:8] == A.to_bytes(8, byteorder="little")
    assert block[8:] == B.to_bytes(8, byteorder="little")


def test_encrypt_decrypt_single_block(rc5: RC5):
    block = b"abcdefghijklmnop"  # 16 bytes

    encrypted = rc5.encrypt(block)
    decrypted = rc5.decrypt(encrypted)

    assert encrypted != block
    assert decrypted == block


def test_pad_adds_padding(rc5: RC5):
    data = b"hello"
    padded = rc5.pad(data)

    assert len(padded) % rc5.block_bytes == 0
    pad_len = padded[-1]
    assert padded.endswith(bytes([pad_len]) * pad_len)


def test_pad_full_block_adds_extra_block(rc5: RC5):
    data = b"a" * rc5.block_bytes
    padded = rc5.pad(data)

    assert len(padded) == len(data) + rc5.block_bytes
    assert padded[-1] == rc5.block_bytes


def test_unpad_valid(rc5: RC5):
    data = b"hello"
    padded = rc5.pad(data)

    assert rc5.unpad(padded) == data


def test_unpad_invalid_length(rc5: RC5):
    with pytest.raises(ValueError, match="Invalid padded data length"):
        rc5.unpad(b"")

    with pytest.raises(ValueError, match="Invalid padded data length"):
        rc5.unpad(b"123")


def test_unpad_invalid_padding_value(rc5: RC5):
    invalid = b"a" * 15 + b"\x00"
    with pytest.raises(ValueError, match="Invalid padding"):
        rc5.unpad(invalid)


def test_unpad_invalid_padding_bytes(rc5: RC5):
    invalid = b"abcdefghijklm" + b"\x03\x03\x02"
    with pytest.raises(ValueError, match="Invalid padding bytes"):
        rc5.unpad(invalid)


def test_encrypt_iv_valid(rc5: RC5):
    iv = b"1234567890abcdef"
    encrypted_iv = rc5.encrypt_iv(iv)

    assert len(encrypted_iv) == rc5.block_bytes
    assert encrypted_iv != iv


def test_encrypt_iv_invalid_length(rc5: RC5):
    with pytest.raises(ValueError, match="IV must be 16 bytes"):
        rc5.encrypt_iv(b"short")


def test_decrypt_iv_valid(rc5: RC5):
    iv = b"1234567890abcdef"
    encrypted_iv = rc5.encrypt_iv(iv)
    decrypted_iv = rc5.decrypt_iv(encrypted_iv)

    assert decrypted_iv == iv


def test_decrypt_iv_invalid_length(rc5: RC5):
    with pytest.raises(ValueError, match="Encrypted IV must be 16 bytes"):
        rc5.decrypt_iv(b"short")


def test_encrypt_decrypt_cbc(rc5: RC5):
    iv = b"1234567890abcdef"
    plaintext = b"Hello RC5 CBC mode test data!"

    ciphertext = rc5.encrypt_cbc(plaintext, iv)
    decrypted = rc5.decrypt_cbc(ciphertext, iv)

    assert ciphertext != plaintext
    assert decrypted == plaintext


def test_encrypt_cbc_invalid_iv(rc5: RC5):
    with pytest.raises(ValueError, match="IV must be 16 bytes"):
        rc5.encrypt_cbc(b"hello", b"short")


def test_decrypt_cbc_invalid_iv(rc5: RC5):
    with pytest.raises(ValueError, match="IV must be 16 bytes"):
        rc5.decrypt_cbc(b"1234567890abcdef", b"short")


def test_decrypt_cbc_invalid_ciphertext_length(rc5: RC5):
    iv = b"1234567890abcdef"
    with pytest.raises(ValueError, match="Ciphertext length must be multiple of block size"):
        rc5.decrypt_cbc(b"12345", iv)


def test_key_from_password_returns_8_bytes():
    key = RC5.key_from_password("mypassword")
    assert isinstance(key, bytes)
    assert len(key) == 8


def test_from_password():
    cipher = RC5.from_password("mypassword")
    assert isinstance(cipher, RC5)
    assert len(cipher.key) == 8


def test_generate_iv_bytes():
    iv = RC5.generate_iv_bytes(16)
    assert isinstance(iv, bytes)
    assert len(iv) == 16


def test_encrypt_file_and_decrypt_file(tmp_path: Path, rc5: RC5):
    input_file = tmp_path / "input.txt"
    encrypted_file = tmp_path / "encrypted.bin"
    decrypted_file = tmp_path / "decrypted.txt"

    original_data = b"Secret file content for RC5 test"
    input_file.write_bytes(original_data)

    def fake_iv_generator(n: int) -> bytes:
        assert n == rc5.block_bytes
        return b"1234567890abcdef"

    rc5.encrypt_file(str(input_file), str(encrypted_file), fake_iv_generator)
    assert encrypted_file.exists()

    encrypted_data = encrypted_file.read_bytes()
    assert len(encrypted_data) > rc5.block_bytes  # IV + ciphertext

    rc5.decrypt_file(str(encrypted_file), str(decrypted_file))
    assert decrypted_file.exists()
    assert decrypted_file.read_bytes() == original_data


def test_encrypt_file_invalid_iv_generator_length(tmp_path: Path, rc5: RC5):
    input_file = tmp_path / "input.txt"
    encrypted_file = tmp_path / "encrypted.bin"

    input_file.write_bytes(b"hello")

    def bad_iv_generator(_: int) -> bytes:
        return b"short"

    with pytest.raises(ValueError, match="iv_generator_func must return 16 bytes"):
        rc5.encrypt_file(str(input_file), str(encrypted_file), bad_iv_generator)


def test_decrypt_file_too_short(tmp_path: Path, rc5: RC5):
    encrypted_file = tmp_path / "encrypted.bin"
    output_file = tmp_path / "output.txt"

    encrypted_file.write_bytes(b"short")

    with pytest.raises(ValueError, match="Encrypted file is too short"):
        rc5.decrypt_file(str(encrypted_file), str(output_file))


def test_decrypt_file_invalid_length(tmp_path: Path, rc5: RC5):
    encrypted_file = tmp_path / "encrypted.bin"
    output_file = tmp_path / "output.txt"

    # 16 bytes encrypted_iv + 5 bytes invalid ciphertext
    encrypted_file.write_bytes(b"1" * 16 + b"12345")

    with pytest.raises(ValueError, match="Invalid encrypted file length"):
        rc5.decrypt_file(str(encrypted_file), str(output_file))