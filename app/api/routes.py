from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from typing import Optional
import io
import os
import zipfile
from app.services.converter import FileConverter

router = APIRouter()
converter = FileConverter()


@router.post("/convert/png-to-pdf")
async def png_to_pdf(file: UploadFile = File(...)):
    """Convert PNG image to PDF"""
    if not file.content_type.startswith("image/png"):
        raise HTTPException(status_code=400, detail="File must be a PNG image")

    try:
        # getting the file name without extension
        original_name = os.path.splitext(file.filename)[0]
        output_filename = f"{original_name}.pdf"

        # Read the uploaded file
        png_content = await file.read()

        # Convert using the converter
        pdf_content = converter.convert_png_to_pdf(png_content)

        # Return as streaming response
        return StreamingResponse(
            io.BytesIO(pdf_content),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={output_filename}"},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Conversion failed: {str(e)}")


@router.post("/convert/jpg-to-pdf")
async def jpg_to_pdf(file: UploadFile = File(...)):
    """Convert JPG image to PDF"""
    if not file.content_type.startswith("image/jpeg"):
        raise HTTPException(status_code=400, detail="File must be a JPG image")

    try:
        original_name = os.path.splitext(file.filename)[0]
        output_filename = f"{original_name}.pdf"

        jpg_content = await file.read()

        pdf_content = converter.convert_jpg_to_pdf(jpg_content)

        return StreamingResponse(
            io.BytesIO(pdf_content),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={output_filename}"},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Conversion failed: {str(e)}")


@router.post("/convert/image-to-pdf")
async def image_to_pdf(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400, detail="File must be an image (jpg, png, webp, etc.)"
        )

    # Extract the image format from content-type, e.g., 'image/png' -> 'PNG'
    image_format = file.content_type.split("/")[-1].upper()

    try:
        original_name = os.path.splitext(file.filename)[0]
        output_filename = f"{original_name}.pdf"
        pdf_content = converter.convert_image_to_pdf(
            await file.read(), image_format=image_format
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return StreamingResponse(
        io.BytesIO(pdf_content),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={output_filename}"},
    )


@router.post("/convert/docx-to-pdf")
async def docx_to_pdf(file: UploadFile = File(...)):
    """Convert DOCX document to PDF"""
    if not file.content_type.startswith("application/vnd.openxmlformats"):
        raise HTTPException(status_code=400, detail="File must be a DOCX document")

    try:
        original_name = os.path.splitext(file.filename)[0]
        output_filename = f"{original_name}.pdf"

        file_content = await file.read()
        pdf_content = converter.convert_docx_to_pdf(file_content)

        return StreamingResponse(
            io.BytesIO(pdf_content),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={output_filename}"},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Conversion failed: {str(e)}")


@router.post("/convert/pdf-to-png")
async def pdf_to_png(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="File must be a PDF")

    try:
        file_content = await file.read()
        images = converter.convert_pdf_to_png(file_content)

        if len(images) == 1:
            # Single page: return image directly
            original_name = os.path.splitext(file.filename)[0]
            output_filename = f"{original_name}_page_1.png"
            return StreamingResponse(
                io.BytesIO(images[0]),
                media_type="image/png",
                headers={
                    "Content-Disposition": f"attachment; filename={output_filename}"
                },
            )
        else:
            # Multiple pages: return a ZIP of images
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w") as zipf:
                for i, img_bytes in enumerate(images, start=1):
                    zipf.writestr(f"{original_name}_page_{i}.png", img_bytes)
            zip_buffer.seek(0)
            zip_filename = f"{original_name}_images.zip"
            return StreamingResponse(
                zip_buffer,
                media_type="application/zip",
                headers={"Content-Disposition": f"attachment; filename={zip_filename}"},
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Conversion failed: {str(e)}")


@router.post("/convert/pdf-to-jpg")
async def pdf_to_jpg(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="File must be a PDF")

    try:
        file_content = await file.read()
        images = converter.convert_pdf_to_jpg(file_content)

        if len(images) == 1:
            # Single page: return image directly
            original_name = os.path.splitext(file.filename)[0]
            output_filename = f"{original_name}_page_1.jpg"
            return StreamingResponse(
                io.BytesIO(images[0]),
                media_type="image/jpeg",
                headers={
                    "Content-Disposition": f"attachment; filename={output_filename}"
                },
            )
        else:
            # Multiple pages: return a ZIP of images
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w") as zipf:
                for i, img_bytes in enumerate(images, start=1):
                    zipf.writestr(f"{original_name}_page_{i}.jpg", img_bytes)
            zip_buffer.seek(0)
            zip_filename = f"{original_name}_images.zip"
            return StreamingResponse(
                zip_buffer,
                media_type="application/zip",
                headers={"Content-Disposition": f"attachment; filename={zip_filename}"},
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Conversion failed: {str(e)}")
