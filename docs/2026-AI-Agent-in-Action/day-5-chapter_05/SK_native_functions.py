import asyncio
import os
from dotenv import load_dotenv

import semantic_kernel as sk
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion, OpenAIChatPromptExecutionSettings
from semantic_kernel.functions import kernel_function, KernelArguments
from semantic_kernel.functions import KernelPlugin
# 1. 환경 변수 로드
load_dotenv()

# 2. Native Plugin 정의 -- 시청목록만 가져온다 
class MySeenMoviesDatabase:
    """사용자가 시청한 영화 목록을 관리하는 플러그인"""
    
    "일반함수를 시맨틱 커널에서 사용하는 플러그인으로 등록하는 데코레이터임"
    @kernel_function(
        name="LoadSeenMovies",
        description="텍스트 파일에서 사용자가 이미 시청한 영화 목록을 불러옵니다."
    )
    def load_seen_movies(self) -> str:
        file_path = "seen_movies.txt"
        # 파일이 없으면 샘플 생성
        if not os.path.exists(file_path):
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("인터스텔라\n인셉션\n매트릭스")
        
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                lines = [line.strip() for line in file.readlines() if line.strip()]
                return ", ".join(lines)
        except Exception as e:
            return f"파일 읽기 오류: {str(e)}"

async def main():
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

    # 4. Native Plugin 등록 (add_plugin 사용)
    seen_movies_plugin = kernel.add_plugin(
        MySeenMoviesDatabase(),  #객체전달 
        plugin_name="SeenMoviesPlugin" #플러그인 이름은 SeenMoviesPlugin임 
    )

    #인스턴스 스캐닝: MySeenMoviesDatabase() 객체 내부를 훑어서 @kernel_function 데코레이터가 붙은 메서드들을 모두 찾아냅니다.
    #기능 매핑: 찾아낸 메서드들을 SeenMoviesPlugin이라는 이름표 아래에 묶어서 관리 리스트에 올립니다.
    #메타데이터 바인딩: 각 메서드에 작성된 name과 description을 읽어와서, 나중에 LLM이 "이 플러그인은 무슨 일을 해?"라고 물어볼 때 대답할 수 있도록 준비해 둡니다.

    # 5. Semantic Plugin 로드 (에러 수정 포인트!)
    # v1.x 최신 버전에서는 add_plugin_from_prompt_directory를 사용합니다.
    plugins_directory = "plugins"
    
    #영화추천 플러그인 
    recommender_plugin = KernelPlugin.from_directory(
        parent_directory=plugins_directory,
        plugin_name="Recommender"
    )

    kernel.add_plugin(recommender_plugin)

    # 6. 실행 단계
    # (1) Native Function 호출 (시청 기록 가져오기)
    seen_movies_result = await kernel.invoke(
        seen_movies_plugin["LoadSeenMovies"]
    )
    seen_movie_list = str(seen_movies_result)
    print(f"📍 불러온 시청 목록: {seen_movie_list}")

    # (2) LLM에게 추천 요청 (Semantic Function 호출)
    execution_settings = OpenAIChatPromptExecutionSettings(
        service_id=service_id,
        temperature=0.7,
        max_tokens=1000
    )

    final_result = await kernel.invoke(
        recommender_plugin["Recommend_Movies"],
        KernelArguments(settings=execution_settings, input=seen_movie_list)
    )

    print("\n" + "="*50)
    print(f"AI 맞춤 영화 추천 결과:\n\n{final_result}")
    print("="*50)

if __name__ == "__main__":
    asyncio.run(main())
   