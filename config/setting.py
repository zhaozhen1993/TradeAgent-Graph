import os

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

load_dotenv()

API_KEY = os.getenv("ALIAPI")
BASE_URL = os.getenv("BASEURL")
MODEL = os.getenv("MODEL")


llm = init_chat_model(
    model=MODEL,
    model_provider="openai",
    api_key=API_KEY,
    base_url=BASE_URL,
)

# message = llm.invoke("你是谁？")
# print(message)