import json
from google import genai
from google.genai import types
import sys # 시스템 종료를 위한 모듈 임포트

# ⭐️ 1. 설정 및 클라이언트 초기화 ⭐️
MODEL_NAME = 'gemini-2.5-flash' 
# 챗봇이 수행해야 할 역할을 명확히 정의합니다.
SYSTEM_INSTRUCTION = (
    "당신은 ABC 보험회사의 친절한 AI 상품 추천 컨설턴트입니다. "
    "사용자의 대화 내용을 항상 기억하고, 상품 추천에 필요한 모든 정보(나이, 직업, 가족 상태)를 "
    "확보했을 때만 'recommend_insurance' 함수를 호출하여 결과를 바탕으로 최종 답변을 생성해야 합니다."
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
    print(f"\n   **[함수 실행]** 추천 로직 실행: 나이={age}, 직업={job_type}, 가족={family_status}...")
    
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
# 4. 메인 챗봇 루프 함수
# ----------------------------------------------------
def run_insurance_chatbot_session():
    # 모델에게 제공할 함수 목록
    tools = [recommend_insurance]
    
    # 1. 챗 세션 생성 (대화 기록을 저장할 컨테이너)
    chat = client.chats.create(
        model=MODEL_NAME,
        config=types.GenerateContentConfig(
            tools=tools, # 함수 정의를 여기에 넣어줍니다.
            system_instruction=SYSTEM_INSTRUCTION
        )
    )

    print("="*60)
    print("🤖 보험 컨설팅 챗봇 시작: 대화를 통해 상품을 추천받으세요. ('종료' 입력)")
    print(f"**필요 정보:** 나이, 직업, 가족 상태")
    print("="*60)

    # 2. 무한 루프 시작
    while True:
        try:
            user_input = input("👤 나: ")
            
            if user_input.lower() == '종료':
                print("🤖 챗봇: 컨설팅을 종료합니다. 다음에 다시 방문해 주세요!")
                break

            if not user_input.strip():
                continue

            # 3. 메시지 전송 (1차 API 호출)
            response = chat.send_message(user_input)
            
            # 4. 모델이 함수 호출을 요청했는지 확인
            if response.function_calls:
                function_call = response.function_calls[0]
                function_name = function_call.name
                function_args = dict(function_call.args)

                print(f"🤖 1차 응답: '{function_name}' 호출 요청 (인수: {function_args})")
                
                # 5. 로컬에서 실제 함수 실행
                function_to_call = AVAILABLE_FUNCTIONS.get(function_name)
                
                if function_to_call:
                    tool_response_json = function_to_call(**function_args)
                else:
                    tool_response_json = json.dumps({"error": f"정의되지 않은 함수 호출: {function_name}"})
                
                print(f"   🐍 함수 실행 결과: {tool_response_json}")
                
                # 6. 함수 실행 결과를 모델에게 다시 전달 (2차 API 호출)
                # messages.append() 대신 chat.send_message()의 내부 로직을 활용하여 결과를 전달합니다.
                # response.candidates[0].content는 함수 호출 요청이 담긴 Content 객체입니다.
                result_part = types.Part.from_function_response(
                    name=function_name, 
                    response={"result": tool_response_json}
                )

                # chat 객체는 이전 기록을 자동으로 포함하여 2차 호출을 수행합니다.
                final_response = chat.send_message(contents=[result_part])

                print(f"\n✅ 최종 AI 답변:\n{final_response.text.strip()}")
            
            else:
                # 7. 함수 호출 없이 바로 답변한 경우 (정보가 부족하거나 일반 대화)
                print(f"🤖 챗봇: {response.text}")

        except Exception as e:
            print(f"\n[오류 발생]: {e}")
            break

# --- 5. 챗봇 세션 실행 ---
if __name__ == '__main__':
    run_insurance_chatbot_session()