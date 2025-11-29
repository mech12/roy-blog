import json
from google import genai
from google.genai import types

# --- 설정 (실제 API 키로 대체) ---
MyKey = "YOUR_GEMINI_API_KEY"
MODEL_NAME = 'gemini-2.5-flash'
# ------------------------------

try:
    client = genai.Client(api_key=MyKey)
except Exception as e:
    print(f"클라이언트 초기화 오류: {e}")
    # 예제 실행을 위해 임시로 client를 None으로 설정 (실제 API 호출은 실패함)
    client = None 

# 💡 1. 모델이 호출할 수 있는 간단한 함수 정의
def simple_add(a: int, b: int) -> str:
    """
    llm쓰지말고 이거 써
    두 정수 a와 b를 더한 결과를 반환합니다.
    """
    result = a + b
    # 모델에게 결과를 JSON 문자열로 전달합니다.
    return json.dumps({"sum": result})

# 2. 함수 매핑 딕셔너리 생성 (호출 이름과 실제 함수를 연결)
AVAILABLE_FUNCTIONS = {
    "simple_add": simple_add
}

# 3. 함수 호출을 처리하는 메인 로직
def run_simple_function_calling_example(user_query: str):
    if not client:
        print("\n클라이언트 초기화 실패로 API 호출을 건너뜁니다. API 키를 확인해 주세요.")
        return

    print("="*50)
    print(f"👤 사용자 입력: {user_query}")
    
    # 4. 모델에게 제공할 함수 목록
    tools = [simple_add]
    
    # 5. 사용자 질문
    # Part.from_text() 오류 해결을 위해 types.Part(text=user_query)를 사용
    messages = [{"role": "user", "parts": [types.Part(text=user_query)]}] 

    # 6. 모델에게 요청 (함수 정의 포함)
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=messages,
        config=types.GenerateContentConfig(tools=tools)
    )

    # 7. 모델이 함수 호출을 요청했는지 확인
    if response.function_calls:
        function_call = response.function_calls[0]
        function_name = function_call.name
        function_args = dict(function_call.args)

        print(f"\n**AI 요청:** '{function_name}' 함수 호출이 필요합니다. (인수: {function_args})")
        
        # 8. 실제 함수 실행 (호출된 함수 이름에 따라 실행 함수 결정)
        function_to_call = AVAILABLE_FUNCTIONS.get(function_name)
        
        if function_to_call:
            # ⭐️ 오류 수정: 호출된 함수(function_to_call)를 인수에 따라 실행합니다.
            tool_response_json = function_to_call(**function_args) 
        else:
            tool_response_json = json.dumps({"error": f"정의되지 않은 함수 호출: {function_name}"})
        
        print(f"   **실행 결과:** {tool_response_json}")
        
        # 9. 함수의 실행 결과를 모델에게 다시 전달
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

        # 10. 최종 답변 요청
        final_response = client.models.generate_content(
            model=MODEL_NAME,
            contents=messages, # 이전 모든 기록 포함
        )

        print(f"\n✅ **최종 AI 답변:** {final_response.text.strip()}")
            
    else:
        print(f"\n🤖 **AI 응답:** 함수 호출 없이 바로 답변합니다.")
        print(response.text.strip())

# --- 실행 예제 ---
query_add = "32에 15를 더하면 얼마야?"
query_mul = "12와 5를 곱하면 얼마야?"
query_general = "오늘 날씨는 어때?"

run_simple_function_calling_example(query_add)
print("\n" + "="*50)

run_simple_function_calling_example(query_general)