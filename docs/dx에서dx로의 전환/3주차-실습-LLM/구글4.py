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

def example_1_text_generation():
    """텍스트 생성 및 요약 예제 실행"""
    print("--- 1. 텍스트 대화 및 요약 예제 시작 ---")
    
    # 사용할 모델 지정
    model = 'gemini-2.5-flash'
    
    # 텍스트 프롬프트
    prompt = """
    다음 문단을 30자 이내로 요약해 주세요:
    인공지능(AI)은 컴퓨터 시스템이 인간의 지능을 모방하여 학습하고, 문제를 해결하며, 의사 결정을 내리는 기술입니다.
    최근 딥러닝 기술의 발전으로 AI는 이미지 인식, 자연어 처리, 그리고 자율 주행 등 다양한 분야에서 혁신을 이끌고 있습니다.
    """
    
    try:
        response = client.models.generate_content(
            model=model,
            contents=prompt,
        )
        
        print(f"🤖 AI 응답 (요약): {response.text.strip()}")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        
    print("--- 텍스트 대화 및 요약 예제 종료 ---\n")

example_1_text_generation()