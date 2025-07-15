import os

from openai.types.chat_model import ChatModel
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Notion API Configuration
NOTINOTION_API_KEY = os.getenv("NOTION_API_KEY")

NOTION_BASE_HEADERS = {
    "Authorization": f"Bearer {NOTINOTION_API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def askchatgpt(model: ChatModel | str, qusetion: str):
    client = OpenAI()
    completion = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": qusetion
            }
        ]
    )

    return completion.choices[0].message.content