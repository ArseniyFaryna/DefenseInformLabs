from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from app.domain.lab4.rsa import (
    RSAFileCipher,
    RSAKeyManager,
    RSAKeyPair,
    RSAPrivateKey,
    RSAPublicKey,
)


@dataclass(slots=True)
class RSAKeyPaths:
    private_key_path: str
    public_key_path: str


@dataclass(slots=True)
class RSAOperationResult:
    success: bool
    message: str


@dataclass(slots=True)
class RSATimingResult:
    operation: str
    input_path: str
    output_path: str
    elapsed_seconds: float
    file_size_bytes: int


class RSAService:
    def __init__(
        self,
        key_manager: Optional[RSAKeyManager] = None,
        file_cipher: Optional[RSAFileCipher] = None,
    ) -> None:
        self.key_manager = key_manager or RSAKeyManager()
        self.file_cipher = file_cipher or RSAFileCipher()

    def generate_and_save_keys(
        self,
        private_key_path: str | Path,
        public_key_path: str | Path,
        key_size: int = 2048,
        password: Optional[str] = None,
    ) -> RSAOperationResult:
        key_pair = self.key_manager.generate_key_pair(key_size=key_size)

        self.key_manager.save_private_key(
            private_key=key_pair.private_key,
            file_path=private_key_path,
            password=password,
        )
        self.key_manager.save_public_key(
            public_key=key_pair.public_key,
            file_path=public_key_path,
        )

        return RSAOperationResult(
            success=True,
            message="RSA keys were successfully generated and saved."
        )

    def generate_key_pair(
        self,
        key_size: int = 2048,
    ) -> RSAKeyPair:
        return self.key_manager.generate_key_pair(key_size=key_size)

    def load_private_key(
        self,
        private_key_path: str | Path,
        password: Optional[str] = None,
    ) -> RSAPrivateKey:
        return self.key_manager.load_private_key(
            file_path=private_key_path,
            password=password,
        )

    def load_public_key(
        self,
        public_key_path: str | Path,
    ) -> RSAPublicKey:
        return self.key_manager.load_public_key(file_path=public_key_path)

    def encrypt_text(
        self,
        text: str,
        public_key_path: str | Path,
        encoding: str = "utf-8",
    ) -> bytes:
        public_key = self.load_public_key(public_key_path)
        data = text.encode(encoding)
        return self.file_cipher.encrypt_bytes(data, public_key)

    def decrypt_text(
        self,
        encrypted_data: bytes,
        private_key_path: str | Path,
        password: Optional[str] = None,
        encoding: str = "utf-8",
    ) -> str:
        private_key = self.load_private_key(private_key_path, password=password)
        decrypted_data = self.file_cipher.decrypt_bytes(encrypted_data, private_key)
        return decrypted_data.decode(encoding)

    def encrypt_file(
        self,
        input_path: str | Path,
        output_path: str | Path,
        public_key_path: str | Path,
    ) -> RSAOperationResult:
        public_key = self.load_public_key(public_key_path)
        self.file_cipher.encrypt_file(
            input_path=input_path,
            output_path=output_path,
            public_key=public_key,
        )

        return RSAOperationResult(
            success=True,
            message=f"File was successfully encrypted: {input_path} -> {output_path}"
        )

    def decrypt_file(
        self,
        input_path: str | Path,
        output_path: str | Path,
        private_key_path: str | Path,
        password: Optional[str] = None,
    ) -> RSAOperationResult:
        private_key = self.load_private_key(
            private_key_path,
            password=password,
        )
        self.file_cipher.decrypt_file(
            input_path=input_path,
            output_path=output_path,
            private_key=private_key,
        )

        return RSAOperationResult(
            success=True,
            message=f"File was successfully decrypted: {input_path} -> {output_path}"
        )

    def measure_encrypt_file_time(
        self,
        input_path: str | Path,
        output_path: str | Path,
        public_key_path: str | Path,
    ) -> RSATimingResult:
        start = time.perf_counter()

        self.encrypt_file(
            input_path=input_path,
            output_path=output_path,
            public_key_path=public_key_path,
        )

        end = time.perf_counter()
        elapsed = end - start

        return RSATimingResult(
            operation="encrypt",
            input_path=str(input_path),
            output_path=str(output_path),
            elapsed_seconds=elapsed,
            file_size_bytes=Path(input_path).stat().st_size,
        )

    def measure_decrypt_file_time(
        self,
        input_path: str | Path,
        output_path: str | Path,
        private_key_path: str | Path,
        password: Optional[str] = None,
    ) -> RSATimingResult:
        start = time.perf_counter()

        self.decrypt_file(
            input_path=input_path,
            output_path=output_path,
            private_key_path=private_key_path,
            password=password,
        )

        end = time.perf_counter()
        elapsed = end - start

        return RSATimingResult(
            operation="decrypt",
            input_path=str(input_path),
            output_path=str(output_path),
            elapsed_seconds=elapsed,
            file_size_bytes=Path(output_path).stat().st_size if Path(output_path).exists() else 0,
        )