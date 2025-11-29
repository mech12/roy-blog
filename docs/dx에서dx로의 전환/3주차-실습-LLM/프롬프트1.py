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

# 2. 사용할 모델 지정 (예: gemini-2.5-flash)
MODEL_NAME = 'gemini-2.5-flash'

# 3. 기본 프롬프트 구성 및 호출
def generate_response(prompt: str):
    """주어진 프롬프트로 LLM을 호출하고 응답 텍스트를 반환합니다."""

    # 텍스트 생성 요청
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )

    # 응답 텍스트 반환
    return response.text

# 4. 실행 예제
user_prompt = "당신은 항상 반말을 사용하는 친절한 강아지 챗봇입니다. 자신을 소개해 줘."
llm_response = generate_response(user_prompt)

print("--- [사용자 입력] ---")
print(user_prompt)
print("\n--- [LLM 응답] ---")
print(llm_response)