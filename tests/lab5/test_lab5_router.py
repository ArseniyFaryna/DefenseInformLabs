from io import BytesIO
from unittest.mock import patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.lab5.router import router


app = FastAPI()
app.include_router(router, prefix="/lab5")
client = TestClient(app)


class TestLab5Router:
    @patch("app.api.lab5.router.lab5_service")
    def test_generate_keys_error(self, mock_service):
        mock_service.generate_keys.side_effect = Exception("generation failed")

        response = client.post(
            "/lab5/keys/generate",
            data={
                "key_size": "2048",
                "password": "secret",
            },
        )

        assert response.status_code == 400
        assert "Помилка генерації ключів" in response.json()["detail"]
        assert "generation failed" in response.json()["detail"]

    @patch("app.api.lab5.router.lab5_service")
    def test_sign_text_error(self, mock_service):
        mock_service.sign_text.side_effect = Exception("sign text failed")

        files = {
            "private_key": ("private_key.pem", b"PRIVATE KEY CONTENT", "application/octet-stream"),
        }
        data = {
            "text": "hello world",
            "password": "secret",
        }

        response = client.post("/lab5/sign/text", data=data, files=files)

        assert response.status_code == 400
        assert "Помилка підпису тексту" in response.json()["detail"]
        assert "sign text failed" in response.json()["detail"]

    @patch("app.api.lab5.router.lab5_service")
    def test_verify_text_success_valid(self, mock_service):
        mock_service.verify_text.return_value = {
            "is_valid": True,
            "message": "Signature verified successfully",
        }

        files = {
            "signature": ("signature.txt", b"abcdef123456", "text/plain"),
            "public_key": ("public_key.pem", b"PUBLIC KEY CONTENT", "application/octet-stream"),
        }
        data = {
            "text": "hello world",
        }

        response = client.post("/lab5/verify/text", data=data, files=files)

        assert response.status_code == 200
        assert response.json() == {
            "is_valid": True,
            "message": "Signature verified successfully",
        }

        mock_service.verify_text.assert_called_once()
        kwargs = mock_service.verify_text.call_args.kwargs
        assert kwargs["text"] == "hello world"
        assert kwargs["signature_hex"] == "abcdef123456"
        assert kwargs["public_key_path"].endswith("public_key.pem")

    @patch("app.api.lab5.router.lab5_service")
    def test_verify_text_success_invalid(self, mock_service):
        mock_service.verify_text.return_value = {
            "is_valid": False,
            "message": "Signature is invalid",
        }

        files = {
            "signature": ("signature.txt", b"bad_signature", "text/plain"),
            "public_key": ("public_key.pem", b"PUBLIC KEY CONTENT", "application/octet-stream"),
        }
        data = {
            "text": "hello world",
        }

        response = client.post("/lab5/verify/text", data=data, files=files)

        assert response.status_code == 200
        assert response.json() == {
            "is_valid": False,
            "message": "Signature is invalid",
        }

    @patch("app.api.lab5.router.lab5_service")
    def test_verify_text_error(self, mock_service):
        mock_service.verify_text.side_effect = Exception("verify text failed")

        files = {
            "signature": ("signature.txt", b"abcdef123456", "text/plain"),
            "public_key": ("public_key.pem", b"PUBLIC KEY CONTENT", "application/octet-stream"),
        }
        data = {
            "text": "hello world",
        }

        response = client.post("/lab5/verify/text", data=data, files=files)

        assert response.status_code == 400
        assert "Помилка перевірки" in response.json()["detail"]
        assert "verify text failed" in response.json()["detail"]


    @patch("app.api.lab5.router.lab5_service")
    def test_sign_file_error(self, mock_service):
        mock_service.sign_file.side_effect = Exception("sign file failed")

        files = {
            "file": ("data.txt", b"some file content", "text/plain"),
            "private_key": ("private_key.pem", b"PRIVATE KEY CONTENT", "application/octet-stream"),
        }
        data = {
            "password": "secret",
        }

        response = client.post("/lab5/sign/file", data=data, files=files)

        assert response.status_code == 400
        assert "Помилка підпису файлу" in response.json()["detail"]
        assert "sign file failed" in response.json()["detail"]

    @patch("app.api.lab5.router.lab5_service")
    def test_verify_file_success_valid(self, mock_service):
        mock_service.verify_file.return_value = {
            "is_valid": True,
            "message": "Signature verified successfully",
        }

        files = {
            "file": ("data.txt", b"some file content", "text/plain"),
            "signature": ("data.txt.sig", b"abcdef123456", "text/plain"),
            "public_key": ("public_key.pem", b"PUBLIC KEY CONTENT", "application/octet-stream"),
        }

        response = client.post("/lab5/verify/file", files=files)

        assert response.status_code == 200
        assert response.json() == {
            "is_valid": True,
            "message": "Signature verified successfully",
        }

        mock_service.verify_file.assert_called_once()
        kwargs = mock_service.verify_file.call_args.kwargs
        assert kwargs["file_path"].endswith("data.txt")
        assert kwargs["public_key_path"].endswith("public_key.pem")
        assert kwargs["signature_hex"] is None
        assert kwargs["signature_file_path"].endswith("signature.sig")

    @patch("app.api.lab5.router.lab5_service")
    def test_verify_file_success_invalid(self, mock_service):
        mock_service.verify_file.return_value = {
            "is_valid": False,
            "message": "Signature is invalid",
        }

        files = {
            "file": ("data.txt", b"some file content", "text/plain"),
            "signature": ("data.txt.sig", b"bad_signature", "text/plain"),
            "public_key": ("public_key.pem", b"PUBLIC KEY CONTENT", "application/octet-stream"),
        }

        response = client.post("/lab5/verify/file", files=files)

        assert response.status_code == 200
        assert response.json() == {
            "is_valid": False,
            "message": "Signature is invalid",
        }

    @patch("app.api.lab5.router.lab5_service")
    def test_verify_file_error(self, mock_service):
        mock_service.verify_file.side_effect = Exception("verify file failed")

        files = {
            "file": ("data.txt", b"some file content", "text/plain"),
            "signature": ("data.txt.sig", b"abcdef123456", "text/plain"),
            "public_key": ("public_key.pem", b"PUBLIC KEY CONTENT", "application/octet-stream"),
        }

        response = client.post("/lab5/verify/file", files=files)

        assert response.status_code == 400
        assert "Помилка перевірки файлу" in response.json()["detail"]
        assert "verify file failed" in response.json()["detail"]