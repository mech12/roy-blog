import asyncio
import os
from dotenv import load_dotenv

import semantic_kernel as sk
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
from semantic_kernel.functions import KernelArguments, KernelPlugin

# 1. 환경 변수 로드
load_dotenv()

async def main():
    # 커널 초기화
    kernel = sk.Kernel()

    # 2. AI 서비스 설정 (v1.x 정석)
    api_key = os.getenv("OPENAI_API_KEY")
    service_id = "oai_chat"
    
    kernel.add_service(
        OpenAIChatCompletion(
            service_id=service_id,
            ai_model_id="gpt-4o", # 강사님, 최신 gpt-4o 권장드립니다.
            api_key=api_key
        )
    )

    # 3. Semantic Plugin 로드 (객체 지향 방식)
    plugins_directory = "plugins"
    try:
        # 'Recommender' 폴더 내의 'Recommend' 함수 폴더를 로드
        recommender_plugin = KernelPlugin.from_directory(
            parent_directory=plugins_directory,
            plugin_name="Recommender"
        )
        kernel.add_plugin(recommender_plugin)
        recommend_function = recommender_plugin["Recommend"]
    except Exception as e:
        print(f"❌ 플러그인 로드 실패: {e}")
        return

    # 4. 실행 함수 정의 (v1.x 데이터 바인딩 방식 적용)
    async def get_recommendation(subject, format, genre, custom):
        # 과거의 context["key"] = value 방식은 KernelArguments로 대체되었습니다.
        args = KernelArguments(
            subject=subject,
            format=format,
            genre=genre,
            custom=custom
        )
        
        # invoke 시 arguments를 넘겨주면 프롬프트 내의 {{$subject}} 등에 자동 매핑됩니다.
        result = await kernel.invoke(recommend_function, args)
        print(f"🎬 AI 추천 결과:\n{result}")

    # 5. 실행
    input_data = {
        "subject": "time travel",
        "format": "movie",
        "genre": "medieval",
        "custom": "must be a comedy",
    }
    
    await get_recommendation(**input_data)

if __name__ == "__main__":
    asyncio.run(main())