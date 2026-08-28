import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("AI_PROVIDER_API_KEY"))

MODEL = "openai/gpt-oss-120b"


def call_llm(system_prompt: str, user_prompt: str) -> str:
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
        response_format={"type": "json_object"},
    )
    return response.choices[0].message.content