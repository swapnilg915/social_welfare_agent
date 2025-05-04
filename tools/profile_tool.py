# tools/profile_tool.py

# from crewai_tools import tool
from crewai.tools import tool

@tool("build_applicant_profile")
def build_profile(extracted_entities: dict, validation_report: dict) -> dict:
    """
    Build the final structured applicant profile from extracted data.
    Also attach a simple validation summary.
    """

    profile = {}
    try:
        # Collect key fields if available
        profile["name"] = extracted_entities.get("application_form", {}).get("name")
        profile["date_of_birth"] = extracted_entities.get("application_form", {}).get("date_of_birth")
        profile["address"] = extracted_entities.get("application_form", {}).get("address") or \
                             extracted_entities.get("national_id", {}).get("address")

        profile["employment_status"] = extracted_entities.get("application_form", {}).get("employment_status")
        profile["monthly_income"] = extracted_entities.get("application_form", {}).get("monthly_income")
        profile["monthly_salary_from_bank"] = extracted_entities.get("bank_statement", {}).get("monthly_salary_from_bank")
        profile["loan_emi"] = extracted_entities.get("bank_statement", {}).get("loan_emi")
        profile["credit_score"] = extracted_entities.get("credit_report", {}).get("credit_score")
        profile["late_payments"] = extracted_entities.get("credit_report", {}).get("late_payments")
        profile["family_members"] = extracted_entities.get("application_form", {}).get("family_members")
        profile["national_id_number"] = extracted_entities.get("national_id", {}).get("national_id_number")

        # Attach Validation Flags
        profile["validation_summary"] = validation_report

        print("***"*32)
        print("\n\n\n build_profile --- ", profile)
        print("***"*32)

    except Exception as e:
        profile["error"] = f"Failed to build profile: {str(e)}"

    return profile
