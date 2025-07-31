import io  # for byte streams to read and write files in memory
from PIL import (
    Image,
)  # Pillow for for image processing like opening, converting and manipulation
from reportlab.pdfgen import canvas  # for pdf generation
from reportlab.lib.pagesizes import letter, A4  # for defining page size
from reportlab.lib.utils import ImageReader  # for reading images in reportlab
import fitz  # PyMuPDF for PDF manipulation pdf to image conversion
from docx2pdf import convert  # for converting Word documents to PDF
import tempfile  # for creating temporary files
import os  # for file path operations


class FileConverter:
    "Class to handle various file conversion operations."

    def __init__(self):
        self.temp_dir = tempfile.gettempdir()

    # conversion to PDF
    def convert_png_to_pdf(self, png_file_path: bytes) -> bytes:
        "function takes a png as bytes and returns a pdf as bytes"
        try:
            # load the image from memory
            image = Image.open(io.BytesIO(png_file_path))

            # convert image to RGB if not already in that mode
            if image.mode != "RGB":
                image = image.convert("RGB")

            # create PDF in memory
            pdf_buffer = io.BytesIO()

            # Get image dimensions
            img_width, img_height = image.size

            # Calculate page size to fit image
            page_width = min(img_width, A4[0])
            page_height = min(img_height, A4[1])

            # Create PDF
            c = canvas.Canvas(pdf_buffer, pagesize=(page_width, page_height))

            # Add image to PDF
            img_reader = ImageReader(io.BytesIO(png_file_path))
            c.drawImage(img_reader, 0, 0, width=page_width, height=page_height)
            c.save()

            return pdf_buffer.getvalue()

        except Exception as e:
            raise Exception(f"Error converting PNG to PDF: {str(e)}")

    @staticmethod
    def convert_jpg_to_pdf(jpg_file_path: bytes) -> bytes:
        "function takes a jpg as bytes and returns a pdf as bytes"
        try:
            image = Image.open(io.BytesIO(jpg_file_path))

            if image.mode != "RGB":
                image = image.convert("RGB")

            pdf_buffer = io.BytesIO()
            img_width, img_height = image.size
            page_width = min(img_width, A4[0])
            page_height = min(img_height, A4[1])
            c = canvas.Canvas(pdf_buffer, pagesize=(page_width, page_height))
            img_reader = ImageReader(io.BytesIO(jpg_file_path))
            c.drawImage(img_reader, 0, 0, width=page_width, height=page_height)
            c.save()
            return pdf_buffer.getvalue()
        except Exception as e:
            raise Exception(f"Error converting JPG to PDF: {str(e)}")

    def convert_docx_to_pdf(self, docx_content: bytes) -> bytes:
        """Convert DOCX bytes to PDF bytes"""
        try:
            # Create temporary files
            with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as temp_docx:
                temp_docx.write(docx_content)
                temp_docx_path = temp_docx.name

            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_pdf:
                temp_pdf_path = temp_pdf.name

            try:
                # Convert DOCX to PDF
                convert(temp_docx_path, temp_pdf_path)

                # Read the converted PDF
                with open(temp_pdf_path, "rb") as pdf_file:
                    pdf_content = pdf_file.read()

                return pdf_content

            finally:
                # Clean up temporary files
                if os.path.exists(temp_docx_path):
                    os.unlink(temp_docx_path)
                if os.path.exists(temp_pdf_path):
                    os.unlink(temp_pdf_path)

        except Exception as e:
            raise Exception(f"Error converting DOCX to PDF: {str(e)}")

    def convert_image_to_pdf(
        self, image_content: bytes, image_format: str = "PNG"
    ) -> bytes:
        """Generic method to convert any image format to PDF"""
        try:
            image = Image.open(io.BytesIO(image_content))

            if image.mode != "RGB":
                image = image.convert("RGB")

            pdf_buffer = io.BytesIO()
            image.save(pdf_buffer, format="PDF", resolution=100.0)

            return pdf_buffer.getvalue()

        except Exception as e:
            raise Exception(f"Error converting {image_format} to PDF: {str(e)}")

    # conversion from PDF
    def convert_pdf_to_png(self, pdf_content: bytes) -> list[bytes]:
        """Convert all PDF pages to PNG and return as a list of PNG bytes"""
        try:
            pdf_document = fitz.open(stream=pdf_content, filetype="pdf")
            images = []
            mat = fitz.Matrix(2.0, 2.0)  # Zoom for better quality
            for page_num in range(len(pdf_document)):
                page = pdf_document.load_page(page_num)
                pix = page.get_pixmap(matrix=mat)
                png_data = pix.tobytes("png")
                images.append(png_data)
                pdf_document.close()
                return images
        except Exception as e:
            raise Exception(f"Error converting PDF to PNG: {str(e)}")

    def convert_pdf_to_jpg(self, pdf_content: bytes) -> list[bytes]:
        """Convert all PDF pages to JPG and return as a list of JPG bytes"""
        try:
            pdf_document = fitz.open(stream=pdf_content, filetype="pdf")
            images = []
            mat = fitz.Matrix(2.0, 2.0)  # Zoom for better quality
            for page_num in range(len(pdf_document)):
                page = pdf_document.load_page(page_num)
                pix = page.get_pixmap(matrix=mat)
                jpg_data = pix.tobytes("jpg")
                images.append(jpg_data)
                pdf_document.close()
                return images
        except Exception as e:
            raise Exception(f"Error converting PDF to JPG: {str(e)}")
