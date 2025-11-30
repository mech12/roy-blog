import json
from google import genai
from google.genai import types

# ⭐️ 1. 설정 및 클라이언트 초기화 ⭐️
MODEL_NAME = 'gemini-2.5-flash' 
SYSTEM_INSTRUCTION = (
    "당신은 ABC 보험회사의 친절한 AI 상품 추천 컨설턴트입니다. "
    "고객의 나이, 직업, 가족 상태를 파악한 후, 'recommend_insurance' 함수를 호출하여 "
    "받은 결과를 바탕으로 최종적인 답변을 생성해야 합니다."
)

MyKey = "YOUR_GEMINI_API_KEY"


import os
from google import genai

# 1. 클라이언트 초기화
# 환경 변수에서 GEMINI_API_KEY를 자동으로 찾습니다.
try:
    client = genai.Client(api_key=MyKey)
except Exception as e:
    print(f"클라이언트 초기화 오류: {e}. API 키 설정을 확인하세요.")
    exit()
# ----------------------------------------------------
# 💡 2. 함수 정의 (외부 시스템 역할)
# ----------------------------------------------------
def recommend_insurance(age: int, job_type: str, family_status: str) -> str:
    """
    고객의 나이(age), 직업 유형(job_type), 가족 상태(family_status)를 입력받아 
    가장 적합한 보험 상품 목록을 추천하는 외부 데이터베이스 검색 함수입니다.
    """
    print(f"\n   **[함수 실행]** 추천 로직 실행 중...")
    
    # ⭐️ 실제 로직 (가상): 조건에 따른 상품 추천 목록 생성
    if age < 40 and job_type == "사무직":
        if family_status == "기혼":
            recommendation = ["가족 생활 보장 보험", "어린이 보험"]
        else:
            recommendation = ["실손 보험", "정기 보험"]
    elif job_type == "현장직" and age >= 40:
        recommendation = ["상해/재해 보험", "중대 질병 보험"]
    else:
        recommendation = ["종합 건강 보험"]
        
    # 결과를 LLM에게 JSON 문자열로 반환
    return json.dumps({"recommended_products": recommendation})

# 💡 3. 함수 매핑 딕셔너리
AVAILABLE_FUNCTIONS = {
    "recommend_insurance": recommend_insurance,
}

# ----------------------------------------------------
# 4. 메인 챗봇 실행 로직
# ----------------------------------------------------
def run_insurance_chatbot(user_query: str):
    if not client:
        print("\n[SKIP] API 클라이언트 오류로 챗봇을 실행할 수 없습니다.")
        return

    print("="*60)
    print(f"👤 사용자 입력: {user_query}")
    print("="*60)
    
    # 모델에게 제공할 함수 목록
    tools = [recommend_insurance]
    
    # 1단계: 사용자 질문과 시스템 지침 포함
    messages = [{"role": "user", "parts": [types.Part(text=user_query)]}]

    # 1차 API 호출: 모델이 함수 호출을 요청할지 판단
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=messages,
        config=types.GenerateContentConfig(
            tools=tools,
            system_instruction=SYSTEM_INSTRUCTION
        )
    )

    # 2단계 A: 모델이 함수 호출을 요청했는지 확인
    if response.function_calls:
        function_call = response.function_calls[0]
        function_name = function_call.name
        function_args = dict(function_call.args)

        print(f"🤖 1차 응답: '{function_name}' 호출 요청 (인수: {function_args})")
        
        # 3단계: 로컬에서 실제 함수 실행
        function_to_call = AVAILABLE_FUNCTIONS.get(function_name)
        
        if function_to_call:
            tool_response_json = function_to_call(**function_args)
        else:
            tool_response_json = json.dumps({"error": f"정의되지 않은 함수 호출: {function_name}"})
        
        print(f"   🐍 함수 실행 결과: {tool_response_json}")
        
        # 4단계: 함수 실행 결과를 모델에게 다시 전달
        messages.append(response.candidates[0].content) # 이전 모델 요청 추가
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

        # 5단계: 최종 답변 요청 (2차 API 호출)
        final_response = client.models.generate_content(
            model=MODEL_NAME,
            contents=messages,
        )

        print(f"\n✅ 최종 AI 답변:\n{final_response.text.strip()}")
            
    else:
        print(f"\n**AI 응답:** 함수 호출 없이 바로 답변합니다.")
        print(response.text.strip())

# --- 실행 예제 ---

# 예제 1: 함수 호출 성공 예상 (사무직 미혼)
query_success = "저는 35세 사무직이고 미혼 남성인데, 어떤 보험이 저에게 필요할까요?"
run_insurance_chatbot(query_success)

print("\n" + "="*60)

# 예제 2: 다른 조건의 함수 호출 성공 예상 (현장직 기혼)
query_success_2 = "저는 45세이고 현장직에서 일해요. 결혼했고 자녀는 없습니다."
run_insurance_chatbot(query_success_2)