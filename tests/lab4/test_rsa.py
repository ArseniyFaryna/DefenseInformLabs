from pathlib import Path

import pytest
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey

from app.domain.lab4.rsa import (
    DEFAULT_HASH_ALGORITHM,
    RSADecryptionError,
    RSAEncryptionError,
    RSAFileCipher,
    RSAKeyLoadError,
    RSAKeyManager,
    RSAKeyPair,
)


@pytest.fixture
def key_pair() -> RSAKeyPair:
    return RSAKeyManager.generate_key_pair()


@pytest.fixture
def cipher() -> RSAFileCipher:
    return RSAFileCipher()


class TestRSAKeyManager:
    def test_generate_key_pair_returns_valid_pair(self):
        pair = RSAKeyManager.generate_key_pair()

        assert isinstance(pair, RSAKeyPair)
        assert isinstance(pair.private_key, RSAPrivateKey)
        assert isinstance(pair.public_key, RSAPublicKey)
        assert pair.private_key.key_size == 2048
        assert pair.public_key.key_size == 2048

    def test_generate_key_pair_with_small_key_size_raises_value_error(self):
        with pytest.raises(ValueError, match="bigger than 2048"):
            RSAKeyManager.generate_key_pair(key_size=1024)

    def test_save_and_load_private_key_without_password(self, tmp_path: Path, key_pair: RSAKeyPair):
        private_key_path = tmp_path / "private_key.pem"

        RSAKeyManager.save_private_key(
            private_key=key_pair.private_key,
            file_path=private_key_path,
            password=None,
        )

        loaded_private_key = RSAKeyManager.load_private_key(
            file_path=private_key_path,
            password=None,
        )

        assert isinstance(loaded_private_key, RSAPrivateKey)
        assert loaded_private_key.private_numbers() == key_pair.private_key.private_numbers()

    def test_save_and_load_private_key_with_password(self, tmp_path: Path, key_pair: RSAKeyPair):
        private_key_path = tmp_path / "private_key_protected.pem"
        password = "secret123"

        RSAKeyManager.save_private_key(
            private_key=key_pair.private_key,
            file_path=private_key_path,
            password=password,
        )

        loaded_private_key = RSAKeyManager.load_private_key(
            file_path=private_key_path,
            password=password,
        )

        assert isinstance(loaded_private_key, RSAPrivateKey)
        assert loaded_private_key.private_numbers() == key_pair.private_key.private_numbers()

    def test_load_private_key_with_wrong_password_raises_error(self, tmp_path: Path, key_pair: RSAKeyPair):
        private_key_path = tmp_path / "private_key_protected.pem"

        RSAKeyManager.save_private_key(
            private_key=key_pair.private_key,
            file_path=private_key_path,
            password="correct_password",
        )

        with pytest.raises(RSAKeyLoadError, match="Failed to load private key"):
            RSAKeyManager.load_private_key(
                file_path=private_key_path,
                password="wrong_password",
            )

    def test_save_and_load_public_key(self, tmp_path: Path, key_pair: RSAKeyPair):
        public_key_path = tmp_path / "public_key.pem"

        RSAKeyManager.save_public_key(
            public_key=key_pair.public_key,
            file_path=public_key_path,
        )

        loaded_public_key = RSAKeyManager.load_public_key(public_key_path)

        assert isinstance(loaded_public_key, RSAPublicKey)
        assert loaded_public_key.public_numbers() == key_pair.public_key.public_numbers()

    def test_load_public_key_from_missing_file_raises_error(self, tmp_path: Path):
        missing_path = tmp_path / "missing_public.pem"

        with pytest.raises(RSAKeyLoadError, match="Failed to load public key"):
            RSAKeyManager.load_public_key(missing_path)

    def test_load_private_key_from_missing_file_raises_error(self, tmp_path: Path):
        missing_path = tmp_path / "missing_private.pem"

        with pytest.raises(RSAKeyLoadError, match="Failed to load private key"):
            RSAKeyManager.load_private_key(missing_path, password=None)


