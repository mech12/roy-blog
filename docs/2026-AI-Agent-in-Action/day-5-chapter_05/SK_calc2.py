import asyncio
import os
import json
from dotenv import load_dotenv

import semantic_kernel as sk
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion, OpenAIChatPromptExecutionSettings
from semantic_kernel.functions import KernelArguments
from semantic_kernel.prompt_template import PromptTemplateConfig, InputVariable
from openai import AsyncOpenAI

# 1. 환경 변수(.env) 로드
load_dotenv()

async def main():
    # 커널 초기화 (에이전트의 몸체 생성)
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

    # 3. 공통 실행 설정 (정확도를 위해 온도를 낮춤)
    execution_settings = OpenAIChatPromptExecutionSettings(
        service_id=service_id,
        max_tokens=1000,
        temperature=0.1, 
    )

    # --- [STEP 1: 인자 추출용 프롬프트 함수 정의] ---
    extract_prompt = """
    system: 당신은 문장에서 핵심 정보를 추출하여 JSON으로 변환하는 전문가입니다.
    user: 사용자의 명령에서 'operation', 'input1', 'input2'를 찾아 JSON 형식으로만 답변하세요.
    - operation: 더하기, 빼기, 곱하기, 나누기 중 하나
    - input1, input2: 추출된 숫자
    
    사용자 명령: {{$userInput}}
    JSON 출력:
    """

    # 수정된 extract_prompt
    extract_prompt = """
    system: 당신은 문장에서 연산 정보를 추출하는 전문가입니다.
    user: 다음 규칙을 엄격히 지켜 JSON으로만 답변하세요.
    1. '더하기, 빼기, 곱하기, 나누기'와 관련된 내용이면 'operation', 'input1', 'input2'를 추출하세요.
    2. 만약 연산과 전혀 상관없는 질문이라면, 아래와 같이 에러 정보를 담은 JSON을 반환하세요.
    {"error": "지원하지 않는 명령입니다", "is_valid": false}

    사용자 명령: {{$userInput}}
    JSON 출력:
    """


    extract_config = PromptTemplateConfig(
        template=extract_prompt,
        name="ExtractArgs",
        input_variables=[InputVariable(name="userInput", is_required=True)],
        execution_settings=execution_settings,
    )

    extract_function = kernel.add_function(
        function_name="ExtractArguments",
        plugin_name="MathPlugin",
        prompt_template_config=extract_config,
    )

    # --- [STEP 2: 실제 연산용 프롬프트 함수 정의] ---
    calc_prompt = """
    system: 당신은 정확한 연산 전문가입니다.
    user: 다음 연산을 수행하고 결과값과 간단한 설명을 적어주세요.
    - 연산: {{$operation}}
    - 숫자1: {{$input1}}
    - 숫자2: {{$input2}}
    """

    calc_config = PromptTemplateConfig(
        template=calc_prompt,
        name="CalculateCore",
        input_variables=[
            InputVariable(name="operation", is_required=True),
            InputVariable(name="input1", is_required=True),
            InputVariable(name="input2", is_required=True),
        ],
        execution_settings=execution_settings,
    )

    calc_function = kernel.add_function(
        function_name="Calculator",
        plugin_name="MathPlugin",
        prompt_template_config=calc_config,
    )

    # --- [STEP 3: 실행부 (에이전트 워크플로우)] ---
    user_input =input("질문을 입력하세요")

    print(f"\n[1/3] 사용자 입력 분석 중: '{user_input}'")
    
    # 1단계: 인자 추출 호출
    extract_result = await kernel.invoke(
        extract_function, 
        KernelArguments(userInput=user_input)
    )
    
    # JSON 파싱 (문자열 -> 딕셔너리)
    try:
        # AI 응답 내용 추출 및 마크다운 제거 (정규화)
        raw_content = str(extract_result).strip()
    
        # 만약 ```json 이나 ``` 로 감싸져 있다면 제거함
        if raw_content.startswith("```"):
            raw_content = raw_content.replace("```json", "").replace("```", "").strip()


        data = json.loads(str(raw_content).strip())
        # # 1. 유효성 체크 로직 추가
        # if data.get("is_valid") == False or "operation" not in data:
        #     print(f"⚠️ 처리 불가: {data.get('error', '계산 관련 질문이 아닙니다.')}")
        #     return # 함수 종료 또는 재입력 유도

        # 2. 정상적인 경우 계산 진행

        print(f"[2/3] 추출된 데이터: {data}")
        
        # 2단계: 추출된 데이터를 인자로 실제 계산 호출
        final_args = KernelArguments(**data) # 딕셔너리를 언패킹하여 전달
        final_result = await kernel.invoke(calc_function, final_args)
        
        print("-" * 40)
        print(f"### 최종 결과:\n{final_result}")
        print("-" * 40)
        
    except Exception as e:
        print(f"오류 발생: {e}\nAI 응답 내용: {extract_result}")

if __name__ == "__main__":
    asyncio.run(main())