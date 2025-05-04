# tools/mongo_tool.py

from pymongo import MongoClient
from gridfs import GridFS
from bson import ObjectId
import datetime

class MongoDBHandler:
    def __init__(self, db_name="social_support", uri="mongodb://localhost:27017/"):
        self.client = MongoClient(uri)
        self.db = self.client[db_name]
        self.fs = GridFS(self.db)
        self.cases = self.db["cases"]

    def save_case(self, case_id: str, uploaded_files: dict, applicant_profile: dict, llm_decision: dict, extracted_text=None) -> str:
        # Upload documents to GridFS and get their ids
        doc_refs = []
        for fname, fbytes in uploaded_files.items():
            fbytes.seek(0)
            fid = self.fs.put(fbytes.read(), filename=fname)
            doc_refs.append({"filename": fname, "file_id": fid})

        case = {
            "_id": case_id,
            "applicant_profile": applicant_profile,
            "llm_decision": llm_decision,
            "documents": doc_refs,
            "created_at": datetime.datetime.utcnow()
        }

        # Only save if it's a dict (avoid empty strings or malformed inputs)
        if extracted_text and isinstance(extracted_text, dict):
            case["extracted_text"] = extracted_text

        self.cases.insert_one(case)
        return case_id

    def get_case(self, case_id: str) -> dict:
        return self.cases.find_one({"_id": case_id}, {"_id": 0})

    def get_file(self, file_id: str) -> bytes:
        return self.fs.get(ObjectId(file_id)).read()

    def get_file_metadata(self, file_id: str) -> dict:
        f = self.fs.get(ObjectId(file_id))
        return {"filename": f.filename, "upload_date": f.upload_date}