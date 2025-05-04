# rag_pipeline.py

import os
import uuid
from typing import List
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.schema import Document
from langchain.docstore.document import Document
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from app.config import load_config
from tools.mongo_tool import MongoDBHandler

# Load config
config = load_config()
os.environ["OPENAI_API_KEY"] = config["openai_api_key"]

# Init once
mongo = MongoDBHandler()
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.2)
embeddings = OpenAIEmbeddings()
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)

VECTOR_DIR = "vector_store"


def get_documents_from_case(case_id: str) -> List[Document]:
    case = mongo.get_case(case_id)
    raw_texts = case.get("extracted_text", {})  # filename -> text

    if not raw_texts:
        raise ValueError(f"No extracted_text found in case {case_id}")

    documents = []
    for fname, content in raw_texts.items():
        if not content.strip():
            continue  # Skip empty content
        chunks = text_splitter.create_documents([content])
        for doc in chunks:
            doc.metadata = {"filename": fname, "case_id": case_id}
        documents.extend(chunks)

    if not documents:
        raise ValueError(f"No valid document chunks found for case {case_id}")

    return documents


# def setup_rag(case_id: str):
#     documents = get_documents_from_case(case_id)
#     case_vector_dir = os.path.join(VECTOR_DIR, case_id)
#     os.makedirs(case_vector_dir, exist_ok=True)
#     Chroma.from_documents(documents, embedding=embeddings, persist_directory=case_vector_dir)


def summarize_json(key: str, value: dict) -> str:
    """Flatten and format nested JSON as readable text"""
    lines = [f"== {key.upper()} =="]
    for k, v in value.items():
        if isinstance(v, dict):
            lines.append(f"{k}:")
            for sub_k, sub_v in v.items():
                lines.append(f"  - {sub_k}: {sub_v}")
        else:
            lines.append(f"{k}: {v}")
    return "\n".join(lines)

def setup_rag(case_id: str):
    documents = get_documents_from_case(case_id)

    case = mongo.get_case(case_id)
    if not case:
        raise ValueError(f"Case {case_id} not found in MongoDB")

    # Add applicant_profile summary
    profile_text = summarize_json("applicant_profile", case.get("applicant_profile", {}))
    documents.extend(text_splitter.create_documents([profile_text]))

    # Add llm_decision reasoning
    decision_text = summarize_json("llm_decision", case.get("llm_decision", {}))
    documents.extend(text_splitter.create_documents([decision_text]))

    # Store vectors
    case_vector_dir = os.path.join(VECTOR_DIR, case_id)
    os.makedirs(case_vector_dir, exist_ok=True)
    Chroma.from_documents(documents, embedding=embeddings, persist_directory=case_vector_dir)


def get_rag_chain_for_case(case_id: str):
    case_vector_dir = os.path.join(VECTOR_DIR, case_id)
    vectordb = Chroma(persist_directory=case_vector_dir, embedding_function=embeddings)
    retriever = vectordb.as_retriever()
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        return_source_documents=True
    )
    return qa_chain


def ask_question(case_id: str, query: str) -> str:
    chain = get_rag_chain_for_case(case_id)
    # result = chain.run(query)
    # return result
    response = chain.invoke({"query": query})
    return response["result"]
