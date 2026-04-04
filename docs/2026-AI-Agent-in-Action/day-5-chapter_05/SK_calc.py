import asyncio
import os
from dotenv import load_dotenv

import semantic_kernel as sk
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion, OpenAIChatPromptExecutionSettings
from semantic_kernel.functions import KernelArguments
from semantic_kernel.prompt_template import PromptTemplateConfig, InputVariable

# 1. 환경 변수 로드
load_dotenv()

async def main():
    # 커널 초기화 (컨테이너 생성)
    kernel = sk.Kernel()

    # 2. AI 서비스 설정 (LLM 엔진 장착)
    service_id = "oai_chat_gpt"
    kernel.add_service(
        OpenAIChatCompletion(
            service_id=service_id,
            ai_model_id="gpt-4o",
            api_key=os.getenv("OPENAI_API_KEY"),
        ),
    )

    # 3. 실행 설정 (창의성보다는 정확도가 중요하므로 temperature를 낮게 설정)
    execution_settings = OpenAIChatPromptExecutionSettings(
        service_id=service_id,
        max_tokens=500,
        temperature=0.1,  # 계산은 정확해야 하므로 낮은 값 권장
    )

    # 4. 사칙연산 프롬프트 템플릿 정의
    # 로봇의 수치 제어나 데이터 분석 로직으로 확장 가능
    prompt = """
    system:
    당신은 정확한 수치 계산을 수행하는 연산 전문가입니다.
    사용자의 요청에 따라 숫자1과 숫자2에 대해 지정된 연산(더하기, 빼기, 곱하기, 나누기)을 수행하세요.

    user:
    다음 두 숫자에 대해 {{$operation}} 연산을 수행해줘.
    - 숫자 1: {{$input1}}
    - 숫자 2: {{$input2}}
    
    결과는 "결과값: [수치]" 형식으로 출력하고, 짧은 수식을 포함해줘.
    """

    # 5. 프롬프트 템플릿 설정 (명세서 작성)
    prompt_template_config = PromptTemplateConfig(
        template=prompt,
        name="calculate_core", 
        template_format="semantic-kernel",
        input_variables=[
            InputVariable(name="operation", description="수행할 연산 (더하기, 빼기 등)", is_required=True),
            InputVariable(name="input1", description="첫 번째 숫자", is_required=True),
            InputVariable(name="input2", description="두 번째 숫자", is_required=True),
        ],
        execution_settings=execution_settings,
    )

    # 6. 함수 생성 및 등록 (메서드와 클래스 매핑)
    calc_function = kernel.add_function(
        function_name="Calculator",        # 메서드명 (내 마음대로)
        plugin_name="MathPlugin",          # 클래스명 (내 마음대로)
        prompt_template_config=prompt_template_config,
    )

    # 7. 실행부 (인자값 전달)
    # 로봇 센서 값이나 사용자 명령을 인자로 구성
    args = KernelArguments(
        operation="곱하기",
        input1="15",
        input2="8"
    )

    # 비동기 호출 (Invoke)
    result = await kernel.invoke(calc_function, args)
    
    print("-" * 30)
    print(f"### 로봇 연산 모듈 결과:\n\n{result}")
    print("-" * 30)

if __name__ == "__main__":
    asyncio.run(main())