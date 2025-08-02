from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")


@app.get("/")
def root():
    return {"message": "File Converter API is running"}


@app.get("/convert/all")
def allConvert():
    return {
        "message": "All conversion endpoints are available",
        "endpoints": [
            "/api/v1/convert/png-to-pdf",
            "/api/v1/convert/jpg-to-pdf",
            "/api/v1/convert/image-to-pdf",
            "/api/v1/convert/docx-to-pdf",
            "/api/v1/convert/img-to-svg",
            "/api/v1/convert/pdf-to-jpg",
            "/api/v1/convert/pdf-to-png",
            "/api/v1/convert/svg-to-png",
            "/api/v1/convert/svg-to-jpg",
            "/api/v1/convert/svg-to-pdf",
        ],
        "Incoming endpoints": [
            "/api/v1/convert/pdf-to-image",
            "/api/v1/convert/pdf-to-docx",
            "/api/v1/convert/pdf-to-svg",
            "/api/v1/convert/svg-to-image",
            "/api/v1/convert/mp4-to-mp3",
            "/api/v1/convert/image-to-gif",
            "compression of all accepted formats of files",
        ],
    }
