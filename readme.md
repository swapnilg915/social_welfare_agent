# Social Support Automation System (Agentic AI)

This project automates the evaluation of government social support applications using an Agentic AI workflow. It processes uploaded documents, classifies them, extracts critical fields, validates the data, and generates a structured profile and preliminary AI decision.

---

## Key Features

- Upload and parse scanned or digital documents (PDF, JPG, PNG)
- Modular agents for classification, extraction, validation, and decision-making
- OCR support using Tesseract and PDFPlumber
- Agentic workflow orchestrated using CrewAI and LangChain
- LLM-powered decisions with explanations using OpenAI models
- Streamlit frontend for upload and optional human review

---

## Tech Stack

| Component         | Technology                         |
|------------------|-------------------------------------|
| Agent Engine     | CrewAI, LangChain, OpenAI API       |
| Backend API      | Flask (Python 3.10)                 |
| Frontend UI      | Streamlit                           |
| OCR              | Tesseract OCR, pdfplumber           |
| Containerization | Docker                              |
| Data Storage     | MongoDB                             |
| Observability    | Langfuse                            |

---

## AI Pipeline Overview
The application uses CrewAI to orchestrate a multi-agent workflow. Each agent is responsible for a specific task:

Document Extractor – Extracts raw text from PDFs or images

Document Classifier – Classifies document type using ML model

Entity Extractor – Extracts fields like name, income, DOB, etc.

Validator – Checks for cross-document consistency

Profile Builder – Builds the final structured profile

Decision Maker – Returns a final decision using LLM

The results are returned as structured JSON: applicant_profile and llm_decision.


## Installation (Local Development)

1. Clone the repository

repo -> https://github.com/swapnilg915/social_welfare_agent
git clone https://github.com/swapnilg915/social_welfare_agent.git
cd social_welfare_agent

2. Create a virtual environment and install dependencies

python3 -m venv env_3.10
source env_3.10/bin/activate
pip install -r requirements.txt

3. Install OCR dependencies (Ubuntu)

sudo apt-get update
sudo apt-get install -y tesseract-ocr poppler-utils

## Running the Application

1. Start the Flask backend

python app/api.py

This will start the backend at http://localhost:5000


2. In a new terminal

streamlit run frontend/upload_documents.py

Visit http://localhost:8501 in your browser.

3. Human Supervisor Review App

streamlit run frontend/chat_with_case.py


4. Docker (Backend)

Build image -> docker build -t social-welfare-agent:latest .
Run container -> docker run -p 5000:5000 --env-file .env social-welfare-agent:latest


### Mongo

# Installation
    # For macOS
        brew tap mongodb/brew
        brew install mongodb-community@7.0
        brew services start mongodb-community@7.0

    # For Ubuntu
        # Import the public key
        curl -fsSL https://pgp.mongodb.com/server-7.0.asc | sudo gpg -o /usr/share/keyrings/mongodb-server-7.0.gpg --dearmor

        # Add MongoDB repo
        echo "deb [ signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list

        # Update & install
        sudo apt update
        sudo apt install -y mongodb-org

        # Start the service
        sudo systemctl start mongod
        sudo systemctl enable mongod


# check data
    activate python environment
    python (enter)
    from pymongo import MongoClient
    client = MongoClient("mongodb://localhost:27017")
    db = client["social_support"]
    collection = db["cases"]

    # display all cases
    for case in collection.find():
        print(case)

    # delete all cases
    collection.delete_many({})

    or download mongoDB compass and create a connection using -> "mongodb://localhost:27017"
    you will be able to see all cases data, files stored, modify/edit/delete/add data


    ### Langfuse
    go to -> https://cloud.langfuse.com
    create your account
    create api credentials with public key and secret key
    create a organization, then project
    once we process applicant documents, we can go to langfuse dashbaord and we will be able to see all llm calls, and their details like prompt, cost, latency details etc.



