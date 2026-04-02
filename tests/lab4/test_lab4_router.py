from io import BytesIO
from pathlib import Path
import zipfile

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.lab4 import router as lab4_router_module
from app.api.lab4.router import router


@pytest.fixture
def app():
    app = FastAPI()
    app.include_router(router, prefix="/api/lab4")
    return app


@pytest.fixture
def client(app):
    return TestClient(app)


@pytest.fixture
def temp_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(lab4_router_module, "BASE_TEMP_DIR", tmp_path)
    return tmp_path


class DummyRSAService:
    def generate_and_save_keys(self, private_key_path, public_key_path, key_size=2048, password=None):
        Path(private_key_path).write_text("PRIVATE KEY")
        Path(public_key_path).write_text("PUBLIC KEY")

    def encrypt_file(self, input_path, output_path, public_key_path):
        Path(output_path).write_bytes(b"encrypted-content")

    def decrypt_file(self, input_path, output_path, private_key_path, password=None):
        Path(output_path).write_bytes(b"decrypted-content")


class DummyRC5Service:
    @staticmethod
    def encrypt_file(password, input_path, output_path):
        Path(output_path).write_bytes(b"rc5-encrypted")


@pytest.fixture
def mock_services(monkeypatch):
    monkeypatch.setattr(lab4_router_module, "rsa_service", DummyRSAService())
    monkeypatch.setattr(lab4_router_module, "Lab3Service", DummyRC5Service)


class TestGenerateKeysEndpoint:
    def test_generate_keys_returns_zip(self, client, temp_dir, mock_services):
        response = client.post(
            "/api/lab4/generate-keys",
            data={"key_size": "2048", "password": "secret"},
        )

        assert response.status_code == 200
        assert response.headers["content-type"] in ("application/zip", "application/x-zip-compressed")

        zip_bytes = BytesIO(response.content)
        with zipfile.ZipFile(zip_bytes, "r") as zip_file:
            names = zip_file.namelist()
            assert "private_key.pem" in names
            assert "public_key.pem" in names

    def test_generate_keys_returns_500_on_exception(self, client, temp_dir, monkeypatch):
        class FailingRSAService:
            def generate_and_save_keys(self, *args, **kwargs):
                raise Exception("generation failed")

        monkeypatch.setattr(lab4_router_module, "rsa_service", FailingRSAService())

        response = client.post(
            "/api/lab4/generate-keys",
            data={"key_size": "2048"},
        )

        assert response.status_code == 500
        assert response.json()["detail"] == "generation failed"


class TestEncryptEndpoint:
    def test_encrypt_returns_encrypted_file(self, client, temp_dir, mock_services):
        files = {
            "file": ("plain.txt", b"hello world"),
            "public_key": ("public_key.pem", b"PUBLIC KEY DATA"),
        }

        response = client.post("/api/lab4/encrypt", files=files)

        assert response.status_code == 200
        assert response.content == b"encrypted-content"
        assert "plain.txt.enc" in response.headers.get("content-disposition", "")

    def test_encrypt_returns_404_if_output_not_created(self, client, temp_dir, monkeypatch):
        class RSAServiceNoOutput:
            def encrypt_file(self, input_path, output_path, public_key_path):
                pass

        monkeypatch.setattr(lab4_router_module, "rsa_service", RSAServiceNoOutput())

        files = {
            "file": ("plain.txt", b"hello world"),
            "public_key": ("public_key.pem", b"PUBLIC KEY DATA"),
        }

        response = client.post("/api/lab4/encrypt", files=files)

        assert response.status_code == 404
        assert "Encrypted file was not created" in response.json()["detail"]

    def test_encrypt_returns_400_on_value_error(self, client, temp_dir, monkeypatch):
        class RSAServiceValueError:
            def encrypt_file(self, input_path, output_path, public_key_path):
                raise ValueError("bad input")

        monkeypatch.setattr(lab4_router_module, "rsa_service", RSAServiceValueError())

        files = {
            "file": ("plain.txt", b"hello world"),
            "public_key": ("public_key.pem", b"PUBLIC KEY DATA"),
        }

        response = client.post("/api/lab4/encrypt", files=files)

        assert response.status_code == 400
        assert response.json()["detail"] == "bad input"


class TestDecryptEndpoint:
    def test_decrypt_returns_decrypted_file(self, client, temp_dir, mock_services):
        files = {
            "file": ("plain.txt.enc", b"encrypted-data"),
            "private_key": ("private_key.pem", b"PRIVATE KEY DATA"),
        }

        response = client.post(
            "/api/lab4/decrypt",
            files=files,
            data={"password": "secret"},
        )

        assert response.status_code == 200
        assert response.content == b"decrypted-content"
        assert 'filename="plain.txt"' in response.headers.get("content-disposition", "")

    def test_decrypt_non_enc_file_gets_dec_suffix(self, client, temp_dir, mock_services):
        files = {
            "file": ("cipher.bin", b"encrypted-data"),
            "private_key": ("private_key.pem", b"PRIVATE KEY DATA"),
        }

        response = client.post("/api/lab4/decrypt", files=files)

        assert response.status_code == 200
        assert 'filename="cipher.bin.dec"' in response.headers.get("content-disposition", "")

    def test_decrypt_returns_404_if_output_not_created(self, client, temp_dir, monkeypatch):
        class RSAServiceNoOutput:
            def decrypt_file(self, input_path, output_path, private_key_path, password=None):
                pass

        monkeypatch.setattr(lab4_router_module, "rsa_service", RSAServiceNoOutput())

        files = {
            "file": ("plain.txt.enc", b"encrypted-data"),
            "private_key": ("private_key.pem", b"PRIVATE KEY DATA"),
        }

        response = client.post("/api/lab4/decrypt", files=files)

        assert response.status_code == 404
        assert "Decrypted file was not created" in response.json()["detail"]


class TestCompareSpeedEndpoint:

    def test_compare_speed_returns_400_on_value_error(self, client, temp_dir, monkeypatch):
        class RSAServiceValueError:
            def encrypt_file(self, input_path, output_path, public_key_path):
                raise ValueError("bad compare input")

        monkeypatch.setattr(lab4_router_module, "RSAService", lambda: RSAServiceValueError())
        monkeypatch.setattr(lab4_router_module, "Lab3Service", DummyRC5Service)

        files = {
            "file": ("sample.txt", b"1234567890"),
            "public_key": ("public_key.pem", b"PUBLIC KEY DATA"),
        }

        response = client.post(
            "/api/lab4/compare-speed",
            files=files,
            data={"password": "mypassword"},
        )

        assert response.status_code == 400
        assert response.json()["detail"] == "bad compare input"