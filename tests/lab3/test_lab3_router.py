from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.lab3.router import router
import app.api.lab3.router as lab3_router_module

app = FastAPI()
app.include_router(router, prefix="/lab3")
client = TestClient(app)


def test_encrypt_file_success(tmp_path, monkeypatch):
    monkeypatch.setattr(lab3_router_module, "BASE_TEMP_DIR", tmp_path)

    def fake_encrypt_file(password: str, input_path: str, output_path: str):
        assert password == "secret123"
        assert Path(input_path).exists()
        Path(output_path).write_bytes(b"encrypted-content")

    monkeypatch.setattr(
        lab3_router_module.Lab3Service,
        "encrypt_file",
        staticmethod(fake_encrypt_file),
    )

    response = client.post(
        "/lab3/encrypt",
        files={"file": ("hello.txt", b"hello world", "text/plain")},
        data={"password": "secret123"},
    )

    assert response.status_code == 200
    assert response.content == b"encrypted-content"
    assert response.headers["content-type"] == "application/octet-stream"
    assert "hello.txt.enc" in response.headers.get("content-disposition", "")


def test_encrypt_file_value_error_returns_400(tmp_path, monkeypatch):
    monkeypatch.setattr(lab3_router_module, "BASE_TEMP_DIR", tmp_path)

    def fake_encrypt_file(password: str, input_path: str, output_path: str):
        raise ValueError("Invalid password")

    monkeypatch.setattr(
        lab3_router_module.Lab3Service,
        "encrypt_file",
        staticmethod(fake_encrypt_file),
    )

    response = client.post(
        "/lab3/encrypt",
        files={"file": ("hello.txt", b"hello world", "text/plain")},
        data={"password": "bad"},
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid password"}


def test_encrypt_file_not_found_returns_404(tmp_path, monkeypatch):
    monkeypatch.setattr(lab3_router_module, "BASE_TEMP_DIR", tmp_path)

    def fake_encrypt_file(password: str, input_path: str, output_path: str):
        raise FileNotFoundError("Input file not found")

    monkeypatch.setattr(
        lab3_router_module.Lab3Service,
        "encrypt_file",
        staticmethod(fake_encrypt_file),
    )

    response = client.post(
        "/lab3/encrypt",
        files={"file": ("hello.txt", b"hello world", "text/plain")},
        data={"password": "secret123"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Input file not found"}


def test_encrypt_file_unexpected_error_returns_500(tmp_path, monkeypatch):
    monkeypatch.setattr(lab3_router_module, "BASE_TEMP_DIR", tmp_path)

    def fake_encrypt_file(password: str, input_path: str, output_path: str):
        raise RuntimeError("Something went wrong")

    monkeypatch.setattr(
        lab3_router_module.Lab3Service,
        "encrypt_file",
        staticmethod(fake_encrypt_file),
    )

    response = client.post(
        "/lab3/encrypt",
        files={"file": ("hello.txt", b"hello world", "text/plain")},
        data={"password": "secret123"},
    )

    assert response.status_code == 500
    assert response.json() == {"detail": "Encryption failed: Something went wrong"}


def test_encrypt_file_output_not_created_returns_404(tmp_path, monkeypatch):
    monkeypatch.setattr(lab3_router_module, "BASE_TEMP_DIR", tmp_path)

    def fake_encrypt_file(password: str, input_path: str, output_path: str):
        pass

    monkeypatch.setattr(
        lab3_router_module.Lab3Service,
        "encrypt_file",
        staticmethod(fake_encrypt_file),
    )

    response = client.post(
        "/lab3/encrypt",
        files={"file": ("hello.txt", b"hello world", "text/plain")},
        data={"password": "secret123"},
    )

    assert response.status_code == 404
    assert "Encrypted file was not created" in response.json()["detail"]


def test_decrypt_file_success_with_enc_name(tmp_path, monkeypatch):
    monkeypatch.setattr(lab3_router_module, "BASE_TEMP_DIR", tmp_path)

    def fake_decrypt_file(password: str, input_path: str, output_path: str):
        assert password == "secret123"
        assert Path(input_path).exists()
        Path(output_path).write_bytes(b"decrypted-content")

    monkeypatch.setattr(
        lab3_router_module.Lab3Service,
        "decrypt_file",
        staticmethod(fake_decrypt_file),
    )

    response = client.post(
        "/lab3/decrypt",
        files={"file": ("hello.txt.enc", b"encrypted bytes", "application/octet-stream")},
        data={"password": "secret123"},
    )

    assert response.status_code == 200
    assert response.content == b"decrypted-content"
    assert response.headers["content-type"] == "application/octet-stream"
    assert 'filename="hello.txt"' in response.headers.get("content-disposition", "")


def test_decrypt_file_success_without_enc_name(tmp_path, monkeypatch):
    monkeypatch.setattr(lab3_router_module, "BASE_TEMP_DIR", tmp_path)

    def fake_decrypt_file(password: str, input_path: str, output_path: str):
        Path(output_path).write_bytes(b"decrypted-content")

    monkeypatch.setattr(
        lab3_router_module.Lab3Service,
        "decrypt_file",
        staticmethod(fake_decrypt_file),
    )

    response = client.post(
        "/lab3/decrypt",
        files={"file": ("hello.bin", b"encrypted bytes", "application/octet-stream")},
        data={"password": "secret123"},
    )

    assert response.status_code == 200
    assert response.content == b"decrypted-content"
    assert 'filename="hello.bin.dec"' in response.headers.get("content-disposition", "")


def test_decrypt_file_empty_output_name_becomes_default(tmp_path, monkeypatch):
    monkeypatch.setattr(lab3_router_module, "BASE_TEMP_DIR", tmp_path)

    def fake_decrypt_file(password: str, input_path: str, output_path: str):
        Path(output_path).write_bytes(b"decrypted-content")

    monkeypatch.setattr(
        lab3_router_module.Lab3Service,
        "decrypt_file",
        staticmethod(fake_decrypt_file),
    )

    response = client.post(
        "/lab3/decrypt",
        files={"file": (".enc", b"encrypted bytes", "application/octet-stream")},
        data={"password": "secret123"},
    )

    assert response.status_code == 200
    assert response.content == b"decrypted-content"
    assert 'filename="decrypted_file"' in response.headers.get("content-disposition", "")


def test_decrypt_file_value_error_returns_400(tmp_path, monkeypatch):
    monkeypatch.setattr(lab3_router_module, "BASE_TEMP_DIR", tmp_path)

    def fake_decrypt_file(password: str, input_path: str, output_path: str):
        raise ValueError("Invalid padding")

    monkeypatch.setattr(
        lab3_router_module.Lab3Service,
        "decrypt_file",
        staticmethod(fake_decrypt_file),
    )

    response = client.post(
        "/lab3/decrypt",
        files={"file": ("hello.txt.enc", b"encrypted bytes", "application/octet-stream")},
        data={"password": "wrong"},
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid padding"}


def test_decrypt_file_not_found_returns_404(tmp_path, monkeypatch):
    monkeypatch.setattr(lab3_router_module, "BASE_TEMP_DIR", tmp_path)

    def fake_decrypt_file(password: str, input_path: str, output_path: str):
        raise FileNotFoundError("Encrypted file not found")

    monkeypatch.setattr(
        lab3_router_module.Lab3Service,
        "decrypt_file",
        staticmethod(fake_decrypt_file),
    )

    response = client.post(
        "/lab3/decrypt",
        files={"file": ("hello.txt.enc", b"encrypted bytes", "application/octet-stream")},
        data={"password": "secret123"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Encrypted file not found"}


def test_decrypt_file_unexpected_error_returns_500(tmp_path, monkeypatch):
    monkeypatch.setattr(lab3_router_module, "BASE_TEMP_DIR", tmp_path)

    def fake_decrypt_file(password: str, input_path: str, output_path: str):
        raise RuntimeError("Something went wrong")

    monkeypatch.setattr(
        lab3_router_module.Lab3Service,
        "decrypt_file",
        staticmethod(fake_decrypt_file),
    )

    response = client.post(
        "/lab3/decrypt",
        files={"file": ("hello.txt.enc", b"encrypted bytes", "application/octet-stream")},
        data={"password": "secret123"},
    )

    assert response.status_code == 500
    assert response.json() == {"detail": "Decryption failed: Something went wrong"}


def test_decrypt_file_output_not_created_returns_404(tmp_path, monkeypatch):
    monkeypatch.setattr(lab3_router_module, "BASE_TEMP_DIR", tmp_path)

    def fake_decrypt_file(password: str, input_path: str, output_path: str):
        pass

    monkeypatch.setattr(
        lab3_router_module.Lab3Service,
        "decrypt_file",
        staticmethod(fake_decrypt_file),
    )

    response = client.post(
        "/lab3/decrypt",
        files={"file": ("hello.txt.enc", b"encrypted bytes", "application/octet-stream")},
        data={"password": "secret123"},
    )

    assert response.status_code == 404
    assert "Decrypted file was not created" in response.json()["detail"]