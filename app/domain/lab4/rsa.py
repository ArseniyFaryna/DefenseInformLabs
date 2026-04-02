from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.asymmetric.rsa import (RSAPrivateKey, RSAPublicKey)

DEFAULT_PUBLIC_EXPONENT = 65537
DEFAULT_KEY_SIZE = 2048
DEFAULT_HASH_ALGORITHM = hashes.SHA256

class RSAError(Exception):
    """Базовий виняток доменного шару для RSA."""

class RSAKeyLoadError(RSAError):
    """Помилка завантаження ключа."""


class RSAEncryptionError(RSAError):
    """Помилка шифрування."""


class RSADecryptionError(RSAError):
    """Помилка дешифрування."""

@dataclass(slots=True)
class RSAKeyPair:
    private_key: RSAPrivateKey
    public_key: RSAPublicKey

class RSAKeyManager:

    @staticmethod
    def generate_key_pair(key_size: int = DEFAULT_KEY_SIZE, public_exponent: int = DEFAULT_PUBLIC_EXPONENT) -> RSAKeyPair:
        if key_size < 2048:
            raise ValueError("Length of the key should be bigger than 2048 bits")
        private_key = rsa.generate_private_key(public_exponent=public_exponent, key_size=key_size)
        public_key = private_key.public_key()

        return RSAKeyPair(private_key=private_key, public_key=public_key)

    @staticmethod
    def save_private_key(private_key: RSAPrivateKey, file_path: str | Path, password: Optional[str]) -> None:
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        encryption_algorithm = (serialization.BestAvailableEncryption(password.encode("utf-8")) if password else serialization.NoEncryption())

        pem_data = private_key.private_bytes(encoding=serialization.Encoding.PEM, format=serialization.PrivateFormat.PKCS8, encryption_algorithm=encryption_algorithm)

        path.write_bytes(pem_data)

    @staticmethod
    def save_public_key(public_key: RSAPublicKey, file_path: str | Path) -> None:
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        pem_data = public_key.public_bytes(encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo)

        path.write_bytes(pem_data)

    @staticmethod
    def load_private_key(file_path: str | Path, password: Optional[str]) -> RSAPrivateKey:
        try:
            pem_data = Path(file_path).read_bytes()
            return serialization.load_pem_private_key(
                pem_data, password=password.encode("utf-8") if password else None,
            )
        except Exception as exc:
            raise RSAKeyLoadError(f"Failed to load private key: {exc}")

    @staticmethod
    def load_public_key(file_path: str | Path) -> RSAPublicKey:
        try:
            pem_data = Path(file_path).read_bytes()
            return serialization.load_pem_public_key(pem_data)
        except Exception as exc:
            raise RSAKeyLoadError(f"Failed to load public key: {exc}")

class RSAFileCipher:

    def __init__(self, hash_algorithm_factory=DEFAULT_HASH_ALGORITHM,) -> None:
        self._hash_algorithm_factory = hash_algorithm_factory

    def encrypt_bytes(self, data: bytes, public_key: RSAPublicKey) -> bytes:
        if data is None:
            raise RSAEncryptionError(f"Encryption failed because data cannot be None")

        chunk_size = self.get_max_plaintext_chunk_size(public_key)
        encrypted_chunks: list[bytes] = []

        for start in range(0, len(data), chunk_size):
            chunk = data[start:start + chunk_size]
            encrypted_chunks.append(self.encrypt_chunk(chunk, public_key))

        return len(data).to_bytes(length=8, byteorder="big") + b"".join(encrypted_chunks)

    def decrypt_bytes(self, encrypted_data: bytes, private_key: RSAPrivateKey) -> bytes:
        if encrypted_data is None or len(encrypted_data) < 8:
            raise RSADecryptionError("Invalid encrypted data")

        original_size = int.from_bytes(encrypted_data[:8], byteorder="big")
        payload = encrypted_data[8:]

        encrypted_block_size = self.get_encrypted_block_size(private_key.public_key())

        if len(payload) % encrypted_block_size != 0:
            raise RSADecryptionError("Length isn't a multiple of encrypted_block_size")

        decrypted_chunks: list[bytes] = []

        for start in range(0, len(payload), encrypted_block_size):
            block = payload[start:start + encrypted_block_size]
            decrypted_chunks.append(self.decrypt_chunk(block, private_key))

        decrypted_data = b"".join(decrypted_chunks)
        return decrypted_data[:original_size]

    def encrypt_file(self, input_path: str | Path, output_path: str | Path, public_key: RSAPublicKey) -> None:
        input_file = Path(input_path)
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        file_size = input_file.stat().st_size
        chunk_size = self.get_max_plaintext_chunk_size(public_key)

        try:
            with input_file.open("rb") as fin, output_file.open("wb") as fout:
                fout.write(file_size.to_bytes(8, byteorder="big"))

                while True:
                    chunk = fin.read(chunk_size)
                    if not chunk:
                        break

                    encrypted_chunk = self.encrypt_chunk(chunk, public_key)
                    fout.write(encrypted_chunk)

        except Exception as exc:
            raise RSAEncryptionError(f"Mistake of encryption of file: {exc}") from exc

    def decrypt_file(self, input_path: str | Path, output_path: str | Path, private_key: RSAPrivateKey) -> None:
        input_file = Path(input_path)
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        encrypted_block_size = self.get_encrypted_block_size(private_key.public_key())

        try:
            with input_file.open("rb") as fin, output_file.open("wb") as fout:
                header = fin.read(8)
                if len(header) != 8:
                    raise RSADecryptionError("Encrypted file is corrupted.")

                original_size = int.from_bytes(header, byteorder="big")
                written = 0

                while True:
                    block = fin.read(encrypted_block_size)
                    if not block:
                        break

                    if len(block) != encrypted_block_size:
                        raise RSADecryptionError("Incomplete encrypted block.")

                    decrypted_chunk = self.decrypt_chunk(block, private_key)

                    remaining = original_size - written
                    to_write = decrypted_chunk[:remaining]
                    fout.write(to_write)
                    written += len(to_write)

                    if written >= original_size:
                        break

        except Exception as exc:
            raise RSADecryptionError(f"Mistake of decryption of file: {exc}") from exc

    def get_max_plaintext_chunk_size(self, public_key: RSAPublicKey) -> int:
        key_size_bytes = public_key.key_size // 8
        hash_len = self._hash_algorithm_factory().digest_size
        max_chunk_size = key_size_bytes - 2 * hash_len - 2

        if max_chunk_size <= 0:
            raise RSAEncryptionError("Impossible to decrypt block due to small key length")

        return max_chunk_size


    def get_encrypted_block_size(self, public_key: RSAPublicKey) -> int:
        return public_key.key_size // 8

    def encrypt_chunk(self, chunk: bytes, public_key: RSAPublicKey) -> bytes:
        try:
            return public_key.encrypt(
                chunk,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=self._hash_algorithm_factory()),
                    algorithm=self._hash_algorithm_factory(),
                    label=None,
                ),
            )
        except Exception as exc:
            raise RSAEncryptionError(f"Cannot encrypt file: {exc}") from exc


    def decrypt_chunk(self, chunk: bytes, private_key: RSAPrivateKey) -> bytes:
        try:
            return private_key.decrypt(
                chunk,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=self._hash_algorithm_factory()),
                    algorithm=self._hash_algorithm_factory(),
                    label=None,
                ),
            )
        except Exception as exc:
            raise RSADecryptionError(f"Cannot to decrypt file: {exc}") from exc