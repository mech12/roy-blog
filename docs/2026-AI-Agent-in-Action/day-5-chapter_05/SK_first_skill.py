import asyncio
import os
from dotenv import load_dotenv

import semantic_kernel as sk
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion, OpenAIChatPromptExecutionSettings
from semantic_kernel.functions import KernelArguments
from openai import AsyncOpenAI

# 1. 환경 변수 로드
load_dotenv()

async def run():
    # 커널 초기화
    kernel = sk.Kernel()

    # 2. AI 서비스 설정 (.env.example 참조)
    service_id = "oai_chat_gpt"
    api_key = os.getenv("OPENAI_API_KEY", "none")
    api_base = os.getenv("OPENAI_API_BASE")
    model_id = os.getenv("OPENAI_API_MODEL", "gpt-4o")

    kernel.add_service(
        OpenAIChatCompletion(
            service_id=service_id,
            ai_model_id=model_id,
            async_client=AsyncOpenAI(api_key=api_key, base_url=api_base),
        ),
    )

    # 3. 실행 설정 (Execution Settings)
    execution_settings = OpenAIChatPromptExecutionSettings(
        service_id=service_id,
        max_tokens=2000,
        temperature=0.7,
    )

    # 4. 플러그인 디렉토리 로드
    # 구조: plugins/Recommender/Recommend_Movies/skprompt.txt
    plugins_directory = "plugins"
    
    #디렉토리에 있는 플러그인을 불러온다
    try:
        recommender = kernel.add_plugin(
            parent_directory=plugins_directory,
            plugin_name="Recommender",
        )
        
        recommend_function = recommender["Recommend_Movies"]

        # 5. 데이터 준비 (시청한 영화 목록)
        seen_movie_list = [
            "백투더퓨처", 
            "터미네이터", 
            "12 몽키즈",
            "루퍼", 
            "사랑의 블랙홀", 
            "프라이머", 
            "도니 다코",
            "인터스텔라", 
            "시간도둑들"
            "닥터스트레인지",
        ]

        # 6. 실행 및 결과 출력
        # KernelArguments에 필요한 변수 매핑
        result = await kernel.invoke(
            recommend_function,
            KernelArguments(
                settings=execution_settings, 
                input=", ".join(seen_movie_list)
            ),
        )
        
        print("-" * 30)
        print(f"### AI 추천 영화 결과:\n\n{result}")
        print("-" * 30)

    except Exception as e:
        print(f"플러그인 로드 오류: {e}")

if __name__ == "__main__":
    asyncio.run(run())