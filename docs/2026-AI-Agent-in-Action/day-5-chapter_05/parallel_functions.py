from openai import OpenAI
import json
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY", "none"),
    base_url=os.getenv("OPENAI_API_BASE"),
)
model_id = os.getenv("OPENAI_API_MODEL", "gpt-4o")

# 1. 실제 실행될 로컬 함수 (비즈니스 로직)
def recommend(topic, rating="good"):
    """다양한 주제에 대해 맞춤형 추천 정보를 제공합니다."""
    topic_lower = topic.lower()
    if "time travel" in topic_lower or "시간 여행" in topic_lower:
        return json.dumps({
            "topic": "시간 여행 영화",
            "recommendation": "백 투 더 퓨처 (Back to the Future)",
            "rating": rating
        }, ensure_ascii=False)
    elif "recipe" in topic_lower or "레시피" in topic_lower:
        return json.dumps({
            "topic": "레시피",
            "recommendation": "당신이 먹어본 것 중 가장 맛있는 스테이크 요리",
            "rating": rating
        }, ensure_ascii=False)
    elif "gift" in topic_lower or "선물" in topic_lower:
        return json.dumps({
            "topic": "선물",
            "recommendation": "최신형 노이즈 캔슬링 헤드폰",
            "rating": rating
        }, ensure_ascii=False)
    else:
        return json.dumps({"topic": topic, "recommendation": "적절한 추천을 찾지 못했습니다."}, ensure_ascii=False)

def run_conversation(user_input):
    # Step 1: 사용자 질문 및 도구(설계도) 정의
   
    
    messages = [{"role": "user", "content": user_input}]
    
    tools = [
        {
            "type": "function",
            "function": {
                "name": "recommend",
                "description": "사용자가 추천받고자 하는 영화의 주제나 장르 (예: 시간 여행, 로맨틱 코미디)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "topic": {
                            "type": "string",
                            "description": "추천을 받고자 하는 주제 (예: '시간 여행 영화', '요리 레시피')",
                        },
                        "rating": {
                            "type": "string",
                            "description": "추천 결과의 품질 등급",
                            "enum": ["good", "bad", "terrible"]
                        },
                    },
                    "required": ["topic"],
                },
            },
        }
    ]

    # 모델에게 첫 번째 요청 (함수 호출 여부 판단)
    response = client.chat.completions.create(
        model=model_id,
        messages=messages,
        tools=tools,
        tool_choice="auto",
    )
    
    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls

    # Step 2: 모델이 함수 호출을 결정했는지 확인
    if tool_calls:
        print("사용자 함수 호출")
        available_functions = {"recommend": recommend}
        messages.append(response_message) # 대화 흐름에 모델의 '함수 호출 의도' 추가

        # Step 3 & 4: 요청된 모든 함수 호출을 순회하며 실행
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call.function.arguments)
            
            # 실제 파이썬 함수 실행
            function_response = function_to_call(
                topic=function_args.get("topic"),
                rating=function_args.get("rating"),
            )
            
            # 실행 결과를 대화 기록에 추가 (tool 역할)
            messages.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": function_name,
                "content": function_response,
            })

        # 모든 함수 실행 결과를 들고 모델에게 최종 답변 요청
        second_response = client.chat.completions.create(
            model=model_id,
            messages=messages,
        )
        return second_response.choices[0].message.content
    
    return response_message.content


print("## 테스트 1: 일반적인 요청")
user1 = "시간 여행 영화 좀 추천해줄래?"
print(f"질문: {user1}\n결과: {run_conversation(user1)}\n")

print("## 테스트 2: 선호도가 포함된 요청")
user2 = "정말 재미있는(good) 시간 여행 영화로 추천해줘."
print(f"질문: {user2}\n결과: {run_conversation(user2)}\n")

print("## 테스트 3: llm스스로 대답")
user3 = "심심한데 영화 추천해줄래"
print(f"질문: {user3}\n결과: {run_conversation(user3)}\n")

