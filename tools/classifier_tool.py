from crewai.tools import tool
import pickle
import os

MODEL_PATH = "models/svm_model.pkl"

if os.path.exists(MODEL_PATH):
    with open(MODEL_PATH, "rb") as f:
        svm_model = pickle.load(f)
else:
    svm_model = None

@tool("classify_document_type")
def classify_document(text: str) -> str:
    """
    Classify the uploaded document into types like 'application_form', 'credit_report', etc.
    """
    if not svm_model:
        return "❌ Model not found. Please ensure the SVM model is trained and placed in 'models/svm_model.pkl'."
    try:
        prediction = svm_model.predict([text])
        return prediction[0]
    except Exception as e:
        return f"❌ Failed to classify document: {str(e)}"
