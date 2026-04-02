from app.domain.lab5.signature import Lab5Domain


class Lab5Service:
    def __init__(self):
        self.domain = Lab5Domain()

    def generate_keys(
        self,
        private_key_path: str,
        public_key_path: str,
        password: str | None = None,
        key_size: int = 2048,
    ) -> dict:
        result = self.domain.generate_keys(
            private_key_path=private_key_path,
            public_key_path=public_key_path,
            password=password,
            key_size=key_size,
        )

        return {
            "message": "Keys generated successfully",
            "private_key_path": result.private_key_path,
            "public_key_path": result.public_key_path,
        }

    def sign_text(
        self,
        text: str,
        private_key_path: str,
        password: str | None = None,
        signature_output_path: str | None = None,
    ) -> dict:
        result = self.domain.sign_text(
            text=text,
            private_key_path=private_key_path,
            password=password,
            signature_output_path=signature_output_path,
        )

        return {
            "message": "Text signed successfully",
            "signature_hex": result.signature_hex,
        }

    def verify_text(
        self,
        text: str,
        signature_hex: str,
        public_key_path: str,
    ) -> dict:
        result = self.domain.verify_text(
            text=text,
            signature_hex=signature_hex,
            public_key_path=public_key_path,
        )

        return {
            "is_valid": result.is_valid,
            "message": result.message,
        }

    def sign_file(
        self,
        file_path: str,
        private_key_path: str,
        password: str | None = None,
        signature_output_path: str | None = None,
    ) -> dict:
        result = self.domain.sign_file(
            file_path=file_path,
            private_key_path=private_key_path,
            password=password,
            signature_output_path=signature_output_path,
        )

        return {
            "message": "File signed successfully",
            "signature_hex": result.signature_hex,
        }

    def verify_file(
        self,
        file_path: str,
        public_key_path: str,
        signature_hex: str | None = None,
        signature_file_path: str | None = None,
    ) -> dict:
        result = self.domain.verify_file(
            file_path=file_path,
            public_key_path=public_key_path,
            signature_hex=signature_hex,
            signature_file_path=signature_file_path,
        )

        return {
            "is_valid": result.is_valid,
            "message": result.message,
        }