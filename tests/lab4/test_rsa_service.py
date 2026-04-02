from pathlib import Path

import pytest
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey

from app.domain.lab4.rsa import RSAKeyPair
from app.services.lab4.rsa_service import (
    RSAOperationResult,
    RSAService,
    RSATimingResult,
)


@pytest.fixture
def service() -> RSAService:
    return RSAService()


@pytest.fixture
def key_paths(tmp_path: Path) -> tuple[Path, Path]:
    private_key_path = tmp_path / "private_key.pem"
    public_key_path = tmp_path / "public_key.pem"
    return private_key_path, public_key_path


class TestRSAServiceKeyOperations:
    def test_generate_and_save_keys_creates_files(
        self,
        service: RSAService,
        key_paths: tuple[Path, Path],
    ):
        private_key_path, public_key_path = key_paths

        result = service.generate_and_save_keys(
            private_key_path=private_key_path,
            public_key_path=public_key_path,
            key_size=2048,
        )

        assert isinstance(result, RSAOperationResult)
        assert result.success is True
        assert private_key_path.exists()
        assert public_key_path.exists()

    def test_generate_and_save_keys_with_password_creates_files(
        self,
        service: RSAService,
        key_paths: tuple[Path, Path],
    ):
        private_key_path, public_key_path = key_paths

        result = service.generate_and_save_keys(
            private_key_path=private_key_path,
            public_key_path=public_key_path,
            key_size=2048,
            password="secret123",
        )

        assert result.success is True
        assert private_key_path.exists()
        assert public_key_path.exists()

    def test_generate_key_pair_returns_valid_key_pair(self, service: RSAService):
        pair = service.generate_key_pair()

        assert isinstance(pair, RSAKeyPair)
        assert isinstance(pair.private_key, RSAPrivateKey)
        assert isinstance(pair.public_key, RSAPublicKey)

    def test_load_private_key_returns_private_key(
        self,
        service: RSAService,
        key_paths: tuple[Path, Path],
    ):
        private_key_path, public_key_path = key_paths

        service.generate_and_save_keys(
            private_key_path=private_key_path,
            public_key_path=public_key_path,
            password="qwerty",
        )

        private_key = service.load_private_key(
            private_key_path=private_key_path,
            password="qwerty",
        )

        assert isinstance(private_key, RSAPrivateKey)

    def test_load_public_key_returns_public_key(
        self,
        service: RSAService,
        key_paths: tuple[Path, Path],
    ):
        private_key_path, public_key_path = key_paths

        service.generate_and_save_keys(
            private_key_path=private_key_path,
            public_key_path=public_key_path,
        )

        public_key = service.load_public_key(public_key_path=public_key_path)

        assert isinstance(public_key, RSAPublicKey)


class TestRSAServiceTextOperations:
    def test_encrypt_and_decrypt_text_roundtrip(
        self,
        service: RSAService,
        key_paths: tuple[Path, Path],
    ):
        private_key_path, public_key_path = key_paths
        original_text = "Hello RSA service test!"

        service.generate_and_save_keys(
            private_key_path=private_key_path,
            public_key_path=public_key_path,
            password="1234",
        )

        encrypted_data = service.encrypt_text(
            text=original_text,
            public_key_path=public_key_path,
        )
        decrypted_text = service.decrypt_text(
            encrypted_data=encrypted_data,
            private_key_path=private_key_path,
            password="1234",
        )

        assert isinstance(encrypted_data, bytes)
        assert decrypted_text == original_text

    def test_encrypt_text_returns_bytes(
        self,
        service: RSAService,
        key_paths: tuple[Path, Path],
    ):
        private_key_path, public_key_path = key_paths

        service.generate_and_save_keys(
            private_key_path=private_key_path,
            public_key_path=public_key_path,
        )

        encrypted_data = service.encrypt_text(
            text="test text",
            public_key_path=public_key_path,
        )

        assert isinstance(encrypted_data, bytes)
        assert len(encrypted_data) > 0


