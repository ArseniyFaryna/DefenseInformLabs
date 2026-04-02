from __future__ import annotations

import re
from pathlib import Path

import pytest

from app.services.lab3.rc5_service import Lab3Service


def test_encrypt_file_success(tmp_path: Path):
    input_file = tmp_path / "input.txt"
    output_file = tmp_path / "encrypted.bin"

    original_data = b"Hello from service test"
    input_file.write_bytes(original_data)

    result_path = Lab3Service.encrypt_file(
        password="mypassword",
        input_path=str(input_file),
        output_path=str(output_file),
    )

    assert output_file.exists()
    assert Path(result_path).resolve() == output_file.resolve()

    encrypted_data = output_file.read_bytes()
    assert encrypted_data != original_data
    assert len(encrypted_data) > 16


def test_encrypt_file_input_not_found(tmp_path: Path):
    missing_file = tmp_path / "missing.txt"
    output_file = tmp_path / "encrypted.bin"

    expected_message = re.escape(f"Input file not found: {missing_file}")

    with pytest.raises(FileNotFoundError, match=expected_message):
        Lab3Service.encrypt_file(
            password="mypassword",
            input_path=str(missing_file),
            output_path=str(output_file),
        )


def test_decrypt_file_success(tmp_path: Path):
    input_file = tmp_path / "input.txt"
    encrypted_file = tmp_path / "encrypted.bin"
    decrypted_file = tmp_path / "decrypted.txt"

    original_data = b"Secret data for decrypt service test"
    input_file.write_bytes(original_data)

    Lab3Service.encrypt_file(
        password="mypassword",
        input_path=str(input_file),
        output_path=str(encrypted_file),
    )

    result_path = Lab3Service.decrypt_file(
        password="mypassword",
        input_path=str(encrypted_file),
        output_path=str(decrypted_file),
    )

    assert decrypted_file.exists()
    assert Path(result_path).resolve() == decrypted_file.resolve()
    assert decrypted_file.read_bytes() == original_data


def test_decrypt_file_input_not_found(tmp_path: Path):
    missing_file = tmp_path / "missing.bin"
    output_file = tmp_path / "decrypted.txt"

    expected_message = re.escape(f"Input file not found: {missing_file}")

    with pytest.raises(FileNotFoundError, match=expected_message):
        Lab3Service.decrypt_file(
            password="mypassword",
            input_path=str(missing_file),
            output_path=str(output_file),
        )


def test_decrypt_file_with_wrong_password_raises_error(tmp_path: Path):
    input_file = tmp_path / "input.txt"
    encrypted_file = tmp_path / "encrypted.bin"
    decrypted_file = tmp_path / "decrypted.txt"

    input_file.write_bytes(b"Top secret message")

    Lab3Service.encrypt_file(
        password="correct_password",
        input_path=str(input_file),
        output_path=str(encrypted_file),
    )

    with pytest.raises(ValueError):
        Lab3Service.decrypt_file(
            password="wrong_password",
            input_path=str(encrypted_file),
            output_path=str(decrypted_file),
        )


def test_encrypt_and_decrypt_empty_file(tmp_path: Path):
    input_file = tmp_path / "empty.txt"
    encrypted_file = tmp_path / "empty.bin"
    decrypted_file = tmp_path / "empty_out.txt"

    input_file.write_bytes(b"")

    Lab3Service.encrypt_file(
        password="mypassword",
        input_path=str(input_file),
        output_path=str(encrypted_file),
    )

    Lab3Service.decrypt_file(
        password="mypassword",
        input_path=str(encrypted_file),
        output_path=str(decrypted_file),
    )

    assert decrypted_file.exists()
    assert decrypted_file.read_bytes() == b""