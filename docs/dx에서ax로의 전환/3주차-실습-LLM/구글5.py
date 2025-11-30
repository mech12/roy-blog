MyKey = "YOUR_GEMINI_API_KEY"

#conda install Pillow

from PIL import Image
from io import BytesIO
import os
from google import genai
import requests 
# 1. 클라이언트 초기화
# 환경 변수에서 GEMINI_API_KEY를 자동으로 찾습니다.
try:
    client = genai.Client(api_key=MyKey)
except Exception as e:
    print(f"클라이언트 초기화 오류: {e}. API 키 설정을 확인하세요.")
    exit()

def example_2_multimodal_understanding():
    """이미지 및 텍스트 이해(멀티모달) 예제 실행"""
    print("--- 2. 멀티모달 이해 예제 시작 ---")
    
    model = 'gemini-2.5-flash'
    
    # 분석할 이미지 URL (예시 이미지 사용)
    image_url = "https://storage.googleapis.com/cloud-samples-data/generative-ai/image/scones.jpg"
    
    try:
        # 1. 이미지 다운로드 및 Part 객체로 변환
        image_data = requests.get(image_url).content
        image = Image.open(BytesIO(image_data))
        
        image_part = genai.types.Part.from_bytes(
            data=image_data,
            mime_type="image/jpeg",
        )
        
        # 2. 이미지와 텍스트를 함께 전달
        contents = [
            image_part,
            "이 사진에 보이는 음식이 무엇인지 설명하고, 이 음식을 만들 때 필요한 주요 재료 세 가지를 한국어로 알려주세요."
        ]
        
        response = client.models.generate_content(
            model=model,
            contents=contents
        )
        
        print(f"🤖 AI 응답 (이미지 분석): {response.text.strip()}")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        
    print("--- 멀티모달 이해 예제 종료 ---\n")

example_2_multimodal_understanding()