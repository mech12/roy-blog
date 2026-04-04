import asyncio
import os
from dotenv import load_dotenv

import semantic_kernel as sk
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion, OpenAIChatPromptExecutionSettings
from semantic_kernel.functions import kernel_function, KernelArguments
from semantic_kernel.prompt_template import PromptTemplateConfig

# 1. 환경 변수 로드
load_dotenv()

# 2. Native Plugin 정의 (데이터 관리 클래스)
class MySeenMoviesDatabase:
    @kernel_function(
        name="LoadSeenMovies",
        description="사용자가 이미 시청한 영화 목록을 파일에서 불러옵니다."
    )
    def load_seen_movies(self) -> str:
        file_path = "seen_movies.txt"
        if not os.path.exists(file_path):
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("인터스텔라\n인셉션\n매트릭스")
        
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                lines = [line.strip() for line in file.readlines() if line.strip()]
                return ", ".join(lines)
        except Exception as e:
            print(f"파일 읽기 오류: {e}")
            return ""

async def run_recommendation():
    # 커널 초기화
    kernel = sk.Kernel()

    # 3. AI 서비스 설정
    api_key = os.getenv("OPENAI_API_KEY")
    service_id = "oai_chat"
    
    kernel.add_service(
        OpenAIChatCompletion(
            service_id=service_id,
            ai_model_id="gpt-4o",
            api_key=api_key
        )
    )

    # 4. Native Plugin 등록 
    # 이제는 add_plugin을 사용하며, 등록된 이름이 프롬프트 내 호출명이 됩니다.
    kernel.add_plugin(MySeenMoviesDatabase(), plugin_name="SeenMoviesPlugin")

    # 5. 프롬프트 템플릿 설정 (v1.x 정석)
    # {{SeenMoviesPlugin.LoadSeenMovies}} 구문을 통해 LLM 실행 전 함수 결과가 주입됩니다.
    sk_prompt = """
    당신은 지혜로운 영화 추천가입니다.
    사용자가 이전에 시청한 영화 목록을 참고하여, 아직 보지 않은 영화 중 하나를 추천해 주세요.
    시청한 영화 목록: {{SeenMoviesPlugin.LoadSeenMovies}}
    """

    execution_settings = OpenAIChatPromptExecutionSettings(
        service_id=service_id,
        max_tokens=2000,
        temperature=0.7,
    )

    prompt_template_config = PromptTemplateConfig(
        template=sk_prompt,
        execution_settings={service_id: execution_settings}
    )

    # 6. 프롬프트로부터 함수 생성
    recommend_function = kernel.add_function(
        function_name="Recommend_Movies",
        plugin_name="Recommendation",
        prompt_template_config=prompt_template_config,
    )

    # 7. 실행
    result = await kernel.invoke(recommend_function)
    
    print("-" * 50)
    print(f"🎬 AI 추천 결과:\n\n{result}")
    print("-" * 50)

if __name__ == "__main__":
    asyncio.run(run_recommendation())