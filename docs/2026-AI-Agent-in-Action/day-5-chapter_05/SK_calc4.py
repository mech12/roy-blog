import asyncio
import os
from dotenv import load_dotenv
import semantic_kernel as sk
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
from semantic_kernel.functions import KernelArguments

load_dotenv()

async def main():
    kernel = sk.Kernel()

    # 서비스 등록
    kernel.add_service(
        OpenAIChatCompletion(
            service_id="oai_chat_gpt",
            ai_model_id="gpt-4o",
            api_key=os.getenv("OPENAI_API_KEY")
        )
    )

    # 🚀 핵심: 디렉토리로부터 플러그인을 한꺼번에 로드합니다.
    # plugins 폴더 안의 모든 하위 폴더(함수)를 자동으로 인식하여 등록합니다.
    plugins_directory = os.path.join(os.getcwd(), "plugins")
    math_plugin = kernel.add_plugin(
        plugin_name="MathPlugin", 
        parent_directory=plugins_directory
    )

    # 실행부: 등록된 플러그인 내의 함수를 호출
    args = KernelArguments(
        operation="곱하기",
        input1="15",
        input2="8"
    )

    # kernel["플러그인명"]["함수명"] 형태로 접근 가능
    result = await kernel.invoke(math_plugin["Calculator"], args)
    
    print("-" * 30)
    print(f"### 파일 분리형 로봇 연산 결과:\n\n{result}")
    print("-" * 30)

if __name__ == "__main__":
    asyncio.run(main())