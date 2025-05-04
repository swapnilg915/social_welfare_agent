# agents/profile_builder_agent.py

from crewai import Agent
from tools.profile_tool import build_profile

profile_builder_agent = Agent(
    role="Profile Builder Agent",
    goal="Build a complete applicant profile from extracted and validated information.",
    backstory="You are a skilled case processor working in the government social welfare department. You combine different pieces of extracted data into a clean, structured applicant profile, ready for decision-making.",
    tools=[build_profile],
    verbose=False
)
