import json
import re
import uuid
from crewai import Crew, Task
from app.shared_state import UPLOADED_FILES
from tools.mongo_tool import MongoDBHandler

# initialize once
mongo = MongoDBHandler()

# Import agents
from agents.extractor_agent import document_extractor_agent
from agents.classifier_agent import document_classifier_agent
from agents.entity_extractor_agent import entity_extractor_agent
from agents.validator_agent import validator_agent
from agents.profile_builder_agent import profile_builder_agent
from agents.decision_maker_agent import decision_maker_agent


def try_fix_json(raw_text):
    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        # Try to fix common issues like single quotes or missing quotes
        fixed = raw_text.strip()
        fixed = re.sub(r"(?<!\")([a-zA-Z_][a-zA-Z0-9_ ]*)(?=\s*:)", r'"\1"', fixed)  # wrap keys in quotes
        fixed = fixed.replace("'", '"')  # convert single quotes to double quotes
        try:
            return json.loads(fixed)
        except Exception:
            return {"error": f"Invalid JSON format: {raw_text[:100]}..."}
        
def run_pipeline(uploaded_files: dict):
    # Save uploaded files globally
    UPLOADED_FILES.clear()
    UPLOADED_FILES.update(uploaded_files)

    if not uploaded_files:
        raise ValueError("No uploaded files found.")

    filenames = list(uploaded_files.keys())
    # Create one extract_text_task per document
    extract_text_tasks = [
        Task(
            description=f"Extract text from this exact file: {fname}. Use the tool to process it.",
            expected_output="Raw text extracted from the uploaded document.",
            agent=document_extractor_agent,
            input={"filename": fname}
        )
        for fname in filenames
    ]

    classify_document_task = Task(
        description="Classify each document into its correct type (Application Form, Bank Statement, Credit Report, National ID).",
        expected_output="List of document types for each uploaded document.",
        agent=document_classifier_agent
    )

    entity_extraction_task = Task(
        description="Extract key fields like name, date of birth, income, address, loan EMI, etc. from the classified documents.",
        expected_output="Dictionary of extracted entities categorized by document type.",
        agent=entity_extractor_agent
    )

    validation_task = Task(
        description="Check consistency of applicant information across different documents (e.g., names, income, addresses).",
        expected_output="Validation report indicating whether extracted fields are consistent.",
        agent=validator_agent
    )

    profile_building_task = Task(
        description="Assemble the validated fields into a final structured Applicant Profile JSON.",
        expected_output="Final Applicant Profile ready for decision making.",
        agent=profile_builder_agent,
        allow_repeat=True
    )

    decision_making_task = Task(
        description="Decide whether to Approve or Soft Decline the applicant based on their profile and validation report.",
        expected_output="Final Decision JSON with 'decision' and 'reason' fields.",
        agent=decision_maker_agent
    )

    crew = Crew(
        agents=[
            document_extractor_agent,
            document_classifier_agent,
            entity_extractor_agent,
            validator_agent,
            profile_builder_agent,
            decision_maker_agent
        ],
        tasks=[
            *extract_text_tasks,
            classify_document_task,
            entity_extraction_task,
            validation_task,
            profile_building_task,
            decision_making_task
        ],
        verbose=False
    )

    output = crew.kickoff()
    extracted_text = {}
    try:
        # Correct way to extract raw output text from document extractor tasks
        extracted_text = {
            fname: task.raw
            for fname, task in zip(uploaded_files.keys(), output.tasks_output[:len(uploaded_files)])
        }

        ######################## working            
        profile_raw = output.tasks_output[-2].raw
        decision_raw = output.tasks_output[-1].raw

        print("\n===== PROFILE RAW =====\n", profile_raw)
        print("\n===== DECISION RAW =====\n", decision_raw)

        profile = json.loads(profile_raw)
        decision = json.loads(decision_raw)
        #########################################

        # Parse profile
        # profile_raw = output.tasks_output[-2].raw
        # profile = json.loads(profile_raw)

        # # Re-run decision with full profile as input
        # decision_making_task.input = {
        #     "applicant_profile": profile
        # }
        # decision_output = decision_making_task.agent.run(
        #     task=decision_making_task,
        #     context={},
        # )

        # decision = json.loads(decision_output)

        # profile = try_fix_json(output.tasks_output[-2].raw)
        # decision = try_fix_json(output.tasks_output[-1].raw)
    except Exception as e:
        profile = {"error": f"Failed to parse profile: {str(e)}"}
        decision = {"decision": "Unknown", "reason": str(e)}

    case_id = str(uuid.uuid4())
    try:
        print("***"*32)
        print("\n extracted_text --- ", extracted_text)
        print("***"*32)
        mongo.save_case(case_id, uploaded_files, profile, decision, extracted_text)
    except Exception as e:
        print(f"[MongoDB Save Error] {e}")

    return {
        "case_id": case_id,
        "applicant_profile": profile,
        "llm_decision": decision
    }
