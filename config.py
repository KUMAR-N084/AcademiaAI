import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_DEFAULT_MODEL = "gpt-4o-mini"
GROQ_DEFAULT_MODEL = "llama-3.1-8b-instant"
GROQ_BASE_URL = "https://api.groq.com/openai/v1"


def _configured_api_key():
    return os.getenv("OPENAI_API_KEY") or os.getenv("GROQ_API_KEY")


def _default_base_url(api_key):
    if api_key and api_key.startswith("gsk_"):
        return GROQ_BASE_URL
    return None


def _default_model(api_key):
    if api_key and api_key.startswith("gsk_"):
        return GROQ_DEFAULT_MODEL
    return OPENAI_DEFAULT_MODEL


class Config:
    _api_key = _configured_api_key()
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/academic_assistant")
    OPENAI_API_KEY = _api_key
    OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL") or _default_base_url(_api_key)
    OPENAI_MODEL = os.getenv("OPENAI_MODEL") or _default_model(_api_key)
    FLASK_ENV = os.getenv("FLASK_ENV", "development")
    DEBUG = FLASK_ENV == "development"
    MONGO_MOCK = False


class TestConfig(Config):
    TESTING = True
    MONGO_URI = "mongodb://localhost:27017/academic_assistant_test"
    WTF_CSRF_ENABLED = False
    MONGO_MOCK = True
