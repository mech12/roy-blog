import asyncio
import os
from dotenv import load_dotenv

import semantic_kernel as sk
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion, OpenAIChatPromptExecutionSettings
from semantic_kernel.contents import ChatHistory
from semantic_kernel.functions import KernelArguments
import semantic_kernel.connectors.ai as ai

# TMDb 서비스 플러그인 임포트 (기존 클래스 그대로 사용 가정)
from plugins.Movies.tmdb import TMDbService

load_dotenv()

async def main():
    kernel = sk.Kernel()

    # 1. AI 서비스 설정
    service_id = "oai_chat"
    kernel.add_service(
        OpenAIChatCompletion(
            service_id=service_id,
            ai_model_id="gpt-4o",
            api_key=os.getenv("OPENAI_API_KEY")
        )
    )

    # 2. 플러그인 등록 (TMDB 연동)
    # 이제는 import_plugin_from_object 대신 add_plugin을 사용합니다.
    kernel.add_plugin(TMDbService(), plugin_name="TMDBService")

    # 3. 자동 함수 호출 설정 (핵심!)
    # execution_settings에서 tool_call_behavior를 'auto'로 설정하면
    # 모델이 필요할 때 알아서 TMDB 플러그인을 호출합니다.
    execution_settings = OpenAIChatPromptExecutionSettings(
        service_id=service_id,
        max_tokens=2000,
        temperature=0.7,
        tool_call_behavior="auto" # 모델이 스스로 도구를 선택함
    )

    # 특정 플러그인/함수만 선택하거나 제외하는 최신 방식
    execution_settings.function_choice_behavior = ai.FunctionChoiceBehavior.Auto(
        filters={"included_plugins": ["TMDBService"]} # "ChatBot"은 빼고 "TMDBService"만 쓰라고 명시
    )

    # 4. 대화 기록 관리
    history = ChatHistory()
    history.add_system_message("당신은 영화 및 TV 프로그램을 추천하는 전문 챗봇 'Rudy'입니다.")

    print("Rudy의 영화챗봇세계에 오신걸 환영합니다. ! (끝내고 싶으면 '종료' 라고 입력하세요)")

    while True:
        try:
            user_input = input("User:> ")
        except (KeyboardInterrupt, EOFError):
            break

        if user_input.lower() == "종료":
            break

        # 사용자의 질문을 히스토리에 추가
        history.add_user_message(user_input)

        # 5. 에이전트 실행 (자동 함수 호출 포함)
        # 이제 별도의 복잡한 유틸리티 함수 없이 kernel.get_service(...).get_chat_message_content로 처리합니다.
        chat_service = kernel.get_service(service_id)
        
        # 모델은 질문을 분석하고 필요 시 TMDBService의 함수를 호출한 뒤 결과를 합쳐서 답변합니다.
        result = await chat_service.get_chat_message_content(
            chat_history=history,
            settings=execution_settings,
            kernel=kernel
        )

        print(f"GPT Agent:> {result}")
        
        # 어시스턴트의 답변도 히스토리에 추가하여 문맥 유지
        history.add_assistant_message(str(result))

if __name__ == "__main__":
    asyncio.run(main())