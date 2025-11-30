MyKey = "YOUR_GEMINI_API_KEY"

import json
from google import genai
from google.genai import types
# 환경변수 설정 (이전에 설정되었다고 가정)
try:
    client = genai.Client(api_key=MyKey)
except Exception as e:
    print(f"클라이언트 초기화 오류: {e}. API 키 설정을 확인하세요.")
    exit()

# 2. 사용할 모델 지정 (예: gemini-2.5-flash)
MODEL_NAME = 'gemini-2.5-flash'

# 1. 외부 시스템과 통신하는 실제 Python 함수
def get_current_weather(city: str) -> str:
    """
    주어진 도시의 현재 날씨 상태와 온도를 반환합니다.
    (실제로는 외부 API를 호출하지만, 여기서는 더미 데이터를 사용합니다.)
    """
    if "서울" in city:
        return json.dumps({"location": "서울", "temperature": "18°C", "forecast": "맑음"})
    elif "파리" in city:
        return json.dumps({"location": "파리", "temperature": "12°C", "forecast": "약간 흐림"})
    else:
        return json.dumps({"location": city, "temperature": "정보 없음", "forecast": "알 수 없음"})

# 2. LLM에게 제공할 함수의 JSON 스키마 (Tool Definition)
# Gemini 모델은 함수 호출을 위해 이 JSON 스키마를 이해해야 합니다.

weather_tool_schema = {
    "name": "get_current_weather",
    "description": "특정 도시의 현재 날씨를 확인합니다. 사용자의 질문에 도시명이 포함되어 있을 때만 호출해야 합니다.",
    "parameters": {
        "type": "object",
        "properties": {
            "city": {
                "type": "string",
                "description": "날씨를 알고 싶은 도시의 이름입니다 (예: 서울, 파리)"
            }
        },
        "required": ["city"]
    }
}

def run_function_calling_example(user_query: str):
    print("\n" + "="*50)
    print("🚀 예제 1: 함수 호출 (Function Calling)")
    print("="*50)
    print(f"👤 사용자 입력: {user_query}")
    
    # 1. 모델에게 제공할 함수 목록
    tools = [get_current_weather]
    
    # 2. 대화 기록 시작 (사용자 질문 포함)
    messages = [{"role": "user", "parts": [types.Part(text=user_query)]}]
    
    # 3. 모델에게 요청 (함수 정의 포함)
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=messages,
        config=types.GenerateContentConfig(tools=tools)
    )

    # 4. 모델이 함수 호출을 요청했는지 확인
    if response.function_calls:
        function_call = response.function_calls[0]
        function_name = function_call.name
        function_args = dict(function_call.args)

        print(f"\n🤖 AI 요청: '{function_name}' 함수 호출이 필요합니다.")
        
        # 5. 실제 함수 실행
        # 함수 이름과 인수를 사용하여 파이썬 함수를 호출합니다.
        if function_name == "get_flight_schedule":
            tool_response_json = get_current_weather(**function_args)
        else:
            tool_response_json = json.dumps({"error": "알 수 없는 함수입니다."})
        
        # 6. 함수의 실행 결과를 모델에게 다시 전달
        messages.append(response.candidates[0].content) # 모델의 요청 추가
        messages.append(
            types.Content(
                role='tool',
                parts=[
                    types.Part.from_function_response(
                        name=function_name, 
                        response={"result": tool_response_json}
                    )
                ]
            )
        )

        # 7. 최종 답변 요청
        final_response = client.models.generate_content(
            model=MODEL_NAME,
            contents=messages, # 이전 모든 기록 포함
        )

        print(f"\n✅ 최종 AI 답변:\n{final_response.text.strip()}")
            
    else:
        print(f"\n🤖 AI 응답: 함수 호출 없이 바로 답변합니다.")
        print(response.text.strip())


# 3. 실행 예제
question_1 = "지금 서울 날씨는 어때?"
print(f"--- [질문 1] {question_1} ---")
print(run_function_calling_example(question_1))

question_2 = "가장 좋아하는 동물은 무엇인가요?"
print(f"\n--- [질문 2] {question_2} ---")
print(run_function_calling_example(question_2))
