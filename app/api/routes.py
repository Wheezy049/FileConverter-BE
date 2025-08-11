from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import StreamingResponse
from typing import Optional
import io
import os
import zipfile
from app.services.converter import FileConverter, FileCompressor
import mimetypes
import uuid

router = APIRouter()
converter = FileConverter()

Temp_Storage = {}


# png to pdf
@router.post("/convert/png-to-pdf")
async def png_to_pdf(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/png"):
        raise HTTPException(status_code=400, detail="File must be a PNG image")

    try:
        # getting the file name without extension
        original_name = os.path.splitext(file.filename)[0]
        output_filename = f"{original_name}.pdf"

        # Read the uploaded file
        png_content = await file.read()
        file_id = str(uuid.uuid4())

        # Convert using the converter
        pdf_content = converter.convert_png_to_pdf(png_content)

        Temp_Storage[file_id] = {
            "content": pdf_content,
            "media_type": "application/pdf",
            "filename": f"{output_filename}",
        }

        # Return as streaming response
        return {
            "file_id": file_id,
            "filename": output_filename,
            "message": "File Converted successfully",
            "download_url": f"/api/v1/download/{file_id}",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Conversion failed: {str(e)}")


# jpg to pdf
@router.post("/convert/jpg-to-pdf")
async def jpg_to_pdf(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/jpeg"):
        raise HTTPException(status_code=400, detail="File must be a JPG image")

    try:
        original_name = os.path.splitext(file.filename)[0]
        output_filename = f"{original_name}.pdf"
        file_id = str(uuid.uuid4())
        jpg_content = await file.read()

        pdf_content = converter.convert_jpg_to_pdf(jpg_content)

        Temp_Storage[file_id] = {
            "content": pdf_content,
            "media_type": "application/pdf",
            "filename": f"{output_filename}",
        }

        return {
            "file_id": file_id,
            "filename": output_filename,
            "message": "File Converted successfully",
            "download_url": f"/api/v1/download/{file_id}",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Conversion failed: {str(e)}")


# image to pdf
@router.post("/convert/img-to-pdf")
async def img_to_pdf(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400, detail="File must be an image (jpg, png, webp, etc.)"
        )

    # Extract the image format from content-type, e.g., 'image/png' -> 'PNG'
    image_format = file.content_type.split("/")[-1].upper()

    try:
        original_name = os.path.splitext(file.filename)[0]
        output_filename = f"{original_name}.pdf"
        file_id = str(uuid.uuid4())
        pdf_content = converter.convert_image_to_pdf(
            await file.read(), image_format=image_format
        )

        Temp_Storage[file_id] = {
            "content": pdf_content,
            "media_type": "application/pdf",
            "filename": f"{output_filename}",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {
        "file_id": file_id,
        "filename": output_filename,
        "message": "File Converted successfully",
        "download_url": f"/api/v1/download/{file_id}",
    }


# doc to pdf
@router.post("/convert/docx-to-pdf")
async def docx_to_pdf(file: UploadFile = File(...)):
    """Convert DOCX document to PDF"""
    if not file.content_type.startswith("application/vnd.openxmlformats"):
        raise HTTPException(status_code=400, detail="File must be a DOCX document")

    try:
        original_name = os.path.splitext(file.filename)[0]
        output_filename = f"{original_name}.pdf"
        file_id = str(uuid.uuid4())
        file_content = await file.read()
        pdf_content = converter.convert_docx_to_pdf(file_content)

        Temp_Storage[file_id] = {
            "content": pdf_content,
            "media_type": "application/pdf",
            "filename": f"{output_filename}",
        }

        return {
            "file_id": file_id,
            "filename": output_filename,
            "message": "File Converted successfully",
            "download_url": f"/api/v1/download/{file_id}",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Conversion failed: {str(e)}")


# svg to pdf
@router.post("/convert/svg-to-pdf")
async def svg_to_pdf(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/svg+xml"):
        raise HTTPException(status_code=400, detail="File must be an SVG image")

    try:
        original_name = os.path.splitext(file.filename)[0]
        output_filename = f"{original_name}.pdf"
        file_id = str(uuid.uuid4())
        svg_content = await file.read()
        pdf_content = converter.convert_svg_to_pdf(svg_content)

        Temp_Storage[file_id] = {
            "content": pdf_content,
            "media_type": "application/pdf",
            "filename": f"{output_filename}",
        }

        return {
            "file_id": file_id,
            "filename": output_filename,
            "message": "File Converted successfully",
            "download_url": f"/api/v1/download/{file_id}",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Conversion failed: {str(e)}")


# pdf to jpg
@router.post("/convert/pdf-to-png")
async def pdf_to_png(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="File must be a PDF")

    try:
        file_content = await file.read()
        if len(file_content) > 100 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File exceeds 100MB limit")
        file_id = str(uuid.uuid4())
        images = converter.convert_pdf_to_png(file_content)

        if len(images) == 1:
            # Single page: return image directly
            original_name = os.path.splitext(file.filename)[0]
            output_filename = f"{original_name}_page_1.png"
            Temp_Storage[file_id] = {
                "content": images,
                "media_type": "image/png",
                "filename": f"{output_filename}",
            }
            return {
                "file_id": file_id,
                "filename": output_filename,
                "message": "File Converted successfully",
                "download_url": f"/api/v1/download/{file_id}",
            }

        else:
            # Multiple pages: return a ZIP of images
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w") as zipf:
                for i, img_bytes in enumerate(images, start=1):
                    zipf.writestr(f"{original_name}_page_{i}.png", img_bytes)
            zip_buffer.seek(0)
            zip_filename = f"{original_name}_images.zip"
            Temp_Storage[file_id] = {
                "content": images,
                "media_type": "application/zip",
                "filename": f"{zip_filename}",
            }
            return {
                "file_id": file_id,
                "filename": zip_filename,
                "message": "File Converted successfully",
                "download_url": f"/api/v1/download/{file_id}",
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Conversion failed: {str(e)}")


# pdf to jpg
@router.post("/convert/pdf-to-jpg")
async def pdf_to_jpg(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="File must be a PDF")

    try:
        file_content = await file.read()
        if len(file_content) > 100 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File exceeds 100MB limit")
        file_id = str(uuid.uuid4())
        images = converter.convert_pdf_to_jpg(file_content)

        if len(images) == 1:
            # Single page: return image directly
            original_name = os.path.splitext(file.filename)[0]
            output_filename = f"{original_name}_page_1.jpg"
            Temp_Storage[file_id] = {
                "content": images,
                "media_type": "image/png",
                "filename": f"{output_filename}",
            }
            return {
                "file_id": file_id,
                "filename": output_filename,
                "message": "File Converted successfully",
                "download_url": f"/api/v1/download/{file_id}",
            }

        else:
            # Multiple pages: return a ZIP of images
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w") as zipf:
                for i, img_bytes in enumerate(images, start=1):
                    zipf.writestr(f"{original_name}_page_{i}.jpg", img_bytes)
            zip_buffer.seek(0)
            zip_filename = f"{original_name}_images.zip"
            Temp_Storage[file_id] = {
                "content": images,
                "media_type": "application/zip",
                "filename": f"{zip_filename}",
            }
            return {
                "file_id": file_id,
                "filename": zip_filename,
                "message": "File Converted successfully",
                "download_url": f"/api/v1/download/{file_id}",
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Conversion failed: {str(e)}")


# pdf to docs
@router.post("/connvert/pdf-to-docx")
async def pdf_to_docx(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="File must be a PDF")

    try:
        file_content = await file.read()
        if len(file_content) > 100 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File exceeds 100MB limit")
        original_filename = os.path.splitext(file.filename)[0]
        output_filename = f"{original_filename}.docx"
        file_id = str(uuid.uuid4())
        docx_byte = converter.convert_pdf_to_docx(file_content)
        Temp_Storage[file_id] = {
            "content": docx_byte,
            "media_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "filename": f"{output_filename}",
        }
        return {
            "file_id": file_id,
            "filename": output_filename,
            "message": "File Converted successfully",
            "download_url": f"/api/v1/download/{file_id}",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Conversion failed: {str(e)}")


# pdf to image
@router.post("/convert/pdf-to-img")
async def pdf_to_img(file: UploadFile = File(...), output_format: str = Form(...)):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="File must be a PDF")

    output_format = output_format.upper()
    if output_format not in ["PNG", "JPEG", "JPG"]:
        raise HTTPException(
            status_code=400,
            detail="Unsupported image format. Only PNG or JPEG are supported.",
        )

    try:
        file_content = await file.read()
        if len(file_content) > 100 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File exceeds 100MB limit")
        original_name = os.path.splitext(file.filename)[0]
        file_id = str(uuid.uuid4())
        images = converter.convert_pdf_to_image(file_content, output_format)

        if len(images) == 1:
            output_filename = f"{original_name}_page_1.{output_format.lower()}"
            Temp_Storage[file_id] = {
                "content": images,
                "media_type": f"image/{output_format.lower()}",
                "filename": f"{output_filename}",
            }
            return {
                "file_id": file_id,
                "filename": output_filename,
                "message": "File Converted successfully",
                "download_url": f"/api/v1/download/{file_id}",
            }
        else:
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w") as zipf:
                for i, img_bytes in enumerate(images, start=1):
                    zipf.writestr(
                        f"{original_name}_page_{i}.{output_format.lower()}", img_bytes
                    )
            zip_buffer.seek(0)
            Temp_Storage[file_id] = {
                "content": images,
                "media_type": "application/zip",
                "filename": f"{original_name}_images.zip",
            }
            return {
                "file_id": file_id,
                "filename": f"{original_name}_images.zip",
                "message": "File Converted successfully",
                "download_url": f"/api/v1/download/{file_id}",
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Conversion failed: {str(e)}")


# pdf to svg


# image to svg
@router.post("/convert/img-to-svg")
async def img_to_svg(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    try:
        original_name = os.path.splitext(file.filename)[0]
        file_id = str(uuid.uuid4())
        output_filename = f"{original_name}.svg"
        file_content = await file.read()
        if "png" in file.content_type:
            image_format = "PNG"
        elif "jpeg" in file.content_type or "jpg" in file.content_type:
            image_format = "JPEG"
        else:
            image_format = "PNG"

        svg_content = converter.convert_image_to_svg(file_content, image_format)
        Temp_Storage[file_id] = {
            "content": svg_content,
            "media_type": "image/svg+xml",
            "filename": f"{output_filename}",
        }

        return {
            "file_id": file_id,
            "filename": output_filename,
            "message": "File Converted successfully",
            "download_url": f"/api/v1/download/{file_id}",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Conversion failed: {str(e)}")


# png to svg
@router.post("/convert/png-to-svg")
async def png_to_svg(file: UploadFile = File(...)):
    if file.content_type != "image/png":
        raise HTTPException(status_code=400, detail="File must be a PNG image")

    try:
        original_name = os.path.splitext(file.filename)[0]
        output_filename = f"{original_name}.svg"
        file_id = str(uuid.uuid4())
        file_content = await file.read()
        svg_content = converter.convert_png_to_svg(file_content)
        Temp_Storage[file_id] = {
            "content": svg_content,
            "media_type": "image/svg+xml",
            "filename": f"{output_filename}",
        }

        return {
            "file_id": file_id,
            "filename": output_filename,
            "message": "File Converted successfully",
            "download_url": f"/api/v1/download/{file_id}",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Conversion failed: {str(e)}")


# jpg to svg
@router.post("/convert/jpg-to-svg")
async def jpg_to_svg(file: UploadFile = File(...)):
    if file.content_type != "image/jpeg":
        raise HTTPException(status_code=400, detail="File must be a JPEG image")

    try:
        original_name = os.path.splitext(file.filename)[0]
        output_filename = f"{original_name}.svg"
        file_id = str(uuid.uuid4())
        file_content = await file.read()
        svg_content = converter.convert_jpg_to_svg(file_content)
        Temp_Storage[file_id] = {
            "content": svg_content,
            "media_type": "application/zip",
            "filename": f"{output_filename}",
        }

        return {
            "file_id": file_id,
            "filename": output_filename,
            "message": "File Converted successfully",
            "download_url": f"/api/v1/download/{file_id}",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Conversion failed: {str(e)}")


# svg to image
@router.post("/convert/svg-to-img")
async def svg_to_img(file: UploadFile = File(...), output_format: str = Form(...)):
    if file.content_type != "image/svg+xml":
        raise HTTPException(status_code=400, detail="File must be an SVG image")

    output_format = output_format.upper()
    supported_format = ["PNG", "JPEG", "JPG"]

    if output_format not in supported_format:
        raise HTTPException(
            status_code=400,
            detail="Unsupported image format. Only PNG or JPEG are supported.",
        )

    try:
        original_name = os.path.splitext(file.filename)[0]
        output_filename = f"{original_name}.{output_format.lower()}"
        file_content = await file.read()
        file_id = str(uuid.uuid4())
        png_content = converter.convert_svg_to_image(file_content, output_format)
        Temp_Storage[file_id] = {
            "content": png_content,
            "media_type": f"image/{output_format.lower()}",
            "filename": f"{output_filename}",
        }

        return {
            "file_id": file_id,
            "filename": output_filename,
            "message": "File Converted successfully",
            "download_url": f"/api/v1/download/{file_id}",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Conversion failed: {str(e)}")


# svg to png
@router.post("/convert/svg-to-png")
def svg_to_png(file: UploadFile = File(...)):
    if file.content_type != "image/svg+xml":
        raise HTTPException(status_code=400, detail="File must be an SVG image")

    try:
        original_name = os.path.splitext(file.filename)[0]
        output_filename = f"{original_name}.png"
        svg_content = file.file.read()
        file_id = str(uuid.uuid4)
        png_content = converter.convert_svg_to_png(svg_content)

        Temp_Storage[file_id] = {
            "content": png_content,
            "media_type": "image/png",
            "filename": f"{output_filename}",
        }

        return {
            "file_id": file_id,
            "filename": output_filename,
            "message": "File Converted successfully",
            "download_url": f"/api/v1/download/{file_id}",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Conversion failed: {str(e)}")


# svg to jpg
@router.post("/convert/svg-to-jpg")
def svg_to_jpg(file: UploadFile = File(...)):
    if file.content_type != "image/svg+xml":
        raise HTTPException(status_code=400, detail="File must be an SVG image")

    try:
        original_name = os.path.splitext(file.filename)[0]
        output_filename = f"{original_name}.jpg"
        svg_content = file.file.read()
        file_id = str(uuid.uuid4())
        jpg_content = converter.convert_svg_to_jpg(svg_content)
        Temp_Storage[file_id] = {
            "content": jpg_content,
            "media_type": "application/zip",
            "filename": f"{output_filename}",
        }

        return {
            "file_id": file_id,
            "filename": output_filename,
            "message": "File Converted successfully",
            "download_url": f"/api/v1/download/{file_id}",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Conversion failed: {str(e)}")


# mp4 to mp3
@router.post("/convert/mp4-to-mp3")
async def mp4_to_mp3(file: UploadFile = File(...)):
    allowed_extensions = [".mp4", ".mov", ".avi", ".mkv", ".flv", ".wmv", ".webm"]
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail=f"Only video files with extensions {allowed_extensions} are supported.")

    try:
        file_content = await file.read()
        if len(file_content) > 300 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File exceeds 300MB limit")
        file_id = str(uuid.uuid4())
        mp3_bytes = converter.convert_mp4_to_mp3(file_content, file_ext)

        output_filename = os.path.splitext(file.filename)[0] + ".mp3"

        Temp_Storage[file_id] = {
            "content": mp3_bytes,
            "media_type": "audio/mpeg",
            "filename": f"{output_filename}",
        }

        return {
            "file_id": file_id,
            "filename": output_filename,
            "message": "File Converted successfully",
            "download_url": f"/api/v1/download/{file_id}",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Conversion failed: {str(e)}")


# file compressor
@router.post("/compress")
async def compress_file(file: UploadFile = File(...), percent: int = Form(...)):
    contents = await file.read()

    if len(contents) > 500 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File exceeds 500MB limit")
    file_id = str(uuid.uuid4())
    mime_type, _ = mimetypes.guess_type(file.filename)
    if mime_type is None or not any(
        mime_type.startswith(typ)
        for typ in ["image", "audio", "video", "application/pdf"]
    ):
        raise HTTPException(status_code=400, detail="Unsupported file type")

    try:
        compressor = FileCompressor(compression_percentage=percent)
        compressed = compressor.compress(contents, mime_type, file.filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    Temp_Storage[file_id] = {
        "content": compressed,
        "media_type": mime_type,
        "filename": f"compressed_{file.filename}",
    }

    return {
        "file_id": file_id,
        "message": "File compressed successfully",
        "filename": f"compressed_{file.filename}",
        "download_url": f"/api/v1/download/{file_id}",
    }


@router.post("/download/{file_id}")
async def download_file(file_id: str):
    file_data = Temp_Storage.get(file_id)
    if not file_data:
        raise HTTPException(status_code=404, detail="File not found")

    return StreamingResponse(
        io.BytesIO(file_data["content"]),
        media_type=file_data["media_type"],
        headers={
            "Content-Disposition": f"attachment; filename={file_data['filename']}"
        },
    )
