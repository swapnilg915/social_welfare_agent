# agents/extractor_agent.py

from crewai import Agent
from tools.extractor_tool import extract_text_tool

document_extractor_agent = Agent(
    role="Document Extractor",
    goal="Extract text from applicant documents (PDFs and images)",
    backstory="You are an expert in document processing and OCR for government use cases. You ensure that text is extracted accurately from both digital and scanned files.",
    tools=[extract_text_tool],
    verbose=False
)
