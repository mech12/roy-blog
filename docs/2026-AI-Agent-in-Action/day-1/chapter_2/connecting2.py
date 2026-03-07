#https://platform.openai.com/chat
import os
from openai import OpenAI
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')
# Ensure the API key is available
if not api_key:
    raise ValueError("No API key found. Please check your .env file.")
client = OpenAI(api_key=api_key)

# Example function to query ChatGPT
def ask_chatgpt(user_message):
    response = client.chat.completions.create(
        model="gpt-4.1",  # gpt-4 turbo or a model of your preference
        messages=[{"role": "system", "content": "당신은 유능한 어시스턴트입니다."},
                  {"role": "user", "content": user_message}],
        temperature=0.7,
        )       
    return response.choices[0].message.content

# Example usage
user = "프랑스의 수도는 어디인가요?"
response = ask_chatgpt(user)
print(response)
