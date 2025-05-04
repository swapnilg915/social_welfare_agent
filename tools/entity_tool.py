# tools/entity_tool.py

from crewai.tools import tool
import re
from pydantic import BaseModel
import pdfplumber
from app.shared_state import UPLOADED_FILES
import pytesseract
from PIL import Image
import io
from pdf2image import convert_from_bytes

@tool("extract_entities_from_text")
def extract_entities(text: str, document_type: str) -> dict:
    """
    Extract relevant fields from text depending on document type.
    Returns a dictionary of extracted entities with document_type as top-level key.
    """
    top_level_entities = {}
    entities = {}

    try:
        if document_type == "application_form":
            name_match = re.search(r"Name:\s*(.*)", text)
            dob_match = re.search(r"Date of Birth:\s*(.*)", text)
            family_members_match = re.search(r"Family Members:\s*(\d+)", text)
            address_match = re.search(r"Address:\s*(.*)", text)
            employment_match = re.search(r"Employment Status:\s*(.*)", text)
            income_match = re.search(r"Monthly Income:\s*([0-9,]+)", text)

            entities["name"] = name_match.group(1).strip() if name_match else None
            entities["date_of_birth"] = dob_match.group(1).strip() if dob_match else None
            entities["family_members"] = int(family_members_match.group(1)) if family_members_match else None
            entities["address"] = address_match.group(1).strip() if address_match else None
            entities["employment_status"] = employment_match.group(1).strip() if employment_match else None
            entities["monthly_income"] = int(income_match.group(1).replace(",", "")) if income_match else None

        elif document_type == "bank_statement":
            lines = text.splitlines()
            salary_credit, total_credit, total_debit, opening_balance, closing_balance = 0, 0, 0, None, None

            for line in lines:
                if "Opening Balance" in line:
                    match = re.search(r"Opening Balance.*?(\d+[,.]?\d*)", line)
                    if match:
                        opening_balance = float(match.group(1).replace(",", ""))
                if "Closing Balance" in line:
                    match = re.search(r"Closing Balance.*?(\d+[,.]?\d*)", line)
                    if match:
                        closing_balance = float(match.group(1).replace(",", ""))
                if "Salary" in line:
                    match = re.search(r"Salary.*?(\d+[,.]?\d*)", line)
                    if match:
                        salary_credit += float(match.group(1).replace(",", ""))
                if "Credit" in line:
                    match = re.search(r"Credit.*?(\d+[,.]?\d*)", line)
                    if match:
                        total_credit += float(match.group(1).replace(",", ""))
                if "Debit" in line:
                    match = re.search(r"Debit.*?(\d+[,.]?\d*)", line)
                    if match:
                        total_debit += float(match.group(1).replace(",", ""))

            entities.update({
                "opening_balance": opening_balance,
                "closing_balance": closing_balance,
                "monthly_salary": salary_credit,
                "total_credit": total_credit,
                "total_debit": total_debit
            })

        elif document_type == "credit_report":
            credit_score_match = re.search(r"Credit Score:\s*(\d+)", text)
            late_payments_match = re.search(r"Late Payments:\s*(\d+)", text)

            entities["credit_score"] = int(credit_score_match.group(1)) if credit_score_match else None
            entities["late_payments"] = int(late_payments_match.group(1)) if late_payments_match else 0

        elif document_type == "national_id":
            national_id_match = re.search(r"ID Number:\s*([\d\-]+)", text)
            address_match = re.search(r"Address:\s*(.*)", text)

            entities["national_id_number"] = national_id_match.group(1).strip() if national_id_match else None
            entities["address"] = address_match.group(1).strip() if address_match else None

        elif document_type == "emirates_id_image":
            file = UPLOADED_FILES.get(text)
            if not file:
                return {document_type: {"error": f"File {text} not found"}}
            file.seek(0)
            image = Image.open(io.BytesIO(file.read()))
            eid_text = pytesseract.image_to_string(image)

            entities["emirates_id_text"] = eid_text
            entities["full_name"] = re.search(r"Name[:\s]*([A-Za-z\s]+)", eid_text).group(1).strip() if re.search(r"Name[:\s]*([A-Za-z\s]+)", eid_text) else None
            entities["id_number"] = re.search(r"ID[\s]*No[:\s]*([\d]+)", eid_text).group(1).strip() if re.search(r"ID[\s]*No[:\s]*([\d]+)", eid_text) else None
            entities["dob"] = re.search(r"DOB[:\s]*([0-9\-]+)", eid_text).group(1).strip() if re.search(r"DOB[:\s]*([0-9\-]+)", eid_text) else None
            entities["expiry"] = re.search(r"Expiry[:\s]*([0-9\-]+)", eid_text).group(1).strip() if re.search(r"Expiry[:\s]*([0-9\-]+)", eid_text) else None

        else:
            return {document_type: {"error": "Unknown document type."}}

    except Exception as e:
        return {document_type: {"error": f"Failed to extract entities: {str(e)}"}}

    top_level_entities[document_type] = entities
    return top_level_entities
