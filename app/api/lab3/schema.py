from pydantic import BaseModel


class Lab3FileResponse(BaseModel):
    filename: str
    message: str