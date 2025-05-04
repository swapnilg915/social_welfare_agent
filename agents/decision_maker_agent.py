import os
from crewai import Agent
from langchain_openai import ChatOpenAI
from langfuse.callback import CallbackHandler
from app.config import load_config
config = load_config()

# llm = ChatOpenAI(model="gpt-4", temperature=0.2, openai_api_key=config["openai_api_key"])
# llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.2, openai_api_key=config["openai_api_key"])


# os.environ["OPENAI_API_KEY"] = config["openai_api_key"]  # ✅ Set it here

callbacks = [CallbackHandler(
    public_key=config["langfuse"]["public_key"],
    secret_key=config["langfuse"]["secret_key"],
    host=config["langfuse"]["host"]
)]


llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0.2,
    openai_api_key=config["openai_api_key"],
    callbacks=callbacks
)

decision_prompt = """
You are a government social support decision assistant.

Evaluate the full applicant profile, including the validation summary and extracted details from the following documents:
- Bank statement
- Application form
- Credit report
- National ID (if applicable)

Your task is to decide whether to APPROVE or DECLINE the application based on:
- Income level and consistency
- Employment status
- Credit score and payment history
- Loan obligations
- Family size
- Address and name consistency
- Any flagged validation issues

✅ You MUST return ONLY a **valid JSON** object, with **all keys in double quotes** (").

Example format (strictly follow this):

{
  "decision": "Approve",
  "reason": "The applicant has a stable job, sufficient income, a good credit score, and no inconsistencies in the documents."
}

DO NOT include any explanation, markdown, headings, or extra text. Just return the JSON block.
"""

decision_maker_agent = Agent(
    role="Social Welfare Decision Assistant",
    goal="Carefully recommend approval or soft-decline for applicants",
    backstory="You're an experienced government caseworker focused on fair social support distribution.",
    verbose=False,
    llm=llm,
    prompt_template=decision_prompt
)
