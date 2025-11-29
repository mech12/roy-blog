import os
import json
from google import genai
from google.genai import types

# --- 설정된 API 키 사용 ---
# MyKey는 예시입니다. 실제 API 키로 대체해야 합니다.
MyKey = "YOUR_GEMINI_API_KEY"
# -------------------------

# 1. 클라이언트 초기화
try:
    client = genai.Client(api_key=MyKey)
except Exception as e:
    print(f"클라이언트 초기화 오류: {e}. API 키 설정을 확인하세요.")
    exit()

# 2. 사용할 모델 지정 (함수 호출과 JSON 출력을 지원하는 모델 사용)
MODEL_NAME = 'gemini-2.5-flash'

# ====================================================================
# 🚀 발전된 실습 예제 1: 함수 호출 (Function Calling / Tools)
# ====================================================================

# 💡 모델이 호출할 수 있는 함수 정의
def get_flight_schedule(airline: str, date: str) -> str:
    """
    주어진 항공사와 날짜에 대한 비행 스케줄을 가상의 데이터베이스에서 조회합니다.
    (실제 API 호출 대신 가상 데이터를 반환합니다.)
    """
    print(f"[함수 실행: get_flight_schedule(항공사='{airline}', 날짜='{date}')]를 실행합니다...")
    
    if "대한항공" in airline and "2025-12-25" in date:
        return json.dumps({
            "airline": "대한항공",
            "date": "2025-12-25",
            "flights": [
                {"flight_number": "KE601", "departure": "10:00", "arrival": "12:30", "status": "정시"},
                {"flight_number": "KE607", "departure": "15:00", "arrival": "17:30", "status": "지연"}
            ]
        })
    else:
        return json.dumps({"airline": airline, "date": date, "flights": [], "message": "해당 조건의 비행편이 없습니다."})

# 💡 함수 호출을 처리하는 메인 로직
def run_function_calling_example(user_query: str):
    print("\n" + "="*50)
    print("🚀 예제 1: 함수 호출 (Function Calling)")
    print("="*50)
    print(f"👤 사용자 입력: {user_query}")
    
    # 1. 모델에게 제공할 함수 목록
    tools = [get_flight_schedule]
    
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
            tool_response_json = get_flight_schedule(**function_args)
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


# --- 예제 1 실행 ---
query1 = "2025년 12월 25일 대한항공 비행 스케줄을 알려줘."
run_function_calling_example(query1)


# ====================================================================
# 🚀 발전된 실습 예제 2: 구조화된 JSON 출력 (Structured Output)
# ====================================================================

def run_json_output_example(input_text: str):
    """
    모델의 출력을 미리 정의된 JSON 스키마 형식으로 받습니다.
    """
    print("\n" + "="*50)
    print("🚀 예제 2: 구조화된 JSON 출력")
    print("="*50)
    print(f"📄 입력 텍스트: {input_text}")

    # 1. 출력 스키마 정의 (모델이 따라야 할 JSON 구조)
    schema = types.Schema(
        type=types.Type.OBJECT,
        properties={
            "item_name_kr": types.Schema(type=types.Type.STRING, description="제품의 한국어 이름"),
            "category": types.Schema(type=types.Type.STRING, description="제품의 카테고리 (예: 전자기기, 의류, 식품)"),
            "price_usd": types.Schema(type=types.Type.NUMBER, description="제품 가격을 USD로 변환한 값"),
            "is_luxury": types.Schema(type=types.Type.BOOLEAN, description="사치품 여부 (가격이 1000 USD 초과면 true)")
        },
        required=["item_name_kr", "category", "price_usd", "is_luxury"]
    )
    
    # 2. 모델에게 요청 (JSON 스키마 및 출력 타입 지정)
    prompt = f"다음 상품 정보를 분석하여 정의된 스키마에 맞는 JSON 객체를 생성하세요: {input_text}"
    
    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json", # JSON 출력 요청
                response_schema=schema,                 # 정의된 스키마 적용
            ),
        )
        
        # 3. JSON 응답 출력 및 검증
        json_output = response.text.strip()
        print("\n✅ 모델 생성 JSON 출력:")
        print(json_output)
        
        # 4. JSON 문자열을 파이썬 딕셔너리로 변환하여 데이터 사용 (검증)
        parsed_data = json.loads(json_output)
        print("\n--- 파이썬에서 파싱된 데이터 ---")
        print(f"제품 이름: {parsed_data.get('item_name_kr')}")
        print(f"가격 (USD): {parsed_data.get('price_usd')}")
        print(f"사치품 여부: {parsed_data.get('is_luxury')}")
        
    except Exception as e:
        print(f"❌ JSON 출력 처리 중 오류 발생: {e}")


# --- 예제 2 실행 ---
input_data = "상품: 최신형 노트북, 카테고리: 전자기기, 가격: 1500 달러"
run_json_output_example(input_data)