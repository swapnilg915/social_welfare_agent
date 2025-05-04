# agents/validator_agent.py

from crewai import Agent
from tools.validator_tool import validate_entities

validator_agent = Agent(
    role="Validation Agent",
    goal="Check consistency of applicant information across multiple documents.",
    backstory="You work in the quality control department of a government social welfare program. You ensure that information extracted from various documents matches and is trustworthy before proceeding to decision making.",
    tools=[validate_entities],
    verbose=False
)
