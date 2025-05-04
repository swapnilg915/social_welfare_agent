# tools/validator_tool.py

from crewai.tools import tool

@tool("validate_extracted_data")
def validate_entities(extracted_entities: dict) -> dict:
    """
    Validate extracted fields across multiple documents.
    Check consistency for name, address, income, etc.
    Returns a validation report.
    """

    validation_report = {}

    try:
        # Ensure top-level input is a dict with doc_type keys
        if not isinstance(extracted_entities, dict):
            return {"status": "error", "error": "Input is not a dictionary"}

        # Check Name consistency
        names = []
        for doc_type, fields in extracted_entities.items():
            if isinstance(fields, dict) and fields.get("name"):
                names.append(fields["name"])

        validation_report["name_consistency"] = len(set(names)) == 1 if names else True

        # Check Address consistency
        addresses = []
        for doc_type, fields in extracted_entities.items():
            if isinstance(fields, dict) and fields.get("address"):
                addresses.append(fields["address"])

        validation_report["address_consistency"] = len(set(addresses)) == 1 if addresses else True

        # Check Monthly Income consistency
        declared_income = None
        bank_salary = None

        for doc_type, fields in extracted_entities.items():
            if not isinstance(fields, dict):
                continue
            if fields.get("monthly_income"):
                declared_income = fields["monthly_income"]
            if fields.get("monthly_salary_from_bank") or fields.get("salary"):
                bank_salary = fields.get("monthly_salary_from_bank") or fields.get("salary")

        if declared_income and bank_salary:
            variation = abs(declared_income - bank_salary) / max(declared_income, bank_salary)
            validation_report["income_consistency"] = variation <= 0.1
        else:
            validation_report["income_consistency"] = True

    except Exception as e:
        return {"status": "error", "error": f"Validation failed: {str(e)}"}

    return {"status": "validated", "issues": [], **validation_report}
