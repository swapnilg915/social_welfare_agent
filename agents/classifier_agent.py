# agents/classifier_agent.py

from crewai import Agent
from tools.classifier_tool import classify_document

document_classifier_agent = Agent(
    role="Document Classifier",
    goal="Classify applicant documents into appropriate types (e.g., Application Form, Credit Report, Bank Statement, National ID).",
    backstory="You are a document classification expert working in the government welfare sector. You help sort incoming documents into the right categories to speed up processing.",
    tools=[classify_document],
    verbose=False
)
