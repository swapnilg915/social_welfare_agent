from crewai.tools import tool
from pydantic import BaseModel
import pandas as pd
import pdfplumber
import pytesseract
from pdf2image import convert_from_bytes
from app.shared_state import UPLOADED_FILES
from PIL import Image
from PIL import ImageOps, ImageFilter

import io

pytesseract.pytesseract.tesseract_cmd = "/opt/homebrew/bin/tesseract"

class ExtractTextInput(BaseModel):
    filename: str

@tool("extract_text_from_document")
def extract_text_tool(filename: str) -> str:
    """
    Extract text from a PDF or image file using OCR and PDF tools.
    Handles both digital PDFs and scanned images.
    """
    file = UPLOADED_FILES.get(filename)
    print("***"*32)
    print(f"\n\n\n[ExtractorTool] Received filename: {filename}")
    print(f"\n\n\n[ExtractorTool] Available files: {list(UPLOADED_FILES.keys())}")
    print("***"*32)

    if file is None:
        return f"❌ Error: File '{filename}' not found in memory."

    try:
        file.seek(0)

        if filename.endswith(".pdf"):
            try:
                with pdfplumber.open(file) as pdf:
                    text = "\n".join(
                        page.extract_text() or "" for page in pdf.pages
                    )
                if text.strip():
                    return text
            except Exception:
                pass

            file.seek(0)
            images = convert_from_bytes(file.read())
            return "\n".join(pytesseract.image_to_string(img) for img in images)

        elif filename.lower().endswith((".jpg", ".jpeg", ".png")):
            file.seek(0)
            image = Image.open(io.BytesIO(file.read()))
            try:
                text = pytesseract.image_to_string(image, lang='eng', config='--psm 3')
                return text
            except Exception as e:
                print("❌ OCR failed:", str(e))
                return f"❌ OCR failed: {str(e)}"

        # elif filename.lower().endswith(("jpg", "jpeg", "png")):
        #     file.seek(0)

        #     print("\n\n\n APPLYING OCR on image --- ", filename)
        #     image = Image.open(io.BytesIO(file.read()))
        #     image = ImageOps.grayscale(image)
        #     image = image.filter(ImageFilter.SHARPEN)

        #     text =  pytesseract.image_to_string(image, lang='eng', config='--psm 6')
        #     print("\n\n\n OCR Text --- ", text)
        #     return text

        elif filename.endswith(".csv"):
            try:
                file.seek(0)
                df = pd.read_csv(io.BytesIO(file.read()))
                csv_data = df.to_string(index=False)
                print("\n\n\n csv_data --- ", csv_data)
                return csv_data
            except Exception as e:
                return f"❌ Failed to read CSV: {str(e)}"
        
        else:
            return "❌ Unsupported file format."

    except Exception as e:
        return f"❌ Failed to extract text from {filename}: {str(e)}"
