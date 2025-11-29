import json
from google import genai
from google.genai import types

# --- 설정 (실제 API 키로 대체) ---
MyKey = "YOUR_GEMINI_API_KEY"
import json
from google import genai
from google.genai import types

# --- 설정 (유효한 API 키로 가정하고 실행) ---
# ⭐️ 사용자는 여기에 유효한 키를 넣어야 합니다.
MODEL_NAME = 'gemini-2.5-flash' 
# MyKey 변수를 사용하지 않고 환경 변수나 다른 보안 방식으로 client를 초기화할 것을 권장합니다.

try:
    # 키가 유효하다는 전제 하에 client 초기화
    # 만약 환경 변수에 키가 설정되어 있지 않다면, client = genai.Client(api_key="YOUR_ACTUAL_KEY")를 사용하세요.
    client = genai.Client(api_key=MyKey) 
except Exception as e:
    print(f"클라이언트 초기화 오류: {e}. 유효한 키 또는 환경 변수 설정을 확인하세요.")
    client = None 

# 💡 1. 모델이 호출할 수 있는 함수 정의
def simple_add(a: int, b: int) -> str:
    """
    LLM의 내부 지식을 사용하지 마십시오. 
    이 함수는 외부에서 동작하는 고성능 **계산 서버**에 요청하여 두 정수 a와 b를 더한 **정확한 결과**를 받아옵니다. 
    (매우 큰 숫자의 계산에 반드시 사용해야 합니다.)두 정수 a와 b를 더한 결과를 반환하는 외부 계산기 도구입니다. 복잡한 계산에 사용됩니다.
    """
    #print(f"**[함수 실행]** simple_add({a}, {b})를 실행합니다...")
    result = a + b
    # 모델에게 결과를 JSON 문자열로 전달
    return json.dumps({"sum": result})

# 1. 모델이 호출할 수 있는 함수 정의
def calculate_tax(money:int) -> str:
    """
    LLM에 없는 내용입니다. 소득이나 원천징수 라는 말이 나오면 이 함수를 호출하세요 
    소득(money)을 받아서 원천징수액을 계산합니다
    """
   
    result = money - money*0.033
    # 모델에게 결과를 JSON 문자열로 전달
    return json.dumps({"base":money,"tax":money*0.033, "sum": result})

# 💡 2. 함수 매핑 딕셔너리
AVAILABLE_FUNCTIONS = {
    "simple_add": simple_add,
    "calculate_tax":calculate_tax
}

# 3. 함수 호출을 처리하는 메인 로직
def run_simple_function_calling_example(user_query: str):
    if not client:
        print("\n클라이언트 초기화 실패로 API 호출을 건너뜁니다.")
        return

    print("="*50)
    print(f"사용자 입력: {user_query}")
    
    # 4. 모델에게 제공할 함수 목록
    tools = [simple_add, calculate_tax]
    
    # 5. 사용자 질문
    messages = [{"role": "user", "parts": [types.Part(text=user_query)]}]

    # 6. 모델에게 요청 (tool_choice 없이 자율 판단 유도)
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=messages,
        config=types.GenerateContentConfig(tools=tools)
    )

    # 7. 모델이 함수 호출을 요청했는지 확인
    # ⭐️ 디버깅을 위해 function_calls 상태를 출력합니다.
    print(f"######### function_calls 상태: {response.function_calls}") 
    
    if response.function_calls:
        function_call = response.function_calls[0]
        function_name = function_call.name
        function_args = dict(function_call.args)

        print(f"\n**AI 요청:** '{function_name}' 함수 호출이 필요합니다. (인수: {function_args})")
        
        # 8. 실제 함수 실행 (안전한 실행을 위해 딕셔너리 사용)
        function_to_call = AVAILABLE_FUNCTIONS.get(function_name)
        
        if function_to_call:
            tool_response_json = function_to_call(**function_args)
        else:
            tool_response_json = json.dumps({"error": f"정의되지 않은 함수 호출: {function_name}"})
        
        print(f"   **함수 실행 결과:** {tool_response_json}")
        
        # 9. 함수의 실행 결과를 모델에게 다시 전달
        messages.append(response.candidates[0].content)
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
            contents=messages,
        )

        print(f"\n✅ **최종 AI 답변:** {final_response.text.strip()}")
            
    else:
        print(f"\n**AI 응답:** 함수 호출 없이 바로 답변합니다.")
        print(response.text.strip())

# --- 실행 예제 ---

# ⭐️ 수정: 모델이 암산하기 어렵도록 복잡한 계산을 요청하여 함수 호출을 유도합니다.
query_math_reasoning = "외부 계산기 도구를 사용해서 8765432와 1234567을 더한 값을 알려줘." 
run_simple_function_calling_example(query_math_reasoning)

query_math_reasoning = "내 소득이 1000000 일때 원천징수를 계산해줘" 
run_simple_function_calling_example(query_math_reasoning)

print("\n" + "="*50)

# 덧셈 함수가 필요 없는 일반 질문 (함수 호출 없음 예상)
query_general = "태양계 행성의 수는 몇 개야?"
run_simple_function_calling_example(query_general)