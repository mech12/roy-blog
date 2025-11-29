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

def run_image_generation_example():
    """DALL·E를 이용한 이미지 생성 예제 실행"""
    print("--- 2. 이미지 생성 예제 시작 ---")

    # 생성할 이미지에 대한 설명
    prompt = "A friendly golden retriever wearing a small party hat, sitting at a birthday table, photorealistic, digital art."
    
    # DALL·E 3 모델 사용
    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        n=1,
        size="1024x1024",
        response_format="url" # 결과를 이미지 URL로 받음
    )

    # 생성된 이미지 URL 출력
    image_url = response.data[0].url
    print(f"🖼️ 생성된 이미지 URL: {image_url}")
    print("이 URL을 웹 브라우저에 붙여넣어 이미지를 확인하세요.")

    # # (선택 사항: 이미지 라이브러리 설치 시) 이미지를 직접 다운로드하여 열기
    # try:
    #     image_response = requests.get(image_url)
    #     image = Image.open(BytesIO(image_response.content))
    #     image.show()
    # except Exception as e:
    #     print(f"\n참고: PIL/requests 라이브러리 설치 필요: {e}")

    print("--- 이미지 생성 예제 종료 ---\n")

# run_image_generation_example()