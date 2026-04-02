from __future__ import annotations
import shutil
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from app.services.lab4.rsa_service import RSAService
import time
from fastapi.responses import JSONResponse
from app.services.lab3.rc5_service import Lab3Service
import zipfile

router = APIRouter()
rsa_service = RSAService()

BASE_TEMP_DIR = Path("temp_lab4")
BASE_TEMP_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/generate-keys")
async def generate_keys(
    key_size: int = Form(2048),
    password: str | None = Form(None),
):
    try:
        private_key_path = BASE_TEMP_DIR / "private_key.pem"
        public_key_path = BASE_TEMP_DIR / "public_key.pem"
        zip_path = BASE_TEMP_DIR / "rsa_keys.zip"

        rsa_service.generate_and_save_keys(
            private_key_path=private_key_path,
            public_key_path=public_key_path,
            key_size=key_size,
            password=password,
        )

        with zipfile.ZipFile(zip_path, "w") as zipf:
            zipf.write(private_key_path, "private_key.pem")
            zipf.write(public_key_path, "public_key.pem")

        return FileResponse(
            path=str(zip_path),
            filename="rsa_keys.zip",
            media_type="application/zip",
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@router.post("/encrypt")
async def encrypt_file(
    file: UploadFile = File(...),
    public_key: UploadFile = File(...),
):
    try:
        safe_file_name = Path(file.filename).name
        safe_key_name = Path(public_key.filename).name

        input_path = BASE_TEMP_DIR / safe_file_name
        public_key_path = BASE_TEMP_DIR / safe_key_name
        output_path = BASE_TEMP_DIR / f"{safe_file_name}.enc"

        with input_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        with public_key_path.open("wb") as buffer:
            shutil.copyfileobj(public_key.file, buffer)

        rsa_service.encrypt_file(
            input_path=input_path,
            output_path=output_path,
            public_key_path=public_key_path,
        )

        if not output_path.exists():
            raise FileNotFoundError(f"Encrypted file was not created: {output_path}")

        return FileResponse(
            path=str(output_path),
            filename=output_path.name,
            media_type="application/octet-stream",
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Encryption failed: {str(e)}")

@router.post("/decrypt")
async def decrypt_file(
    file: UploadFile = File(...),
    private_key: UploadFile = File(...),
    password: str | None = Form(None),
):
    try:
        safe_file_name = Path(file.filename).name
        safe_key_name = Path(private_key.filename).name

        input_path = BASE_TEMP_DIR / safe_file_name
        private_key_path = BASE_TEMP_DIR / safe_key_name

        if safe_file_name.endswith(".enc"):
            output_name = safe_file_name[:-4]
            if not output_name:
                output_name = "decrypted_file"
        else:
            output_name = f"{safe_file_name}.dec"

        output_path = BASE_TEMP_DIR / output_name

        with input_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        with private_key_path.open("wb") as buffer:
            shutil.copyfileobj(private_key.file, buffer)

        rsa_service.decrypt_file(
            input_path=input_path,
            output_path=output_path,
            private_key_path=private_key_path,
            password=password,
        )

        if not output_path.exists():
            raise FileNotFoundError(f"Decrypted file was not created: {output_path}")

        return FileResponse(
            path=str(output_path),
            filename=output_path.name,
            media_type="application/octet-stream",
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Decryption failed: {str(e)}")

@router.post("/compare-speed")
async def compare_speed(
    file: UploadFile = File(...),
    public_key: UploadFile = File(...),
    password: str = Form(...),
):
    try:
        safe_file_name = Path(file.filename).name
        safe_key_name = Path(public_key.filename).name

        input_path = BASE_TEMP_DIR / safe_file_name
        public_key_path = BASE_TEMP_DIR / safe_key_name

        rsa_output_path = BASE_TEMP_DIR / f"{safe_file_name}.rsa.enc"
        rc5_output_path = BASE_TEMP_DIR / f"{safe_file_name}.rc5.enc"

        with input_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        with public_key_path.open("wb") as buffer:
            shutil.copyfileobj(public_key.file, buffer)

        rsa_service = RSAService()

        rsa_start = time.perf_counter()
        rsa_service.encrypt_file(
            input_path=input_path,
            output_path=rsa_output_path,
            public_key_path=public_key_path,
        )
        rsa_end = time.perf_counter()

        rc5_start = time.perf_counter()
        Lab3Service.encrypt_file(
            password=password,
            input_path=str(input_path),
            output_path=str(rc5_output_path),
        )
        rc5_end = time.perf_counter()

        rsa_time = rsa_end - rsa_start
        rc5_time = rc5_end - rc5_start

        if rsa_time < rc5_time:
            faster_algorithm = "RSA"
            difference = rc5_time - rsa_time
        else:
            faster_algorithm = "RC5"
            difference = rsa_time - rc5_time

        return JSONResponse(
            content={
                "file_name": safe_file_name,
                "file_size_bytes": input_path.stat().st_size,
                "rsa_encrypt_time_seconds": round(rsa_time, 6),
                "rc5_encrypt_time_seconds": round(rc5_time, 6),
                "faster_algorithm": faster_algorithm,
                "time_difference_seconds": round(difference, 6),
            }
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Comparison failed: {str(e)}")