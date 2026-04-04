import asyncio
import os
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion, AzureChatCompletion
from semantic_kernel.functions import KernelArguments
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

async def main():
    # 1. 커널 초기화 (빌더 패턴 사용)
    kernel = Kernel()

    # 2. AI 서비스 설정
    use_azure_openai = False  # 상황에 맞게 변경

    if use_azure_openai:
        # Azure OpenAI 설정
        kernel.add_service(AzureChatCompletion(
            service_id="default",
            # .env의 환경변수를 자동으로 가져오도록 구성 가능
        ))
    else:
        # 일반 OpenAI 설정 (최신 gpt-4o 모델 권장)
        api_key = os.getenv("OPENAI_API_KEY")
        org_id = os.getenv("OPENAI_ORG_ID")
        kernel.add_service(OpenAIChatCompletion(
            service_id="default",
            ai_model_id="gpt-4o",
            api_key=api_key,
            org_id=org_id
        ))

    # 3. 플러그인 가져오기 (이전의 Skill이 Plugin으로 명칭 변경됨)
    # 디렉토리 구조: plugins/FunPlugin/Joke/skprompt.txt
    plugins_directory = "plugins"
    
    try:
        fun_plugin = kernel.add_plugin(
            plugin_name="FunPlugin",
            parent_directory=plugins_directory,
        )
        
        joke_function = fun_plugin["Joke"]

        # 4. 인자 설정 및 실행 (ContextVariables 대신 KernelArguments 사용)
        # prompt 내의 {{$input}} 과 {{$style}} 변수에 매핑됩니다.
        arguments = KernelArguments(
            input="공룡 시대로의 시간 여행",
            style="스탠드업 코미디"
        )

        # 비동기 실행 (최신 SK는 비동기가 기본입니다)
        result = await kernel.invoke(joke_function, arguments)

        print(f"### 생성된 농담:\n{result}")

    except Exception as e:
        print(f"플러그인을 로드하거나 실행하는 중 오류 발생: {e}")
        print(f"팁: '{plugins_directory}/FunPlugin/Joke' 경로에 skprompt.txt 파일이 있는지 확인하세요.")

if __name__ == "__main__":
    asyncio.run(main())