import asyncio
import os
from dotenv import load_dotenv
import semantic_kernel as sk
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
from openai import AsyncOpenAI
#커널 하나에 OpenAI, Azure, Google Gemini 등을 동시에 등록해 두고 용도별로 호출할 수 있습니다.
# 1. .env 파일 수동 로드 (가장 확실한 방법)
load_dotenv()

# 2. 환경 변수에서 API 설정 가져오기 (.env.example 참조)
api_key = os.getenv("OPENAI_API_KEY", "none")
api_base = os.getenv("OPENAI_API_BASE")
model_id = os.getenv("OPENAI_API_MODEL", "gpt-4o")

kernel = sk.Kernel()
service_id = "oai_chat_gpt"

# 3. 서비스 추가 (AsyncOpenAI 클라이언트를 통해 커스텀 엔드포인트 지원)
# service_id: 여러 모델을 쓸 때 구분하는 이름 (내 마음대로 지정 가능)
kernel.add_service(
    OpenAIChatCompletion(
        service_id=service_id,
        ai_model_id=model_id,
        async_client=AsyncOpenAI(api_key=api_key, base_url=api_base),
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