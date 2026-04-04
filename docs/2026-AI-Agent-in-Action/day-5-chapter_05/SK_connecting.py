import asyncio
import os
from dotenv import load_dotenv
import semantic_kernel as sk
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
#커널 하나에 OpenAI, Azure, Google Gemini 등을 동시에 등록해 두고 용도별로 호출할 수 있습니다.
# 1. .env 파일 수동 로드 (가장 확실한 방법)
load_dotenv()

selected_service = "OpenAI"  #사용할 LLM 선택 
kernel = sk.Kernel()

if selected_service == "OpenAI":
    # 2. 환경 변수에서 직접 가져오기
    api_key = os.getenv("OPENAI_API_KEY")
    org_id = os.getenv("OPENAI_ORG_ID") # 필수 아님 (None 가능)
    
    if not api_key:
        print("오류: .env 파일에 OPENAI_API_KEY가 설정되어 있지 않습니다.")
    else:
        service_id = "oai_chat_gpt"
        # 3. 서비스 추가 (최신 v1.x 스타일)
        # 2. 서비스(AI 엔진) 추가
        # service_id: 여러 모델을 쓸 때 구분하는 이름 (내 마음대로 지정 가능)
        # 시맨틸 커널에 서비스를 등록한다  
        kernel.add_service(
            OpenAIChatCompletion(
                service_id=service_id, # 서비스 식별자
                ai_model_id="gpt-4o",       # 사용할 모델명
                api_key=api_key,    # API 키
                org_id=org_id,
            ),
        )


async def run_prompt():
    # 한글 프롬프트 실행
    result = await kernel.invoke_prompt(
        prompt="시간 여행을 주제로 한 영화를 한 편 추천해주고, 그 영화를 꼭 봐야 하는 이유를 짧게 요약해줘."
    )
    print(f"### AI 추천 결과:\n{result}")

if __name__ == "__main__":
    asyncio.run(run_prompt())