from __future__ import annotations

from pathlib import Path

from app.domain.lab3.rc5 import RC5


class Lab3Service:
    @staticmethod
    def encrypt_file(password: str, input_path: str, output_path: str) -> str:
        input_file = Path(input_path)
        output_file = Path(output_path)

        if not input_file.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")

        rc5 = RC5.from_password(password)
        rc5.encrypt_file(str(input_file), str(output_file), RC5.generate_iv_bytes)

        return str(output_file.resolve())

    @staticmethod
    def decrypt_file(password: str, input_path: str, output_path: str) -> str:
        input_file = Path(input_path)
        output_file = Path(output_path)

        if not input_file.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")

        rc5 = RC5.from_password(password)
        rc5.decrypt_file(str(input_file), str(output_file))

        return str(output_file.resolve())