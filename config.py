import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    PROVIDER = os.getenv("PROVIDER", "openai").lower()
    MODEL_API_KEY = os.getenv("MODEL_API_KEY", "")
    MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4")

config = Config()
