#conda activate llm_env
#pip install openai


MYKEY="YOUR_OPENAI_API_KEY"

from openai import OpenAI
# Image 라이브러리가 설치되어 있다면, 이미지를 바로 열어볼 수 있습니다.
# from PIL import Image
# import requests
# from io import BytesIO

# 클라이언트 초기화
client = OpenAI(api_key=MYKEY)

from openai import OpenAI
import json

# 클라이언트 초기화
client = OpenAI()

# 💡 모델이 호출할 수 있는 함수를 정의합니다.
def get_current_weather(city: str, unit: str = "celsius") -> str:
    """주어진 도시의 현재 날씨를 가져옵니다."""
    print(f"[Function Called: get_current_weather(city='{city}', unit='{unit}')]")
    
    # 실제 API 호출 대신 가상의 데이터를 반환합니다.
    if "seoul" in city.lower():
        return json.dumps({"city": "Seoul", "temperature": "15", "unit": unit, "forecast": "sunny"})
    elif "busan" in city.lower():
        return json.dumps({"city": "Busan", "temperature": "18", "unit": unit, "forecast": "cloudy"})
    else:
        return json.dumps({"city": city, "temperature": "22", "unit": unit, "forecast": "light rain"})

# 💡 함수 목록을 딕셔너리로 정의합니다. (함수 이름: 실제 함수)
available_functions = {
    "get_current_weather": get_current_weather,
}

def run_function_calling_example():
    """함수 호출(Tool Use) 예제 실행"""
    print("--- 3. 함수 호출 예제 시작 ---")

    # 1. 모델에게 전달할 함수 정의 (JSON Schema 형식)
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_current_weather",
                "description": "특정 도시의 현재 날씨를 가져옵니다.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "city": {
                            "type": "string",
                            "description": "날씨를 알고 싶은 도시 이름 (예: 서울, 부산)"
                        },
                        "unit": {
                            "type": "string",
                            "enum": ["celsius", "fahrenheit"],
                            "description": "온도 단위. 기본값은 섭씨(celsius)"
                        },
                    },
                    "required": ["city"],
                },
            },
        }
    ]

    # 2. 사용자 질문
    messages = [{"role": "user", "content": "서울의 현재 날씨는 어때? 단위는 섭씨로 알려줘."}]

    # 3. 모델에게 요청 (함수 정의 포함)
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        tools=tools,
        tool_choice="auto", # 모델이 함수 호출 여부를 결정하도록 함
    )

    response_message = response.choices[0].message
    
    # 4. 모델이 함수 호출을 요청했는지 확인
    if response_message.tool_calls:
        print("\n🤖 AI 응답: 함수 호출 요청을 받았습니다.")
        
        # 함수 호출 상세 정보 출력
        tool_calls = response_message.tool_calls
        messages.append(response_message) # 모델의 요청을 대화 기록에 추가
        
        # 함수 호출 실행
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call.function.arguments)

            print(f"  - 호출할 함수: {function_name}")
            print(f"  - 전달 인자: {function_args}")
            
            # 실제 함수 실행 및 결과 반환
            function_response = function_to_call(
                city=function_args.get("city"),
                unit=function_args.get("unit")
            )

            # 5. 함수의 실행 결과를 모델에게 다시 전달
            messages.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": function_response, # 함수의 JSON 결과
                }
            )

        # 6. 최종 답변 요청
        final_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages, # 이전 모든 기록 (요청, 응답, 함수 결과) 포함
        )

        final_answer = final_response.choices[0].message.content
        print(f"\n✅ 최종 AI 답변: {final_answer}")

    else:
        # 모델이 함수 호출 없이 바로 답변한 경우
        print("🤖 AI 응답: 함수 호출 없이 바로 답변합니다.")
        print(response_message.content)

    print("--- 함수 호출 예제 종료 ---\n")

# run_function_calling_example()