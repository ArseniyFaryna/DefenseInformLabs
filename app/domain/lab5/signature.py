from dataclasses import dataclass
from pathlib import Path
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import dsa

@dataclass(slots=True)
class SignatureResult:
    signature_bytes: bytes
    signature_hex: str

@dataclass(slots=True)
class VerificationResult:
    is_valid: bool
    message: str


@dataclass(slots=True)
class KeyPairPaths:
    private_key_path: str
    public_key_path: str


class Lab5Domain:
    def __init__(self, has_algorithm=None):
        self.hash_algorithm = has_algorithm or hashes.SHA256()

    def generate_keys(self, private_key_path: str, public_key_path: str, password: str | None = None, key_size: int = 2048) -> KeyPairPaths:
        private_key = dsa.generate_private_key(key_size=key_size)
        public_key = private_key.public_key()

        if password:
            encryption = serialization.BestAvailableEncryption(password.encode("utf-8"))
        else:
            encryption = serialization.NoEncryption()

        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=encryption
        )

        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )

        private_path = Path(private_key_path)
        public_path = Path(public_key_path)

        private_path.parent.mkdir(parents=True, exist_ok=True)
        public_path.parent.mkdir(parents=True, exist_ok=True)

        private_path.write_bytes(private_pem)
        public_path.write_bytes(public_pem)

        return KeyPairPaths(
            private_key_path=str(private_path),
            public_key_path=str(public_path)
        )

    def load_private_key(self, private_key_path: str, password: str | None = None):
        pem_data = Path(private_key_path).read_bytes()
        return serialization.load_pem_private_key(pem_data, password=password.encode("utf-8") if password else None)

    def load_public_key(self, public_key_path: str):
        pem_data = Path(public_key_path).read_bytes()
        return serialization.load_pem_public_key(pem_data)

    def sign_bytes(self, data: bytes, private_key) -> SignatureResult:
        signature = private_key.sign(data, self.hash_algorithm)
        return SignatureResult(signature_bytes=signature, signature_hex=signature.hex())

    def verify_bytes(self, data: bytes, signature_hex: str, public_key) -> VerificationResult:
        try:
            signature_bytes = bytes.fromhex(signature_hex.strip())
            public_key.verify(signature_bytes, data, self.hash_algorithm)
            return VerificationResult(is_valid=True, message="Signature verified successfully.")
        except ValueError:
            return VerificationResult(is_valid=False, message="Signature hex format is invalid.")
        except InvalidSignature:
            return VerificationResult(is_valid=False, message="Signature is invalid")

    def sign_text(self, text: str, private_key_path: str, password: str | None = None, signature_output_path: str | None = None) -> SignatureResult:
        private_key = self.load_private_key(private_key_path, password)
        result = self.sign_bytes(text.encode("utf-8"), private_key)

        if signature_output_path:
            Path(signature_output_path).write_text(result.signature_hex, encoding="utf-8")
        return result

    def verify_text(self, text: str, signature_hex: str, public_key_path: str) -> VerificationResult:
        public_key = self.load_public_key(public_key_path)
        return self.verify_bytes(text.encode("utf-8"), signature_hex, public_key)

    def sign_file(self, file_path: str, private_key_path: str, password: str | None = None, signature_output_path: str | None = None) -> SignatureResult:
        private_key = self.load_private_key(private_key_path, password)
        data = Path(file_path).read_bytes()
        result = self.sign_bytes(data, private_key)

        if signature_output_path:
            Path(signature_output_path).write_text(result.signature_hex, encoding="utf-8")

        return result

    def verify_file(self, file_path: str, public_key_path: str, signature_hex: str | None = None, signature_file_path: str | None = None) -> VerificationResult:
        if not signature_hex and not signature_file_path:
            return VerificationResult(False, "Signature is missing")

        if signature_file_path:
            signature_hex = Path(signature_file_path).read_text(encoding="utf-8").strip()

        public_key = self.load_public_key(public_key_path)
        data = Path(file_path).read_bytes()

        return self.verify_bytes(data, signature_hex, public_key)
