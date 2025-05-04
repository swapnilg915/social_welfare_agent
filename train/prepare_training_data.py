import os
import pandas as pd
from app.document_processor import DocumentProcessor

# Define which label each file represents
LABEL_MAPPING = {
    # Old files from applicant_1 and applicant_2
    "application_form.pdf": "application_form",
    "national_id.pdf": "national_id",
    "bank_statement.pdf": "bank_statement",
    "credit_report.pdf": "credit_report",

    # Your new files from Swapnil_Gaikwad
    "application.pdf": "application_form",
    "eid_front.jpg": "national_id",
    "AccountStatement.pdf": "bank_statement",
    "credit_report.pdf": "credit_report",
    "Emirates_ID.pdf": "national_id"
}

def extract_documents(folder_path, applicant_tag):
    processor = DocumentProcessor()
    documents = []

    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)

        if file_name.lower().endswith(('.pdf', '.jpg', '.jpeg', '.png')):
            text = processor.extract_text_from_file(file_path)
            label = LABEL_MAPPING.get(file_name, "unknown")
            documents.append({
                "applicant": applicant_tag,
                "file_name": file_name,
                "text": text,
                "label": label
            })
    return documents

def main():
    all_documents = []

    # Process applicant 1
    applicant_1_docs = extract_documents("../social_support_system/data/applicant_1/", "applicant_1")
    all_documents.extend(applicant_1_docs)

    # Process applicant 2
    applicant_2_docs = extract_documents("../social_support_system/data/applicant_2/", "applicant_2")
    all_documents.extend(applicant_2_docs)

    # Process Swapnil Gaikwad
    swapnil_docs = extract_documents("../social_support_system/data/Swapnil_Gaikwad/", "swapnil_gaikwad")
    all_documents.extend(swapnil_docs)

    # Create DataFrame
    df = pd.DataFrame(all_documents)
    df.to_csv("../social_support_system/data/training_data.csv", index=False)
    print("✅ Extracted data and saved to data/training_data.csv")

if __name__ == "__main__":
    main()
