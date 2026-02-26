from openai import OpenAI
from config import config

client = OpenAI(api_key=config.MODEL_API_KEY)

models = client.models.list()
for model in models.data:
    if "gpt" in model.id:
        print(f"- {model.id}")
