import asyncio
import os
from dotenv import load_dotenv
import semantic_kernel as sk
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
from semantic_kernel.functions import KernelArguments

load_dotenv()

async def main():
    kernel = sk.Kernel()

    # 1. AI 서비스 등록
    kernel.add_service(
        OpenAIChatCompletion(
            service_id="travel_service",
            ai_model_id="gpt-4o",
            api_key=os.getenv("OPENAI_API_KEY")
        )
    )

    # 2. 플러그인 로드 (디렉토리 방식)
    # plugins/TravelPlugin 폴더를 읽어서 함수를 등록함
    plugins_directory = os.path.join(os.getcwd(), "plugins")
    travel_plugin = kernel.add_plugin(
        plugin_name="TravelPlugin", 
        parent_directory=plugins_directory
    )

    # 3. 사용자 입력값 설정 (나중에는 자연어에서 추출하도록 연동 가능)
    args = KernelArguments(
        location="유럽",
        budget="중간",
        activity="역사 유적 탐방과 맛집 탐방"
    )

    # 4. 실행
    print("여행 가이드 로봇이 최적의 장소를 찾고 있습니다...\n")
    result = await kernel.invoke(travel_plugin["SuggestDestination"], args)
    
    print("-" * 40)
    print(f"✈️ 추천 여행 일정:\n\n{result}")
    print("-" * 40)

if __name__ == "__main__":
    asyncio.run(main())