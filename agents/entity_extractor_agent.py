# agents/entity_extractor_agent.py

from crewai import Agent
from tools.entity_tool import extract_entities
from pydantic import BaseModel

class ExtractEntitiesInput(BaseModel):
    text: str
    document_type: str

entity_extractor_agent = Agent(
    role="Entity Extraction Agent",
    goal="Extract key applicant information from classified documents including ID, income, and bank activity.",
    backstory="You specialize in reading government forms, ID images, and financial statements to accurately extract structured data for downstream automation.",
    tools=[extract_entities],
    verbose=False
)
