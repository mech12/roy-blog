#https://platform.openai.com/chat
# .venv/bin/python day-1/chapter_2/connecting.py
# python day-1/chapter_2/connecting.py
import os
from openai import OpenAI
from dotenv import load_dotenv

# Load config from .env file
load_dotenv()
client = OpenAI(
    base_url=os.getenv('MSA_LLM_API_BASE', 'http://10.10.20.92:8009/v1'),
    api_key=os.environ['MSA_LLM_API_KEY'],
)

# Example function to query ChatGPT
def ask_chatgpt(user_message):
    response = client.chat.completions.create(
        model=os.getenv('MSA_LLM_MODEL', '/models/gpt-oss-120b'),
        messages=[{"role": "system", "content": "당신은 유능한 어시스턴트입니다."},
                  {"role": "user", "content": user_message}],
        temperature=0.7,
        )       
    return response.choices[0].message.content

# Example usage
user = "프랑스의 수도는 어디인가요?"
response = ask_chatgpt(user)
print(response)
