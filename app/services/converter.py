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
import base64  # for encoding and decoding base64 strings
from xml.etree.cElementTree import (
    Element,
    SubElement,
    tostring,
)  # for XML parsing and manipulation
import xml.etree.ElementTree as ET  # for XML parsing and manipulation

# from cairosvg import svg2png  # for converting SVG to PNG
# import svglib.svglib as svglib  # for SVG to PDF conversion
from reportlab.graphics import renderPM  # for rendering SVG to PDF
from cairosvg import svg2png, svg2pdf
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM
from docx import Document
from moviepy import VideoFileClip

# from pydub import AudioSegment
import pikepdf  # for PDF manipulation and compression


class FileConverter:
    "Class to handle various file conversion operations."

    def __init__(self):
        self.temp_dir = tempfile.gettempdir()

    # png to pdf
    def convert_png_to_pdf(self, png_file_path: bytes) -> bytes:
        return self.convert_image_to_pdf(png_file_path, image_format="PNG")

    # jpg to pdf
    @staticmethod
    def convert_jpg_to_pdf(jpg_file_path: bytes) -> bytes:
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

    # doc to pdf
    def convert_docx_to_pdf(self, docx_content: bytes) -> bytes:
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
                if os.path.exists(temp_docx_path):
                    os.unlink(temp_docx_path)
                if os.path.exists(temp_pdf_path):
                    os.unlink(temp_pdf_path)

        except Exception as e:
            raise Exception(f"Error converting DOCX to PDF: {str(e)}")

    # image to pdf
    def convert_image_to_pdf(
        self, image_content: bytes, image_format: str = "PNG"
    ) -> bytes:
        try:
            image = Image.open(io.BytesIO(image_content))

            if image.mode != "RGB":
                image = image.convert("RGB")

            pdf_buffer = io.BytesIO()
            image.save(pdf_buffer, format="PDF", resolution=100.0)

            return pdf_buffer.getvalue()

        except Exception as e:
            raise Exception(f"Error converting {image_format} to PDF: {str(e)}")

    # svg to pdf
    def convert_svg_to_pdf(self, svg_content: bytes) -> bytes:
        try:
            pdf_bytes = svg2pdf(bytestring=svg_content)
            return pdf_bytes
        except Exception as e:
            raise Exception(f"Error converting SVG to PDF: {str(e)}")

    # pdf to png
    def convert_pdf_to_png(self, pdf_content: bytes) -> list[bytes]:
        try:
            pdf_document = fitz.open(stream=pdf_content, filetype="pdf")
            images = []
            mat = fitz.Matrix(2.0, 2.0)
            for page_num in range(len(pdf_document)):
                page = pdf_document.load_page(page_num)
                pix = page.get_pixmap(matrix=mat)
                png_data = pix.tobytes("png")
                images.append(png_data)
            pdf_document.close()
            return images
        except Exception as e:
            raise Exception(f"Error converting PDF to PNG: {str(e)}")

    # pdf to jpg
    def convert_pdf_to_jpg(self, pdf_content: bytes) -> list[bytes]:
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

    # pdf to image
    def convert_pdf_to_image(
        self, pdf_content: bytes, image_format: str = "PNG"
    ) -> list[bytes]:
        supported_formats = ["PNG", "JPG", "JPEG"]
        fmt = image_format.lower()
        if fmt == "jpeg":
            fmt = "jpg"
        if fmt.upper() not in supported_formats:
            raise ValueError(f"Unsupported image format: {image_format}")

        try:
            pdf_document = fitz.open(stream=pdf_content, filetype="pdf")
            images = []
            mat = fitz.Matrix(2.0, 2.0)
            for page_num in range(len(pdf_document)):
                page = pdf_document.load_page(page_num)
                pix = page.get_pixmap(matrix=mat)
                img_data = pix.tobytes(fmt)
                images.append(img_data)
            pdf_document.close()
            return images
        except Exception as e:
            raise Exception(f"Error converting PDF to image: {str(e)}")

    # pdf to docx
    def convert_pdf_to_docx(self, pdf_content: bytes) -> bytes:
        try:
            pdf_document = fitz.open(stream=pdf_content, filetype="pdf")

            doc = Document()
            for page_num in range(len(pdf_document)):
                page = pdf_document.load_page(page_num)
                text = page.get_text()
                doc.add_paragraph(text)
                doc.add_page_break()
            pdf_document.close()
            docx_stream = io.BytesIO()
            doc.save(docx_stream)
            docx_stream.seek(0)
            return docx_stream.read()
        except Exception as e:
            raise Exception(f"Error converting PDF to DOCX: {str(e)}")

    # image to svg
    def convert_image_to_svg(
        self, image_content: bytes, image_format: str = "PNG"
    ) -> bytes:
        try:
            image = Image.open(io.BytesIO(image_content))
            width, height = image.size

            # Convert image to base64 string
            svg_buffer = io.BytesIO()

            if image_format.upper() == "PNG":
                image.save(svg_buffer, format="PNG")
                mime_type = "image/png"
            elif image_format.upper() in ["JPG", "JPEG"]:
                if image.mode in ("RGBA", "LA", "P"):
                    image = image.convert("RGB")
                image.save(svg_buffer, format="JPEG")
                mime_type = "image/jpeg"
            else:
                image.save(svg_buffer, format="PNG")
                mime_type = "image/png"

            img_base64 = base64.b64encode(svg_buffer.getvalue()).decode("utf-8")

            # create SVG elements
            svg = Element("svg")
            svg.set("xmlns", "http://www.w3.org/2000/svg")
            svg.set("xmlns:xlink", "http://www.w3.org/1999/xlink")
            svg.set("width", str(width))
            svg.set("height", str(height))
            svg.set("viewBox", f"0 0 {width} {height}")
            svg.set("version", "1.1")

            # Add image element
            image_elem = SubElement(svg, "image")
            image_elem.set("x", "0")
            image_elem.set("y", "0")
            image_elem.set("width", str(width))
            image_elem.set("height", str(height))
            image_elem.set("href", f"data:{mime_type};base64,{img_base64}")
            image_elem.set("preserveAspectRatio", "xMidYMid meet")

            # convert SVG to bytes string with xml declaration
            svg_string = '<?xml version="1.0" encoding="UTF-8"?>\n'
            svg_string += tostring(svg, encoding="unicode")

            return svg_string.encode("utf-8")

        except Exception as e:
            raise Exception(f"Error converting {image_format} to SVG: {str(e)}")

    # png to svg
    def convert_png_to_svg(self, png_content: bytes) -> bytes:
        return self.convert_image_to_svg(png_content, image_format="PNG")

    # jpg to svg
    def convert_jpg_to_svg(self, jpg_content: bytes) -> bytes:
        return self.convert_image_to_svg(jpg_content, image_format="JPG")

    # svg to image
    def convert_svg_to_image(
        self,
        svg_content: bytes,
        output_format: str = "PNG",
        width: int = None,
        height: int = None,
    ) -> bytes:
        try:
            if output_format.upper() == "PNG":
                png_data = svg2png(
                    bytestring=svg_content, output_width=width, output_height=height
                )
                return png_data
            else:
                png_data = svg2png(
                    bytestring=svg_content, output_width=width, output_height=height
                )
                image = Image.open(io.BytesIO(png_data))

                output_buffer = io.BytesIO()

                if output_format.upper() in ["JPG", "JPEG"]:
                    # Convert to RGB for JPEG (remove alpha channel)
                    if image.mode in ("RGBA", "LA"):
                        background = Image.new("RGB", image.size, (255, 255, 255))
                        background.paste(
                            image,
                            mask=image.split()[-1] if image.mode == "RGBA" else None,
                        )
                        image = background
                    image.save(output_buffer, format="JPEG", quality=95)
                else:
                    image.save(output_buffer, format=output_format.upper())

                return output_buffer.getvalue()

        except Exception as e:
            raise Exception(f"Error converting SVG to {output_format}: {str(e)}")

    # svg to png
    def convert_svg_to_png(
        self, svg_content: bytes, width: int = None, height: int = None
    ) -> bytes:
        return self.convert_svg_to_image(svg_content, "PNG", width, height)

    # svg to jpg
    def convert_svg_to_jpg(
        self, svg_content: bytes, width: int = None, height: int = None
    ) -> bytes:
        return self.convert_svg_to_image(svg_content, "JPG", width, height)

    # mp4 to mp3
    def convert_mp4_to_mp3(self, mp4_content: bytes) -> bytes:
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video:
                temp_video.write(mp4_content)
                temp_video_path = temp_video.name

            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
                temp_audio_path = temp_audio.name

            video = VideoFileClip(temp_video_path)
            video.audio.write_audiofile(temp_audio_path)
            video.close()

            with open(temp_audio_path, "rb") as f:
                mp3_bytes = f.read()

            os.remove(temp_video_path)
            os.remove(temp_audio_path)

            return mp3_bytes

        except Exception as e:
            raise Exception(f"Error converting MP4 to MP3: {str(e)}")


