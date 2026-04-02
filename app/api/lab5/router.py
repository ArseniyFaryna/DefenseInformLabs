from fastapi import APIRouter, HTTPException, status, UploadFile, File, Form
from fastapi.responses import FileResponse, StreamingResponse
from app.services.lab5.signature_service import Lab5Service
import tempfile, os, zipfile, io
from typing import Optional

router = APIRouter()
lab5_service = Lab5Service()


@router.post("/keys/generate", status_code=status.HTTP_201_CREATED)
def generate_keys(
    key_size: int = Form(2048),
    password: Optional[str] = Form(None),
):
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            private_key_path = os.path.join(tmpdir, "private_key.pem")
            public_key_path = os.path.join(tmpdir, "public_key.pem")

            lab5_service.generate_keys(
                private_key_path=private_key_path,
                public_key_path=public_key_path,
                password=password or None,
                key_size=key_size,
            )

            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w") as zf:
                zf.write(private_key_path, "private_key.pem")
                zf.write(public_key_path, "public_key.pem")
            zip_buffer.seek(0)

            return StreamingResponse(
                zip_buffer,
                media_type="application/zip",
                headers={"Content-Disposition": "attachment; filename=dsa_keys.zip"},
            )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Помилка генерації ключів: {str(e)}")


@router.post("/sign/text", status_code=status.HTTP_200_OK)
def sign_text(
    text: str = Form(...),
    private_key: UploadFile = File(...),
    password: Optional[str] = Form(None),
):
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            key_path = os.path.join(tmpdir, "private_key.pem")
            with open(key_path, "wb") as f:
                f.write(private_key.file.read())

            sig_path = os.path.join(tmpdir, "signature.txt")

            lab5_service.sign_text(
                text=text,
                private_key_path=key_path,
                password=password or None,
                signature_output_path=sig_path,
            )

            with open(sig_path, "rb") as f:
                content = f.read()

            return StreamingResponse(
                io.BytesIO(content),
                media_type="text/plain",
                headers={"Content-Disposition": "attachment; filename=text_signature.txt"},
            )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Помилка підпису тексту: {str(e)}")


@router.post("/verify/text", status_code=status.HTTP_200_OK)
def verify_text(
    text: str = Form(...),
    signature: UploadFile = File(...),
    public_key: UploadFile = File(...),
):
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            key_path = os.path.join(tmpdir, "public_key.pem")
            sig_path = os.path.join(tmpdir, "signature.txt")

            with open(key_path, "wb") as f:
                f.write(public_key.file.read())
            with open(sig_path, "wb") as f:
                f.write(signature.file.read())

            sig_hex = open(sig_path).read().strip()

            result = lab5_service.verify_text(
                text=text,
                signature_hex=sig_hex,
                public_key_path=key_path,
            )
            return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Помилка перевірки: {str(e)}")


@router.post("/sign/file", status_code=status.HTTP_200_OK)
def sign_file(
    file: UploadFile = File(...),
    private_key: UploadFile = File(...),
    password: Optional[str] = Form(None),
):
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, file.filename)
            key_path = os.path.join(tmpdir, "private_key.pem")
            sig_path = os.path.join(tmpdir, f"{file.filename}.sig")

            with open(file_path, "wb") as f:
                f.write(file.file.read())
            with open(key_path, "wb") as f:
                f.write(private_key.file.read())

            lab5_service.sign_file(
                file_path=file_path,
                private_key_path=key_path,
                password=password or None,
                signature_output_path=sig_path,
            )

            with open(sig_path, "rb") as f:
                content = f.read()

            return StreamingResponse(
                io.BytesIO(content),
                media_type="application/octet-stream",
                headers={"Content-Disposition": f"attachment; filename={file.filename}.sig"},
            )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Помилка підпису файлу: {str(e)}")


@router.post("/verify/file", status_code=status.HTTP_200_OK)
def verify_file(
    file: UploadFile = File(...),
    signature: UploadFile = File(...),
    public_key: UploadFile = File(...),
):
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, file.filename)
            key_path = os.path.join(tmpdir, "public_key.pem")
            sig_path = os.path.join(tmpdir, "signature.sig")

            with open(file_path, "wb") as f:
                f.write(file.file.read())
            with open(key_path, "wb") as f:
                f.write(public_key.file.read())
            with open(sig_path, "wb") as f:
                f.write(signature.file.read())

            result = lab5_service.verify_file(
                file_path=file_path,
                public_key_path=key_path,
                signature_hex=None,
                signature_file_path=sig_path,
            )
            return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Помилка перевірки файлу: {str(e)}")