class TestRSAFileCipherBytes:
    def test_encrypt_and_decrypt_bytes_roundtrip(self, cipher: RSAFileCipher, key_pair: RSAKeyPair):
        data = b"Hello RSA! " * 20

        encrypted = cipher.encrypt_bytes(data, key_pair.public_key)
        decrypted = cipher.decrypt_bytes(encrypted, key_pair.private_key)

        assert encrypted != data
        assert decrypted == data

    def test_encrypt_bytes_with_none_raises_error(self, cipher: RSAFileCipher, key_pair: RSAKeyPair):
        with pytest.raises(RSAEncryptionError, match="data cannot be None"):
            cipher.encrypt_bytes(None, key_pair.public_key)  # type: ignore[arg-type]

    def test_decrypt_bytes_with_invalid_short_payload_raises_error(self, cipher: RSAFileCipher, key_pair: RSAKeyPair):
        with pytest.raises(RSADecryptionError, match="Invalid encrypted data"):
            cipher.decrypt_bytes(b"123", key_pair.private_key)

    def test_decrypt_bytes_with_invalid_block_size_raises_error(self, cipher: RSAFileCipher, key_pair: RSAKeyPair):
        invalid_data = (10).to_bytes(8, byteorder="big") + b"broken_payload"

        with pytest.raises(RSADecryptionError, match="multiple of encrypted_block_size"):
            cipher.decrypt_bytes(invalid_data, key_pair.private_key)

    def test_encrypt_and_decrypt_empty_bytes(self, cipher: RSAFileCipher, key_pair: RSAKeyPair):
        data = b""

        encrypted = cipher.encrypt_bytes(data, key_pair.public_key)
        decrypted = cipher.decrypt_bytes(encrypted, key_pair.private_key)

        assert encrypted == (0).to_bytes(8, byteorder="big")
        assert decrypted == b""


class TestRSAFileCipherChunks:
    def test_get_max_plaintext_chunk_size_returns_expected_value(self, cipher: RSAFileCipher, key_pair: RSAKeyPair):
        key_size_bytes = key_pair.public_key.key_size // 8
        hash_len = DEFAULT_HASH_ALGORITHM().digest_size
        expected = key_size_bytes - 2 * hash_len - 2

        assert cipher.get_max_plaintext_chunk_size(key_pair.public_key) == expected

    def test_get_encrypted_block_size_returns_key_size_in_bytes(self, cipher: RSAFileCipher, key_pair: RSAKeyPair):
        expected = key_pair.public_key.key_size // 8

        assert cipher.get_encrypted_block_size(key_pair.public_key) == expected

    def test_encrypt_chunk_and_decrypt_chunk_roundtrip(self, cipher: RSAFileCipher, key_pair: RSAKeyPair):
        chunk = b"test chunk"

        encrypted_chunk = cipher.encrypt_chunk(chunk, key_pair.public_key)
        decrypted_chunk = cipher.decrypt_chunk(encrypted_chunk, key_pair.private_key)

        assert encrypted_chunk != chunk
        assert decrypted_chunk == chunk


class TestRSAFileCipherFiles:
    def test_encrypt_and_decrypt_file_roundtrip(self, tmp_path: Path, cipher: RSAFileCipher, key_pair: RSAKeyPair):
        input_path = tmp_path / "input.txt"
        encrypted_path = tmp_path / "input.txt.enc"
        decrypted_path = tmp_path / "input_decrypted.txt"

        original_data = b"A" * 5000 + b" RSA file test " + b"B" * 3000
        input_path.write_bytes(original_data)

        cipher.encrypt_file(input_path, encrypted_path, key_pair.public_key)
        cipher.decrypt_file(encrypted_path, decrypted_path, key_pair.private_key)

        assert encrypted_path.exists()
        assert decrypted_path.exists()
        assert decrypted_path.read_bytes() == original_data

    def test_encrypt_file_creates_output_file(self, tmp_path: Path, cipher: RSAFileCipher, key_pair: RSAKeyPair):
        input_path = tmp_path / "plain.bin"
        output_path = tmp_path / "encrypted.bin"

        input_path.write_bytes(b"content for encryption")

        cipher.encrypt_file(input_path, output_path, key_pair.public_key)

        assert output_path.exists()
        assert output_path.stat().st_size > 8

    def test_decrypt_file_with_corrupted_header_raises_error(self, tmp_path: Path, cipher: RSAFileCipher, key_pair: RSAKeyPair):
        encrypted_path = tmp_path / "broken.enc"
        output_path = tmp_path / "output.txt"

        encrypted_path.write_bytes(b"1234")

        with pytest.raises(RSADecryptionError, match="Mistake of decryption of file"):
            cipher.decrypt_file(encrypted_path, output_path, key_pair.private_key)

    def test_decrypt_file_with_incomplete_block_raises_error(self, tmp_path: Path, cipher: RSAFileCipher, key_pair: RSAKeyPair):
        encrypted_path = tmp_path / "broken_block.enc"
        output_path = tmp_path / "output.txt"

        encrypted_path.write_bytes((100).to_bytes(8, byteorder="big") + b"not_full_block")

        with pytest.raises(RSADecryptionError, match="Mistake of decryption of file"):
            cipher.decrypt_file(encrypted_path, output_path, key_pair.private_key)
