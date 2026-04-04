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
    # 커널 초기화및 서비스를등록한다
    kernel = sk.Kernel()

    # 2. AI 서비스 설정 (OpenAI 기준),서비스란 LLM을 말함  
    service_id = "oai_chat_gpt"
    api_key = os.getenv("OPENAI_API_KEY")
    org_id = os.getenv("OPENAI_ORG_ID")
    model_id = "gpt-4o"  # 최신 모델 권장

    kernel.add_service(
        OpenAIChatCompletion(
            service_id=service_id,
            ai_model_id=model_id,
            api_key=api_key,
            org_id=org_id,
        ),
    )

    # 3. 실행 설정 (Execution Settings)
    execution_settings = OpenAIChatPromptExecutionSettings(
        service_id=service_id,
        max_tokens=2000,
        temperature=0.7,
    )

    #프롬프트를 이용해 사용자 함수를 만든다 
    # 4. 한글 프롬프트 템플릿 정의  ==> 별도의 파일로 만들 수 있다
    # 프롬프트 템플릿 정의 (별도의 외부 파일(.txt)로 분리 관리 가능)
    # 변수는 {{$변수명}} 형태로 지정하여 동적 바인딩 준비

    prompt = """
    system:
    당신은 세상의 모든 지식을 섭렵한 전문가입니다. 
    제시된 주제, 장르, 형식 및 추가 정보를 바탕으로 최적의 콘텐츠를 추천해야 합니다.

    user:
    다음 조건에 맞는 {{$format}} 한 편을 추천해줘.
    - 주제: {{$subject}}
    - 장르: {{$genre}}
    - 추가 요구사항: {{$custom}}
    
    추천 이유를 포함하여 친절하게 설명해줘.
    """

    # 5. 프롬프트 템플릿 설정 (최신 버전 규격)
    prompt_template_config = PromptTemplateConfig(
        template=prompt, #프롬프트 내용
        name="recommend_content", #커널 내에서 이 프롬프트 함수를 식별하기 위한 고유 이름
        template_format="semantic-kernel", #템플릿의 문법 규격을 지정

        input_variables=[
            InputVariable(name="format", description="추천받을 형식(영화, 책 등)", is_required=True),
            InputVariable(name="subject", description="추천 주제", is_required=True),
            InputVariable(name="genre", description="선호 장르", is_required=True),
            InputVariable(name="custom", description="기타 요구사항", is_required=True),
        ],
        execution_settings=execution_settings,
    )

    # 6. 함수 생성 및 등록
    recommend_function = kernel.add_function(
        function_name="RecommendContent", #내마음대로 지정함 - 메서드명에 대응된다
        plugin_name="RecommendationPlugin",#내마음대로 - 자바의 클러스이름에 대응
        prompt_template_config=prompt_template_config, #prompt_template_config 를 입력받아 함수를 작성함
    )

    # 7. 실행부
    # 인자 설정
    args = KernelArguments(
        subject="시간 여행",
        format="영화",
        genre="중세 시대",
        custom="반드시 코미디 요소가 포함되어야 함"
    )

    # 비동기 호출
    result = await kernel.invoke(recommend_function, args)
    
    print("-" * 30)
    print(f"### AI 추천 결과:\n\n{result}")
    print("-" * 30)

if __name__ == "__main__":
    asyncio.run(main())