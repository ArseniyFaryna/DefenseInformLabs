from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from app.services.lab5.signature_service import Lab5Service


class TestLab5Service:
    @patch("app.services.lab5.signature_service.Lab5Domain")
    def test_generate_keys_success(self, mock_domain_class):
        mock_domain = MagicMock()
        mock_domain.generate_keys.return_value = SimpleNamespace(
            private_key_path="temp/lab5/private_key.pem",
            public_key_path="temp/lab5/public_key.pem",
        )
        mock_domain_class.return_value = mock_domain

        service = Lab5Service()

        result = service.generate_keys(
            private_key_path="temp/lab5/private_key.pem",
            public_key_path="temp/lab5/public_key.pem",
            password="secret",
            key_size=2048,
        )

        mock_domain.generate_keys.assert_called_once_with(
            private_key_path="temp/lab5/private_key.pem",
            public_key_path="temp/lab5/public_key.pem",
            password="secret",
            key_size=2048,
        )

        assert result == {
            "message": "Keys generated successfully",
            "private_key_path": "temp/lab5/private_key.pem",
            "public_key_path": "temp/lab5/public_key.pem",
        }

    @patch("app.services.lab5.signature_service.Lab5Domain")
    def test_sign_text_success(self, mock_domain_class):
        mock_domain = MagicMock()
        mock_domain.sign_text.return_value = SimpleNamespace(
            signature_hex="abcdef123456"
        )
        mock_domain_class.return_value = mock_domain

        service = Lab5Service()

        result = service.sign_text(
            text="hello",
            private_key_path="temp/lab5/private_key.pem",
            password="secret",
            signature_output_path="temp/lab5/text_signature.txt",
        )

        mock_domain.sign_text.assert_called_once_with(
            text="hello",
            private_key_path="temp/lab5/private_key.pem",
            password="secret",
            signature_output_path="temp/lab5/text_signature.txt",
        )

        assert result == {
            "message": "Text signed successfully",
            "signature_hex": "abcdef123456",
        }

    @patch("app.services.lab5.signature_service.Lab5Domain")
    def test_verify_text_valid_signature(self, mock_domain_class):
        mock_domain = MagicMock()
        mock_domain.verify_text.return_value = SimpleNamespace(
            is_valid=True,
            message="Signature verified successfully",
        )
        mock_domain_class.return_value = mock_domain

        service = Lab5Service()

        result = service.verify_text(
            text="hello",
            signature_hex="abcdef123456",
            public_key_path="temp/lab5/public_key.pem",
        )

        mock_domain.verify_text.assert_called_once_with(
            text="hello",
            signature_hex="abcdef123456",
            public_key_path="temp/lab5/public_key.pem",
        )

        assert result == {
            "is_valid": True,
            "message": "Signature verified successfully",
        }

    @patch("app.services.lab5.signature_service.Lab5Domain")
    def test_verify_text_invalid_signature(self, mock_domain_class):
        mock_domain = MagicMock()
        mock_domain.verify_text.return_value = SimpleNamespace(
            is_valid=False,
            message="Signature is invalid",
        )
        mock_domain_class.return_value = mock_domain

        service = Lab5Service()

        result = service.verify_text(
            text="hello",
            signature_hex="bad_signature",
            public_key_path="temp/lab5/public_key.pem",
        )

        mock_domain.verify_text.assert_called_once_with(
            text="hello",
            signature_hex="bad_signature",
            public_key_path="temp/lab5/public_key.pem",
        )

        assert result == {
            "is_valid": False,
            "message": "Signature is invalid",
        }

    @patch("app.services.lab5.signature_service.Lab5Domain")
    def test_sign_file_success(self, mock_domain_class):
        mock_domain = MagicMock()
        mock_domain.sign_file.return_value = SimpleNamespace(
            signature_hex="deadbeef"
        )
        mock_domain_class.return_value = mock_domain

        service = Lab5Service()

        result = service.sign_file(
            file_path="temp/lab5/data.txt",
            private_key_path="temp/lab5/private_key.pem",
            password="secret",
            signature_output_path="temp/lab5/file_signature.txt",
        )

        mock_domain.sign_file.assert_called_once_with(
            file_path="temp/lab5/data.txt",
            private_key_path="temp/lab5/private_key.pem",
            password="secret",
            signature_output_path="temp/lab5/file_signature.txt",
        )

        assert result == {
            "message": "File signed successfully",
            "signature_hex": "deadbeef",
        }

    @patch("app.services.lab5.signature_service.Lab5Domain")
    def test_verify_file_with_signature_hex_success(self, mock_domain_class):
        mock_domain = MagicMock()
        mock_domain.verify_file.return_value = SimpleNamespace(
            is_valid=True,
            message="Signature verified successfully",
        )
        mock_domain_class.return_value = mock_domain

        service = Lab5Service()

        result = service.verify_file(
            file_path="temp/lab5/data.txt",
            public_key_path="temp/lab5/public_key.pem",
            signature_hex="cafebabe",
            signature_file_path=None,
        )

        mock_domain.verify_file.assert_called_once_with(
            file_path="temp/lab5/data.txt",
            public_key_path="temp/lab5/public_key.pem",
            signature_hex="cafebabe",
            signature_file_path=None,
        )

        assert result == {
            "is_valid": True,
            "message": "Signature verified successfully",
        }

    @patch("app.services.lab5.signature_service.Lab5Domain")
    def test_verify_file_with_signature_file_success(self, mock_domain_class):
        mock_domain = MagicMock()
        mock_domain.verify_file.return_value = SimpleNamespace(
            is_valid=True,
            message="Signature verified successfully",
        )
        mock_domain_class.return_value = mock_domain

        service = Lab5Service()

        result = service.verify_file(
            file_path="temp/lab5/data.txt",
            public_key_path="temp/lab5/public_key.pem",
            signature_hex=None,
            signature_file_path="temp/lab5/file_signature.txt",
        )

        mock_domain.verify_file.assert_called_once_with(
            file_path="temp/lab5/data.txt",
            public_key_path="temp/lab5/public_key.pem",
            signature_hex=None,
            signature_file_path="temp/lab5/file_signature.txt",
        )

        assert result == {
            "is_valid": True,
            "message": "Signature verified successfully",
        }

    @patch("app.services.lab5.signature_service.Lab5Domain")
    def test_generate_keys_propagates_exception(self, mock_domain_class):
        mock_domain = MagicMock()
        mock_domain.generate_keys.side_effect = ValueError("generation failed")
        mock_domain_class.return_value = mock_domain

        service = Lab5Service()

        try:
            service.generate_keys(
                private_key_path="temp/lab5/private_key.pem",
                public_key_path="temp/lab5/public_key.pem",
                password="secret",
                key_size=2048,
            )
            assert False, "Expected ValueError to be raised"
        except ValueError as exc:
            assert str(exc) == "generation failed"

    @patch("app.services.lab5.signature_service.Lab5Domain")
    def test_sign_text_propagates_exception(self, mock_domain_class):
        mock_domain = MagicMock()
        mock_domain.sign_text.side_effect = ValueError("sign failed")
        mock_domain_class.return_value = mock_domain

        service = Lab5Service()

        try:
            service.sign_text(
                text="hello",
                private_key_path="temp/lab5/private_key.pem",
                password="secret",
                signature_output_path="temp/lab5/text_signature.txt",
            )
            assert False, "Expected ValueError to be raised"
        except ValueError as exc:
            assert str(exc) == "sign failed"