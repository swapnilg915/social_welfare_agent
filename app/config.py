import os
from dotenv import load_dotenv
load_dotenv()

def load_config():
    return {
        "openai_api_key": os.getenv("OPENAI_API_KEY"),
        "langfuse": {
            "public_key": os.getenv("LANGFUSE_PUBLIC_KEY"),
            "secret_key": os.getenv("LANGFUSE_SECRET_KEY"),
            "host": os.getenv("LANGFUSE_HOST"),
        }
    }
