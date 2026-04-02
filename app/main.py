from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.lab1.router import router as lab1_router
from app.api.lab2.router import router as lab2_router
from app.api.lab3.router import router as lab3_router
from app.api.lab4.router import router as lab4_router
from app.api.lab5.router import router as lab5_router

app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name="static")
# API
app.include_router(lab1_router, prefix="/api/lab1", tags=["lab1"])
app.include_router(lab2_router, prefix="/api/lab2", tags=["lab2"])
app.include_router(lab3_router, prefix="/api/lab3", tags=["lab3"])
app.include_router(lab4_router, prefix="/api/lab4", tags=["lab4"])
app.include_router(lab5_router, prefix="/api/lab5", tags=["lab5"])

# Pages (HTML)
@app.get("/", include_in_schema=False)
def home():
    return FileResponse("app/static/home.html")

@app.get("/lab1", include_in_schema=False)
def lab1_page():
    return FileResponse("app/static/lab1.html")

@app.get("/lab2", include_in_schema=False)
def lab2_page():
    return FileResponse("app/static/lab2.html")

@app.get("/lab3", include_in_schema=False)
def lab3_page():
    return FileResponse("app/static/lab3.html")

@app.get("/lab4", include_in_schema=False)
def lab4_page():
    return FileResponse("app/static/lab4.html")

@app.get("/lab5", include_in_schema=False)
def lab5_page():
    return FileResponse("app/static/lab5.html")
