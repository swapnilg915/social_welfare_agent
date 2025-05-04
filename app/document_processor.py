import os
from io import BytesIO
import pdfplumber
import pytesseract
from PIL import Image
from pdf2image import convert_from_path


class DocumentProcessor:
    def __init__(self):
        pass
    
    def extract_text_from_upload(self, file):
        """Extract text from an uploaded file object (Flask Upload)."""
        filename = file.filename.lower()

        if filename.endswith(".pdf"):
            return self._extract_from_pdf_upload(file)
        elif filename.endswith((".jpg", ".jpeg", ".png")):
            return self._extract_from_image_upload(file)
        else:
            raise ValueError("Unsupported file format (only PDF, JPG, PNG allowed)")
        
    def _extract_from_pdf_upload(self, file):
        try:
            file_bytes = file.read()
            file.seek(0)  # Reset file pointer for future use

            with pdfplumber.open(BytesIO(file_bytes)) as pdf:
                text = " ".join(page.extract_text() for page in pdf.pages if page.extract_text())

            if text.strip():
                return text
            else:
                # fallback to OCR
                images = convert_from_bytes(file_bytes)
                ocr_text = " ".join([pytesseract.image_to_string(img) for img in images])
                return ocr_text

        except Exception as e:
            raise ValueError(f"Failed to process PDF: {str(e)}")

    def _extract_from_image_upload(self, file):
        try:
            img = Image.open(file.stream)
            text = pytesseract.image_to_string(img)
            return text
        except Exception as e:
            raise ValueError(f"Failed to process image: {str(e)}")
        
    def extract_text_from_file(self, file_path):
        if file_path.endswith(".pdf"):
            try:
                text = self._extract_text_from_pdf(file_path)
                if text.strip():
                    return text
                else:
                    # fallback to OCR
                    text = self._extract_text_from_scanned_pdf(file_path)
                    return text
            except Exception as e:
                raise ValueError(f"Failed to process file {file_path}: {str(e)}")

    def _extract_text_from_pdf(self, file_path):
        """Extract text from digitally created PDFs."""
        text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text

    def _extract_text_from_scanned_pdf(self, file_path):
        """Use OCR if digital text is not found."""
        images = convert_from_path(file_path)
        ocr_text = ""
        for img in images:
            ocr_text += pytesseract.image_to_string(img) + "\n"
        return ocr_text

    def process_folder(self, folder_path):
        """Process all PDFs in a folder."""
        extracted_docs = {}
        for file_name in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file_name)
            if os.path.isfile(file_path) and file_name.lower().endswith(".pdf"):
                print(f"Processing {file_name} ...")
                text = self.extract_text_from_file(file_path)
                extracted_docs[file_name] = text
        return extracted_docs