import pytest
import tempfile
import os
from pathlib import Path
from cryptography.hazmat.primitives import hashes

from app.domain.lab5.signature import Lab5Domain, SignatureResult, KeyPairPaths


@pytest.fixture
def domain():
    return Lab5Domain()


@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def key_paths(domain, temp_dir):
    private_path = os.path.join(temp_dir, "private.pem")
    public_path = os.path.join(temp_dir, "public.pem")
    domain.generate_keys(private_path, public_path)
    return private_path, public_path


@pytest.fixture
def key_paths_with_password(domain, temp_dir):
    private_path = os.path.join(temp_dir, "private_enc.pem")
    public_path = os.path.join(temp_dir, "public_enc.pem")
    domain.generate_keys(private_path, public_path, password="secret123")
    return private_path, public_path


# ── generate_keys ────────────────────────────────────────────────────────────

class TestGenerateKeys:
    def test_returns_key_pair_paths(self, domain, temp_dir):
        private_path = os.path.join(temp_dir, "priv.pem")
        public_path = os.path.join(temp_dir, "pub.pem")
        result = domain.generate_keys(private_path, public_path)
        assert isinstance(result, KeyPairPaths)

    def test_files_are_created(self, domain, temp_dir):
        private_path = os.path.join(temp_dir, "priv.pem")
        public_path = os.path.join(temp_dir, "pub.pem")
        domain.generate_keys(private_path, public_path)
        assert Path(private_path).exists()
        assert Path(public_path).exists()

    def test_private_key_pem_header(self, domain, temp_dir):
        private_path = os.path.join(temp_dir, "priv.pem")
        public_path = os.path.join(temp_dir, "pub.pem")
        domain.generate_keys(private_path, public_path)
        content = Path(private_path).read_text()
        assert "BEGIN PRIVATE KEY" in content

    def test_public_key_pem_header(self, domain, temp_dir):
        private_path = os.path.join(temp_dir, "priv.pem")
        public_path = os.path.join(temp_dir, "pub.pem")
        domain.generate_keys(private_path, public_path)
        content = Path(public_path).read_text()
        assert "BEGIN PUBLIC KEY" in content

    def test_encrypted_private_key_header(self, domain, temp_dir):
        private_path = os.path.join(temp_dir, "priv_enc.pem")
        public_path = os.path.join(temp_dir, "pub_enc.pem")
        domain.generate_keys(private_path, public_path, password="pass")
        content = Path(private_path).read_text()
        assert "ENCRYPTED PRIVATE KEY" in content

    def test_creates_parent_directories(self, domain, temp_dir):
        private_path = os.path.join(temp_dir, "nested", "dir", "priv.pem")
        public_path = os.path.join(temp_dir, "another", "pub.pem")
        domain.generate_keys(private_path, public_path)
        assert Path(private_path).exists()
        assert Path(public_path).exists()

    def test_paths_returned_match_input(self, domain, temp_dir):
        private_path = os.path.join(temp_dir, "priv.pem")
        public_path = os.path.join(temp_dir, "pub.pem")
        result = domain.generate_keys(private_path, public_path)
        assert result.private_key_path == private_path
        assert result.public_key_path == public_path


# ── sign_text / verify_text ──────────────────────────────────────────────────

class TestSignAndVerifyText:
    def test_sign_returns_signature_result(self, domain, key_paths):
        private_path, _ = key_paths
        result = domain.sign_text("hello", private_path)
        assert isinstance(result, SignatureResult)

    def test_signature_hex_is_hex_string(self, domain, key_paths):
        private_path, _ = key_paths
        result = domain.sign_text("hello", private_path)
        bytes.fromhex(result.signature_hex)  # must not raise

    def test_signature_bytes_match_hex(self, domain, key_paths):
        private_path, _ = key_paths
        result = domain.sign_text("hello", private_path)
        assert result.signature_bytes == bytes.fromhex(result.signature_hex)

    def test_verify_valid_signature(self, domain, key_paths):
        private_path, public_path = key_paths
        result = domain.sign_text("hello world", private_path)
        verification = domain.verify_text("hello world", result.signature_hex, public_path)
        assert verification.is_valid is True

    def test_verify_wrong_text_fails(self, domain, key_paths):
        private_path, public_path = key_paths
        result = domain.sign_text("original", private_path)
        verification = domain.verify_text("tampered", result.signature_hex, public_path)
        assert verification.is_valid is False

    def test_verify_invalid_hex_fails(self, domain, key_paths):
        _, public_path = key_paths
        verification = domain.verify_text("hello", "not_valid_hex!!!", public_path)
        assert verification.is_valid is False

    def test_verify_wrong_key_fails(self, domain, key_paths, temp_dir):
        private_path, _ = key_paths
        # generate a second, different key pair
        priv2 = os.path.join(temp_dir, "priv2.pem")
        pub2 = os.path.join(temp_dir, "pub2.pem")
        domain.generate_keys(priv2, pub2)
        result = domain.sign_text("hello", private_path)
        verification = domain.verify_text("hello", result.signature_hex, pub2)
        assert verification.is_valid is False

    def test_sign_with_password(self, domain, key_paths_with_password):
        private_path, public_path = key_paths_with_password
        result = domain.sign_text("secure text", private_path, password="secret123")
        verification = domain.verify_text("secure text", result.signature_hex, public_path)
        assert verification.is_valid is True

    def test_sign_saves_signature_to_file(self, domain, key_paths, temp_dir):
        private_path, _ = key_paths
        sig_path = os.path.join(temp_dir, "sig.hex")
        result = domain.sign_text("hello", private_path, signature_output_path=sig_path)
        saved = Path(sig_path).read_text(encoding="utf-8")
        assert saved == result.signature_hex

    def test_empty_string_can_be_signed(self, domain, key_paths):
        private_path, public_path = key_paths
        result = domain.sign_text("", private_path)
        verification = domain.verify_text("", result.signature_hex, public_path)
        assert verification.is_valid is True

    def test_unicode_text_can_be_signed(self, domain, key_paths):
        private_path, public_path = key_paths
        text = "Привіт світ 🌍"
        result = domain.sign_text(text, private_path)
        verification = domain.verify_text(text, result.signature_hex, public_path)
        assert verification.is_valid is True


