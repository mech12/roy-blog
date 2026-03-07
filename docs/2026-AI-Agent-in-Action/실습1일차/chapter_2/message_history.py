import os
from openai import OpenAI
from dotenv import load_dotenv
import json

# Load API key from .env file
load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')
# Ensure the API key is available
if not api_key:
    raise ValueError("No API key found. Please check your .env file.")
client = OpenAI(api_key=api_key)


# Example function to query ChatGPT
def ask_chatgpt(messages):
    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=messages,
        temperature=0.7,        
        )     
    
    response_model = response.model_dump()
    print(json.dumps(response_model, indent=4))  
    
    return response.choices[0].message.content


messages = [
    {"role": "system", "content": "당신은 유능한 어시스턴트 입니다. 응답은 반드시 JSON형태로 해주세요"}, # AI의 역할과 출력 형식 정의
    {"role": "user", "content": "프랑스의 수도는 어디인가요?"}, # 사용자의 첫 질문
    {"role": "assistant", "content": "프랑스의 수도는 파리입니다."}, # AI의 이전 답변 (문맥 유지용)
    {"role": "user", "content": "그곳에 대해 재미있는 사실을 알려줘"} # 사용자의 새로운 질문
]
response = ask_chatgpt(messages)
print(response)
