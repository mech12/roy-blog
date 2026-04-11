import asyncio
from typing import Tuple
import uuid
import semantic_kernel as sk
from semantic_kernel.connectors.ai.open_ai import (
    OpenAIChatCompletion,
    OpenAITextEmbedding,
    AzureChatCompletion,
    AzureTextEmbedding
)

kernel = sk.Kernel()

# Azure OpenAI 사용 여부 설정
useAzureOpenAI = False

# 커널에서 사용할 AI 서비스 구성
if useAzureOpenAI:
    deployment, api_key, endpoint = sk.azure_openai_settings_from_dot_env()
    azure_chat_service = AzureChatCompletion(deployment_name="turbo", endpoint=endpoint, api_key=api_key)
    azure_text_embedding = AzureTextEmbedding(deployment_name="text-embedding", endpoint=endpoint, api_key=api_key)
    kernel.add_chat_service("chat_completion", azure_chat_service)
    kernel.add_text_embedding_generation_service("ada", azure_text_embedding)
else:
    api_key, _ = sk.openai_settings_from_dot_env()
    # GPT-4 모델 및 임베딩 서비스 등록
    oai_chat_service = OpenAIChatCompletion(ai_model_id="gpt-4", api_key=api_key)
    oai_text_embedding = OpenAITextEmbedding(ai_model_id="text-embedding-ada-002", api_key=api_key)
    kernel.add_chat_service("chat-gpt", oai_chat_service)
    kernel.add_text_embedding_generation_service("ada", oai_text_embedding)

# 메모리 저장소 및 핵심 스킬 등록
kernel.register_memory_store(memory_store=sk.memory.VolatileMemoryStore())
kernel.import_skill(sk.core_skills.TextMemorySkill())

# 시맨틱 함수 1: 사용자 선호도 추출기
preferences = kernel.create_semantic_function("""
당신은 선호도 감지기입니다.
대화 기록에서 사용자의 선호도를 추출할 수 있습니다.
새로운 선호도를 쉼표로 구분된 문장 목록으로 추출하세요.
[입력 데이터]
{{$input}}
[입력 종료]
""")

# 시맨틱 함수 2: 질문 맥락 추출기
question_context = kernel.create_semantic_function("""
당신은 사용자 입력에서 관련 맥락을 추출하는 전문가입니다.
메모리에서 추가 정보를 가져오기 위해 사용할 수 있는 가장 관련성 높은 질문을 추출하는 것이 목표입니다.
사용자 입력에서 5개의 관련 질문을 쉼표로 구분하여 추출하세요.
[입력 데이터]
{{$input}}
[입력 종료]
""")

async def populate_memory(kernel: sk.Kernel) -> None:
    """초기 시맨틱 메모리에 사용자 정보를 저장합니다."""
    await kernel.memory.save_information_async(collection="preferences", id="info1", text="나는 시간 여행 주제를 좋아해")
    await kernel.memory.save_information_async(collection="preferences", id="info2", text="내가 선호하는 장르는 SF야")
    await kernel.memory.save_information_async(collection="preferences", id="info3", text="나는 TV 쇼 형태의 콘텐츠를 선호해")
    await kernel.memory.save_information_async(collection="preferences", id="info4", text="나는 1960년 이전의 고전 영화는 별로 좋아하지 않아")
    await kernel.memory.save_information_async(collection="preferences", id="info5", text="내가 가장 좋아하는 배우는 크리스 파인이야")

async def search_memory_examples(kernel: sk.Kernel, input:str) -> None:
    """메모리 검색 예시를 출력합니다."""
    questions = await question_context.invoke_async(input)    
    for question in questions.result.split(","):
        question = question.strip()
        print(f"질문: {question}")
        result = await kernel.memory.search_async("preferences", question)
        if result:
            print(f"답변(메모리): {result[0].text}\n")

async def setup_chat_with_memory(kernel: sk.Kernel) -> Tuple[sk.SKFunctionBase, sk.SKContext]:
    """메모리가 포함된 채팅 설정을 수행합니다."""
    sk_prompt = """
    챗봇은 어떤 주제에 대해서든 당신과 대화할 수 있습니다.
    명확한 지침을 제공하거나, 답을 모를 경우 '잘 모르겠습니다'라고 말할 수 있습니다.

    이전 대화를 통해 파악한 나에 대한 정보:
    - {{$preference1}} {{recall $preference1}}
    - {{$preference2}} {{recall $preference2}}
    - {{$preference3}} {{recall $preference3}}
    - {{$preference4}} {{recall $preference4}}
    - {{$preference5}} {{recall $preference5}}

    대화 기록:
    {{$chat_history}}
    사용자: {{$user_input}}
    챗봇: """.strip()

    chat_func = kernel.create_semantic_function(sk_prompt, max_tokens=200, temperature=0.8)
    context = kernel.create_new_context()
    
    # 초기 컨텍스트 변수 설정
    context["preference1"] = "주제는?"
    context["preference2"] = "장르는?"
    context["preference3"] = "형태는?"
    context["preference4"] = "좋아하거나 싫어하는 것은?"
    context["preference5"] = "좋아하는 배우는?"
    context[sk.core_skills.TextMemorySkill.COLLECTION_PARAM] = "preferences"
    context[sk.core_skills.TextMemorySkill.RELEVANCE_PARAM] = "0.8"
    context["chat_history"] = ""
    return chat_func, context

async def update_memory_context(history, input):    
    """사용자 질문에 따라 메모리 검색용 질문을 업데이트합니다."""
    questions = await question_context.invoke_async(input)    
    context = kernel.create_new_context()
    for i, question in enumerate(questions.result.split(",")):
        if i < 5:
            context[f"preference{i+1}"] = question.strip()
    context[sk.core_skills.TextMemorySkill.COLLECTION_PARAM] = "preferences"
    context[sk.core_skills.TextMemorySkill.RELEVANCE_PARAM] = "0.8"
    context["chat_history"] = history
    return context

async def chat(kernel: sk.Kernel, chat_func: sk.SKFunctionBase, context: sk.SKContext) -> bool:
    """메인 채팅 루프 함수입니다."""
    try:
        user_input = input("사용자:> ")
        context["user_input"] = user_input        
    except (KeyboardInterrupt, EOFError):
        print("\n\n채팅을 종료합니다...")
        return False

    if user_input.lower() == "exit":
        print("\n\n채팅을 종료합니다...")
        return False

    # 질문에 맞는 메모리 컨텍스트 업데이트 및 실행
    updated_context = await update_memory_context(context["chat_history"], user_input)
    answer = await kernel.run_async(chat_func, input_vars=updated_context.variables)
    
    # 대화 기록 업데이트
    context["chat_history"] += f"\n사용자:> {user_input}\n챗봇:> {answer}\n"
    
    # 새로운 선호도 학습 및 메모리 저장
    new_preferences = await preferences.invoke_async(f"{user_input} {answer}")
    for pref in new_preferences.result.split(","):
        pref = pref.strip()
        if pref:
            await kernel.memory.save_information_async(
                collection="preferences",
                id=f"{uuid.uuid4()}",
                text=pref
            )    
    
    print(f"챗봇:> {answer}")
    await search_memory_examples(kernel, user_input)
    return True

async def main():  
    await populate_memory(kernel)    
    print("메모리 기반 채팅 설정 중...")
    chat_func, context = await setup_chat_with_memory(kernel)
    print("대화를 시작합니다 (종료하려면 'exit' 입력):\n")
    
    chatting = True
    while chatting:
        chatting = await chat(kernel, chat_func, context) 

if __name__ == "__main__":
    asyncio.run(main())