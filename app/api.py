import json
import io
from flask import Flask, request, jsonify, send_file
from crew_runner import run_pipeline
from app.shared_state import UPLOADED_FILES
from tools.mongo_tool import MongoDBHandler
from app.rag_pipeline import setup_rag, ask_question

# initialize once
mongo = MongoDBHandler()

app = Flask(__name__)

# Temporary memory to store uploaded documents during a session
uploaded_files_memory = {}

@app.route("/upload_documents", methods=["POST"])
def upload_documents():
    global uploaded_files_memory
    uploaded_files_memory = {}
    files = request.files.getlist("documents")
    if not files:
        return jsonify({"error": "No documents uploaded."}), 400

    for file in files:
        uploaded_files_memory[file.filename] = io.BytesIO(file.read())

    return jsonify({"message": "Documents received successfully!"}), 200

@app.route("/run_pipeline", methods=["POST"])
def run_agentic_pipeline():
    global uploaded_files_memory
    if not uploaded_files_memory:
        return jsonify({"error": "No documents found. Upload first."}), 400

    try:
        result = run_pipeline(uploaded_files_memory)
        case_id = result.get("case_id")

        # ✅ Clear memory after use
        uploaded_files_memory = {}

        # After pipeline is done, trigger RAG vectorization
        setup_rag(case_id)

        return jsonify({
            "success": True,
            "result": result
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/case/<case_id>", methods=["GET"])
def fetch_case(case_id):
    try:
        case_data = mongo.get_case(case_id)
        if not case_data:
            return jsonify({"error": "Case not found"}), 404
        return jsonify(case_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/case/<case_id>/file/<filename>")
def get_case_file(case_id, filename):
    try:
        case = mongo.get_case(case_id)
        if not case:
            return jsonify({"error": "Case not found"}), 404

        file_entry = next((doc for doc in case["documents"] if doc["filename"] == filename), None)
        if not file_entry:
            return jsonify({"error": "File not found"}), 404

        file_id = file_entry["file_id"]
        file_bytes = mongo.get_file(file_id)

        return send_file(
            io.BytesIO(file_bytes),
            download_name=filename,
            as_attachment=False
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/case/<case_id>/ask", methods=["POST"])
def ask_question_for_case(case_id):
    try:
        data = request.json
        query = data.get("query")
        if not query:
            return jsonify({"error": "Missing query field"}), 400

        response = ask_question(case_id, query)
        return jsonify({"answer": response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# @app.route("/cases", methods=["GET"])
# def list_all_cases():
#     try:
#         # Fetch all cases
#         cases = list(mongo.cases.find({}, {"_id": 1, "applicant_profile": 1, "llm_decision": 1}))
        
#         # Convert ObjectId to string explicitly (if needed)
#         formatted_cases = []
#         for case in cases:
#             case["case_id"] = str(case["_id"])
#             del case["_id"]  # Remove _id since we use case_id
#             formatted_cases.append(case)

#         return jsonify({"cases": formatted_cases})
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

@app.route("/cases", methods=["GET"])
def list_all_cases():
    try:
        cases = list(mongo.cases.find({}, {"_id": 1, "applicant_profile": 1, "llm_decision": 1, "documents": 1}))
        formatted_cases = []

        for case in cases:
            case_id = str(case["_id"])
            del case["_id"]

            # Ensure documents field is a list and convert ObjectId to str
            docs = case.get("documents", [])
            for doc in docs:
                if "file_id" in doc:
                    doc["file_id"] = str(doc["file_id"])

            formatted_cases.append({
                "case_id": case_id,
                "applicant_profile": case.get("applicant_profile", {}),
                "llm_decision": case.get("llm_decision", {}),
                "documents": docs
            })

        return jsonify({"cases": formatted_cases})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