class FileCompressor:

    def __init__(self, compression_percentage: int):
        self.quality = max(10, 100 - compression_percentage)

    def compress_image(self, file: bytes) -> bytes:
        with tempfile.NamedTemporaryFile(delete=False) as temp_in:
            temp_in.write(file)
            temp_in.flush()

            img = Image.open(temp_in.name)
            format = img.format

            with tempfile.NamedTemporaryFile(
                suffix=f".{format.lower()}", delete=False
            ) as temp_out:
                if format.upper() == "JPEG":
                    img.save(temp_out.name, format, quality=self.quality)
                elif format.upper() == "PNG":
                    compress_level = int((100 - self.quality) / 10)
                    img.save(temp_out.name, format, compress_level=compress_level)
                else:
                    img.save(temp_out.name, format)
                temp_out.seek(0)
                return temp_out.read()

    # def compress_audio(self, file: bytes) -> bytes:
    #     with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_in:
    #         temp_in.write(file)
    #         temp_in.flush()

    #         audio = AudioSegment.from_file(temp_in)

    #         with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_out:
    #             audio.export(temp_out.name, format="mp3", bitrate=f"{self.quality}k")
    #             temp_out.seek(0)
    #             return temp_out.read()

    def compress_video(self, file: bytes) -> bytes:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_in:
            temp_in.write(file)
            temp_in.flush()

            video = VideoFileClip(temp_in.name)
            with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as temp_out:
                video.write_videofile(
                    temp_out.name,
                    bitrate=f"{self.quality*1000}k",
                    audio_codec="aac",
                    logger=None,
                )
                return open(temp_out.name, "rb").read()
            

    def compress_pdf(self, file: bytes) -> bytes:
        temp_in_path = None
        temp_out_path = None
    
        try:
           with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_in:
               temp_in.write(file)
               temp_in_path = temp_in.name
        
           temp_out_fd, temp_out_path = tempfile.mkstemp(suffix=".pdf")
           os.close(temp_out_fd)
        
           with pikepdf.open(temp_in_path) as pdf:
               pdf.save(
                  temp_out_path,
                  compress_streams=True,
                  object_stream_mode=pikepdf.ObjectStreamMode.generate
                )
        
           with open(temp_out_path, "rb") as f:
                compressed_data = f.read()
        
           return compressed_data
    
        finally:
             if temp_in_path and os.path.exists(temp_in_path):
                try:
                    os.unlink(temp_in_path)
                except PermissionError:
                    pass 
        
             if temp_out_path and os.path.exists(temp_out_path):
                 try:
                     os.unlink(temp_out_path)
                 except PermissionError:
                     pass

    def compress(self, file: bytes, mime_type: str) -> bytes:
        if mime_type.startswith("image/"):
            return self.compress_image(file)
        elif mime_type.startswith("audio/"):
            return self.compress_audio(file)
        elif mime_type.startswith("video/"):
            return self.compress_video(file)
        elif mime_type == "application/pdf":
            return self.compress_pdf(file)
        else:
            raise ValueError("Unsupported file type")