class TestRSAServiceFileOperations:
    def test_encrypt_and_decrypt_file_roundtrip(
        self,
        service: RSAService,
        key_paths: tuple[Path, Path],
        tmp_path: Path,
    ):
        private_key_path, public_key_path = key_paths

        input_path = tmp_path / "input.txt"
        encrypted_path = tmp_path / "input.txt.enc"
        decrypted_path = tmp_path / "decrypted.txt"

        original_data = b"RSA service file test " * 200
        input_path.write_bytes(original_data)

        service.generate_and_save_keys(
            private_key_path=private_key_path,
            public_key_path=public_key_path,
            password="pass123",
        )

        encrypt_result = service.encrypt_file(
            input_path=input_path,
            output_path=encrypted_path,
            public_key_path=public_key_path,
        )
        decrypt_result = service.decrypt_file(
            input_path=encrypted_path,
            output_path=decrypted_path,
            private_key_path=private_key_path,
            password="pass123",
        )

        assert encrypt_result.success is True
        assert decrypt_result.success is True
        assert encrypted_path.exists()
        assert decrypted_path.exists()
        assert decrypted_path.read_bytes() == original_data

    def test_encrypt_file_returns_success_result(
        self,
        service: RSAService,
        key_paths: tuple[Path, Path],
        tmp_path: Path,
    ):
        private_key_path, public_key_path = key_paths
        input_path = tmp_path / "plain.bin"
        output_path = tmp_path / "plain.bin.enc"

        input_path.write_bytes(b"test content")

        service.generate_and_save_keys(
            private_key_path=private_key_path,
            public_key_path=public_key_path,
        )

        result = service.encrypt_file(
            input_path=input_path,
            output_path=output_path,
            public_key_path=public_key_path,
        )

        assert isinstance(result, RSAOperationResult)
        assert result.success is True
        assert output_path.exists()

    def test_decrypt_file_returns_success_result(
        self,
        service: RSAService,
        key_paths: tuple[Path, Path],
        tmp_path: Path,
    ):
        private_key_path, public_key_path = key_paths
        input_path = tmp_path / "plain.txt"
        encrypted_path = tmp_path / "plain.txt.enc"
        decrypted_path = tmp_path / "plain_decrypted.txt"

        input_path.write_bytes(b"content for decrypt test")

        service.generate_and_save_keys(
            private_key_path=private_key_path,
            public_key_path=public_key_path,
            password="testpass",
        )

        service.encrypt_file(
            input_path=input_path,
            output_path=encrypted_path,
            public_key_path=public_key_path,
        )

        result = service.decrypt_file(
            input_path=encrypted_path,
            output_path=decrypted_path,
            private_key_path=private_key_path,
            password="testpass",
        )

        assert isinstance(result, RSAOperationResult)
        assert result.success is True
        assert decrypted_path.exists()


class TestRSAServiceTiming:
    def test_measure_encrypt_file_time_returns_timing_result(
        self,
        service: RSAService,
        key_paths: tuple[Path, Path],
        tmp_path: Path,
    ):
        private_key_path, public_key_path = key_paths
        input_path = tmp_path / "time_input.txt"
        encrypted_path = tmp_path / "time_input.txt.enc"

        input_path.write_bytes(b"A" * 3000)

        service.generate_and_save_keys(
            private_key_path=private_key_path,
            public_key_path=public_key_path,
        )

        result = service.measure_encrypt_file_time(
            input_path=input_path,
            output_path=encrypted_path,
            public_key_path=public_key_path,
        )

        assert isinstance(result, RSATimingResult)
        assert result.operation == "encrypt"
        assert result.input_path == str(input_path)
        assert result.output_path == str(encrypted_path)
        assert result.elapsed_seconds >= 0
        assert result.file_size_bytes == input_path.stat().st_size
        assert encrypted_path.exists()

    def test_measure_decrypt_file_time_returns_timing_result(
        self,
        service: RSAService,
        key_paths: tuple[Path, Path],
        tmp_path: Path,
    ):
        private_key_path, public_key_path = key_paths
        input_path = tmp_path / "measure.txt"
        encrypted_path = tmp_path / "measure.txt.enc"
        decrypted_path = tmp_path / "measure_decrypted.txt"

        input_path.write_bytes(b"B" * 4000)

        service.generate_and_save_keys(
            private_key_path=private_key_path,
            public_key_path=public_key_path,
            password="abc123",
        )

        service.encrypt_file(
            input_path=input_path,
            output_path=encrypted_path,
            public_key_path=public_key_path,
        )

        result = service.measure_decrypt_file_time(
            input_path=encrypted_path,
            output_path=decrypted_path,
            private_key_path=private_key_path,
            password="abc123",
        )

        assert isinstance(result, RSATimingResult)
        assert result.operation == "decrypt"
        assert result.input_path == str(encrypted_path)
        assert result.output_path == str(decrypted_path)
        assert result.elapsed_seconds >= 0
        assert result.file_size_bytes == decrypted_path.stat().st_size
        assert decrypted_path.exists()


class TestRSAServiceErrors:
    def test_encrypt_file_with_missing_public_key_raises_error(
        self,
        service: RSAService,
        tmp_path: Path,
    ):
        input_path = tmp_path / "input.txt"
        output_path = tmp_path / "input.txt.enc"
        missing_public_key_path = tmp_path / "missing_public.pem"

        input_path.write_bytes(b"data")

        with pytest.raises(Exception):
            service.encrypt_file(
                input_path=input_path,
                output_path=output_path,
                public_key_path=missing_public_key_path,
            )

    def test_decrypt_file_with_missing_private_key_raises_error(
        self,
        service: RSAService,
        tmp_path: Path,
    ):
        input_path = tmp_path / "input.enc"
        output_path = tmp_path / "output.txt"
        missing_private_key_path = tmp_path / "missing_private.pem"

        input_path.write_bytes(b"broken data")

        with pytest.raises(Exception):
            service.decrypt_file(
                input_path=input_path,
                output_path=output_path,
                private_key_path=missing_private_key_path,
                password=None,
            )