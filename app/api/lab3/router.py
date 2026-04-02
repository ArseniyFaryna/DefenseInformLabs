from __future__ import annotations
import shutil
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from app.services.lab3.rc5_service import Lab3Service
router = APIRouter()

BASE_TEMP_DIR = Path("temp_lab3")
BASE_TEMP_DIR.mkdir(exist_ok=True)


@router.post("/encrypt")
async def encrypt_file(
    file: UploadFile = File(...),
    password: str = Form(...)
):
    try:
        safe_name = Path(file.filename).name
        input_path = BASE_TEMP_DIR / safe_name
        output_path = BASE_TEMP_DIR / f"{safe_name}.enc"

        with input_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        Lab3Service.encrypt_file(
            password=password,
            input_path=str(input_path),
            output_path=str(output_path)
        )

        if not output_path.exists():
            raise FileNotFoundError(f"Encrypted file was not created: {output_path}")

        return FileResponse(
            path=str(output_path),
            filename=output_path.name,
            media_type="application/octet-stream"
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
    password: str = Form(...)
):
    try:
        safe_name = Path(file.filename).name
        input_path = BASE_TEMP_DIR / safe_name

        if safe_name.endswith(".enc"):
            output_name = safe_name[:-4]
            if not output_name:
                output_name = "decrypted_file"
        else:
            output_name = f"{safe_name}.dec"

        output_path = BASE_TEMP_DIR / output_name

        with input_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        Lab3Service.decrypt_file(
            password=password,
            input_path=str(input_path),
            output_path=str(output_path)
        )

        if not output_path.exists():
            raise FileNotFoundError(f"Decrypted file was not created: {output_path}")

        return FileResponse(
            path=str(output_path),
            filename=output_path.name,
            media_type="application/octet-stream"
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Decryption failed: {str(e)}")