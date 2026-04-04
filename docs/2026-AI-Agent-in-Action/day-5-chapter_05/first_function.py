import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY", "none"),
    base_url=os.getenv("OPENAI_API_BASE"),
)
model_id = os.getenv("OPENAI_API_MODEL", "gpt-4o")

#함수의 설계도만 필요하다. 실제 함수는 gpt입장에서는 필요가 없다 
#내가 사용자가 만든 함수의 정보만 전달한다. => 보안이나 정교함 때문입니다. 내 파이썬 함수의 소스코드가 외부에 노출되는 것을 막고, AI에게 전달될 설명을 개발자가 더 세밀
#제미나이의 경우 함수만 만들면 자동으로 함수의 정보룰 전달한다. 
#만들기 어려울 경우에 미리 함수를 만들고 제미나이한테 함수의 정보를 만들어 달라고 한다 
tools=[
            {
                "type": "function",
                "function": {
                    "name": "recommend_movie", # 함수명을 더 명확하게 변경
                    "description": "다양한 주제에 대해 사용자에게 맞춤형 영화를 추천합니다.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "topic": {
                                "type": "string",
                                "description": "사용자가 추천받고자 하는 영화의 주제나 장르 (예: 시간 여행, 로맨틱 코미디)",
                            },
                            "rating": {
                                "type": "string",
                                "description": "사용자가 원하는 영화의 선호도 또는 평가 등급",
                                "enum": ["good", "bad", "terrible"]
                            },
                        },
                        "required": ["topic"], # 주제는 필수값으로 설정
                    },
                },
            }
        ]


def ask_chatgpt(user_message):    
    response = client.chat.completions.create(
        model=model_id,
        messages=[
            {"role": "system", "content": "당신은 사용자의 요청을 분석하여 적절한 도구를 선택하는 유능한 비서입니다."},
            {"role": "user", "content": user_message}
        ],
        temperature=0.7,
        tools=tools  #사용자 함수정보를 리스트형태로(여러개 보내야 하므로)전달한다. 
    )
    
    # 도구 호출이 있는지 확인하는 안전 코드를 추가했습니다.
    message = response.choices[0].message
    if message.tool_calls:
        return message.tool_calls[0].function
    else:
        return f"일반 응답: {message.content}"

# --- 실행 예시 ---
print("## 테스트 1: 일반적인 요청")
user1 = "시간 여행 영화 좀 추천해줄래?"
print(f"질문: {user1}\n결과: {ask_chatgpt(user1)}\n")

print("## 테스트 2: 선호도가 포함된 요청")
user2 = "정말 재미있는(good) 시간 여행 영화로 추천해줘."
print(f"질문: {user2}\n결과: {ask_chatgpt(user2)}\n")

print("## 테스트 3: llm스스로 대답")
user3 = "심심한데 영화 추천해줄래"
print(f"질문: {user3}\n결과: {ask_chatgpt(user3)}\n")