# ── sign_file / verify_file ──────────────────────────────────────────────────

class TestSignAndVerifyFile:
    def _write_file(self, path, content: bytes):
        Path(path).write_bytes(content)

    def test_sign_file_returns_signature_result(self, domain, key_paths, temp_dir):
        file_path = os.path.join(temp_dir, "data.bin")
        self._write_file(file_path, b"file content")
        private_path, _ = key_paths
        result = domain.sign_file(file_path, private_path)
        assert isinstance(result, SignatureResult)

    def test_verify_file_valid(self, domain, key_paths, temp_dir):
        file_path = os.path.join(temp_dir, "data.bin")
        self._write_file(file_path, b"important data")
        private_path, public_path = key_paths
        result = domain.sign_file(file_path, private_path)
        verification = domain.verify_file(file_path, public_path, signature_hex=result.signature_hex)
        assert verification.is_valid is True

    def test_verify_file_tampered_fails(self, domain, key_paths, temp_dir):
        file_path = os.path.join(temp_dir, "data.bin")
        self._write_file(file_path, b"original")
        private_path, public_path = key_paths
        result = domain.sign_file(file_path, private_path)
        # tamper the file
        self._write_file(file_path, b"tampered")
        verification = domain.verify_file(file_path, public_path, signature_hex=result.signature_hex)
        assert verification.is_valid is False

    def test_verify_file_with_signature_file(self, domain, key_paths, temp_dir):
        file_path = os.path.join(temp_dir, "data.bin")
        sig_path = os.path.join(temp_dir, "sig.hex")
        self._write_file(file_path, b"data")
        private_path, public_path = key_paths
        domain.sign_file(file_path, private_path, signature_output_path=sig_path)
        verification = domain.verify_file(file_path, public_path, signature_file_path=sig_path)
        assert verification.is_valid is True

    def test_verify_file_missing_signature_returns_invalid(self, domain, key_paths, temp_dir):
        file_path = os.path.join(temp_dir, "data.bin")
        self._write_file(file_path, b"data")
        _, public_path = key_paths
        verification = domain.verify_file(file_path, public_path)
        assert verification.is_valid is False
        assert "missing" in verification.message.lower()

    def test_sign_file_saves_signature(self, domain, key_paths, temp_dir):
        file_path = os.path.join(temp_dir, "data.bin")
        sig_path = os.path.join(temp_dir, "sig.hex")
        self._write_file(file_path, b"content")
        private_path, _ = key_paths
        result = domain.sign_file(file_path, private_path, signature_output_path=sig_path)
        saved = Path(sig_path).read_text(encoding="utf-8")
        assert saved == result.signature_hex

    def test_empty_file_can_be_signed(self, domain, key_paths, temp_dir):
        file_path = os.path.join(temp_dir, "empty.bin")
        self._write_file(file_path, b"")
        private_path, public_path = key_paths
        result = domain.sign_file(file_path, private_path)
        verification = domain.verify_file(file_path, public_path, signature_hex=result.signature_hex)
        assert verification.is_valid is True


# ── custom hash algorithm ─────────────────────────────────────────────────────

class TestCustomHashAlgorithm:
    def test_sha512_sign_verify(self, temp_dir):
        domain = Lab5Domain(has_algorithm=hashes.SHA512())
        private_path = os.path.join(temp_dir, "priv.pem")
        public_path = os.path.join(temp_dir, "pub.pem")
        domain.generate_keys(private_path, public_path)
        result = domain.sign_text("test sha512", private_path)
        verification = domain.verify_text("test sha512", result.signature_hex, public_path)
        assert verification.is_valid is True

    def test_default_algorithm_is_sha256(self):
        domain = Lab5Domain()
        assert isinstance(domain.hash_algorithm, hashes.SHA256)

class TestVerificationResultMessages:
    def test_valid_message(self, domain, key_paths):
        private_path, public_path = key_paths
        result = domain.sign_text("ok", private_path)
        verification = domain.verify_text("ok", result.signature_hex, public_path)
        assert "success" in verification.message.lower() or verification.is_valid

    def test_invalid_hex_message(self, domain, key_paths):
        _, public_path = key_paths
        verification = domain.verify_text("ok", "ZZZZ", public_path)
        assert "invalid" in verification.message.lower()

    def test_invalid_signature_message(self, domain, key_paths):
        private_path, public_path = key_paths
        result = domain.sign_text("original", private_path)
        verification = domain.verify_text("different", result.signature_hex, public_path)
        assert "invalid" in verification.message.lower()