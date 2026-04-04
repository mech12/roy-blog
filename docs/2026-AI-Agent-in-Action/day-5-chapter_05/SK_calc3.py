import asyncio
import os
import json
from dotenv import load_dotenv

import semantic_kernel as sk
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion, OpenAIChatPromptExecutionSettings
from semantic_kernel.functions import KernelArguments
from semantic_kernel.prompt_template import PromptTemplateConfig, InputVariable
from openai import AsyncOpenAI

load_dotenv()

# 환경 변수 (.env.example 참조)
api_key = os.getenv("OPENAI_API_KEY", "none")
api_base = os.getenv("OPENAI_API_BASE")
model_id = os.getenv("OPENAI_API_MODEL", "gpt-4o")

# 통합 판단 및 추출 프롬프트
router_prompt = """
system: 당신은 사용자의 질문을 분석하여 적절한 처리를 수행하는 만능 전문가입니다.

규칙:
1. 사칙연산(더하기, 빼기, 곱하기, 나누기) 요청인 경우, 아래 JSON 형식으로만 응답하세요.
    {"type": "calc", "operation": "연산종류", "input1": 숫자1, "input2": 숫자2}

2. 그 외의 일반적인 질문(예: 수도, 인사, 상식 등)은 즉시 친절하게 답변을 작성하세요.
    {"type": "chat", "answer": "질문에 대한 답변 내용"}

user: {{$userInput}}
JSON 출력:
"""

async def main():
    kernel = sk.Kernel()
    service_id = "oai_chat_gpt"
    
    kernel.add_service(
        OpenAIChatCompletion(service_id=service_id, ai_model_id=model_id, async_client=AsyncOpenAI(api_key=api_key, base_url=api_base))
    )

    execution_settings = OpenAIChatPromptExecutionSettings(service_id=service_id, max_tokens=1000, temperature=0.3)

    # [함수 1: 판단 및 라우팅]
    router_config = PromptTemplateConfig(
        template=router_prompt, # 위에서 정의한 프롬프트
        name="Router",
        input_variables=[InputVariable(name="userInput", is_required=True)],
        execution_settings=execution_settings,
    )
    router_func = kernel.add_function(function_name="RouteIntent", plugin_name="MainPlugin", prompt_template_config=router_config)

    # [함수 2: 실제 연산 수행 (기존과 동일)]
    calc_prompt = "user: {{$operation}} 연산 수행: {{$input1}}와 {{$input2}}의 결과와 설명을 적어줘."
    calc_config = PromptTemplateConfig(
        template=calc_prompt, name="Calc",
        input_variables=[InputVariable(name="operation"), InputVariable(name="input1"), InputVariable(name="input2")],
        execution_settings=execution_settings
    )
    calc_func = kernel.add_function(function_name="Calculator", plugin_name="MathPlugin", prompt_template_config=calc_config)

    # --- 실행 루프 ---
    while True:
        user_input = input("\n질문을 입력하세요 (종료: q): ")
        if user_input.lower() == 'q': break

        # 1단계: AI의 의도 판단
        route_result = await kernel.invoke(router_func, KernelArguments(userInput=user_input))
        
        # JSON 정규화 및 파싱
        raw_content = str(route_result).strip()
        if raw_content.startswith("```"):
            raw_content = raw_content.replace("```json", "").replace("```", "").strip()

        try:
            data = json.loads(raw_content)
            
            # 2단계: 타입에 따른 분기 처리 (이게 핵심입니다!)
            if data.get("type") == "calc":
                # 계산인 경우: Calculator 함수 호출
                print(f"[계산 모드 실행] {data['operation']} 처리 중...")
                final_res = await kernel.invoke(calc_func, KernelArguments(**data))
                print(f"### 결과: {final_res}")
                
            else:
                # 일반 질문인 경우: 바로 답변 출력
                print(f"### AI 답변: {data.get('answer')}")

        except Exception as e:
            print(f"오류가 발생했습니다. 다시 질문해주세요. ({e})")

if __name__ == "__main__":
    asyncio.run(main())