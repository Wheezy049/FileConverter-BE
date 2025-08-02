from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from typing import Optional
import io
import os
import zipfile
from app.services.converter import FileConverter

router = APIRouter()
converter = FileConverter()


# conversion to pdf
# png to pdf
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


# jpg to pdf
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


# doc to pdf
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


# svg to pdf
@router.post("/convert/svg-to-pdf")
async def svg_to_pdf(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/svg+xml"):
        raise HTTPException(status_code=400, detail="File must be an SVG image")

    try:
        original_name = os.path.splitext(file.filename)[0]
        output_filename = f"{original_name}.pdf"

        svg_content = await file.read()
        pdf_content = converter.convert_svg_to_pdf(svg_content)

        return StreamingResponse(
            io.BytesIO(pdf_content),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={output_filename}"},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Conversion failed: {str(e)}")


# conversion from pdf


# pdf to jpg
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


# pdf to jpg
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


# pdf to docs

# pdf to image

# pdf to svg

# svg conversion


# image to svg
@router.post("/convert/img-to-svg")
async def img_to_svg(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    try:
        original_name = os.path.splitext(file.filename)[0]
        output_filename = f"{original_name}.svg"
        file_content = await file.read()
        if "png" in file.content_type:
            image_format = "PNG"
        elif "jpeg" in file.content_type or "jpg" in file.content_type:
            image_format = "JPEG"
        else:
            image_format = "PNG"

        svg_content = converter.convert_image_to_svg(file_content, image_format)

        return StreamingResponse(
            io.BytesIO(svg_content),
            media_type="image/svg+xml",
            headers={"Content-Disposition": f"attachment; filename={output_filename}"},
        )
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
        file_content = await file.read()
        svg_content = converter.convert_png_to_svg(file_content)

        return StreamingResponse(
            io.BytesIO(svg_content),
            media_type="image/svg+xml",
            headers={"Content-Disposition": f"attachment; filename={output_filename}"},
        )
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

        file_content = await file.read()
        svg_content = converter.convert_jpg_to_svg(file_content)

        return StreamingResponse(
            io.BytesIO(svg_content),
            media_type="image/svg+xml",
            headers={"Content-Disposition": f"attachment; filename={output_filename}"},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Conversion failed: {str(e)}")


# svg to image
# @router.post("/convert/svg-to-image")
# async def svg_to_image(file: UploadFile = File(...)):
#     if file.content_type != "image/svg+xml":
#         raise HTTPException(status_code=400, detail="File must be an SVG image")

#     try:
#         original_name = os.path.splitext(file.filename)[0]
#         output_filename = f"{original_name}.png"
#         file_content = await file.read()
#         png_content = converter.convert_svg_to_png(file_content)

#         return StreamingResponse(
#             io.BytesIO(png_content),
#             media_type="image/png",
#             headers={"Content-Disposition": f"attachment; filename={output_filename}"},
#         )
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Conversion failed: {str(e)}")


# svg to png
@router.post("/convert/svg-to-png")
def svg_to_png(file: UploadFile = File(...)):
    if file.content_type != "image/svg+xml":
        raise HTTPException(status_code=400, detail="File must be an SVG image")

    try:
        original_name = os.path.splitext(file.filename)[0]
        output_filename = f"{original_name}.png"
        svg_content = file.file.read()
        png_content = converter.convert_svg_to_png(svg_content)

        return StreamingResponse(
            io.BytesIO(png_content),
            media_type="image/png",
            headers={"Content-Disposition": f"attachment; filename={output_filename}"},
        )
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
        jpg_content = converter.convert_svg_to_jpg(svg_content)

        return StreamingResponse(
            io.BytesIO(jpg_content),
            media_type="image/jpeg",
            headers={"Content-Disposition": f"attachment; filename={output_filename}"},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Conversion failed: {str(e)}")
