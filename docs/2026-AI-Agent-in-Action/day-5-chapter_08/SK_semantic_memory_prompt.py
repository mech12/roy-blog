import asyncio
from typing import Tuple
import semantic_kernel as sk
from semantic_kernel.connectors.ai.open_ai import (
    OpenAIChatCompletion,
    OpenAITextEmbedding,
    AzureChatCompletion,
    AzureTextEmbedding
)

# 시맨틱 커널 초기화
kernel = sk.Kernel()

useAzureOpenAI = False

# 커널 AI 서비스 설정
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

# 휘발성 메모리 저장소 및 텍스트 메모리 스킬 등록
kernel.register_memory_store(memory_store=sk.memory.VolatileMemoryStore())
kernel.import_skill(sk.core_skills.TextMemorySkill())

async def populate_memory(kernel: sk.Kernel) -> None:
    """장기 기억용 선호도 데이터를 메모리에 저장합니다."""
    await kernel.memory.save_information_async(collection="preferences", id="info1", text="내가 선호하는 주제는 시간 여행이야")
    await kernel.memory.save_information_async(collection="preferences", id="info2", text="내가 선호하는 장르는 SF(공상과학)야")
    await kernel.memory.save_information_async(collection="preferences", id="info3", text="내가 선호하는 포맷은 TV 쇼(드라마)야")
    await kernel.memory.save_information_async(collection="preferences", id="info4", text="나는 1960년 이전의 고전 영화는 좋아하지 않아")
    await kernel.memory.save_information_async(collection="preferences", id="info5", text="내가 가장 좋아하는 배우는 크리스 파인이야")

async def setup_chat_with_memory(kernel: sk.Kernel) -> Tuple[sk.SKFunctionBase, sk.SKContext]:
    """메모리 회상 기능이 포함된 채팅 프롬프트를 설정합니다."""
    # {{recall $변수명}}을 통해 해당 변수의 질문과 유사한 메모리를 자동으로 가져옵니다.
    sk_prompt = """
    챗봇은 당신과 어떤 주제로든 대화할 수 있습니다.
    질문에 대한 답이 없을 경우 '잘 모르겠습니다'라고 정직하게 답변합니다.

    이전 대화를 통해 알고 있는 나에 대한 정보:
    - 주제 선호도: {{recall $preference1}}
    - 장르 선호도: {{recall $preference2}}
    - 포맷 선호도: {{recall $preference3}}
    - 호불호: {{recall $preference4}}
    - 좋아하는 배우: {{recall $preference5}}

    대화 기록:
    {{$chat_history}}
    사용자: {{$user_input}}
    챗봇: """.strip()

    chat_func = kernel.create_semantic_function(sk_prompt, max_tokens=200, temperature=0.8)

    context = kernel.create_new_context()
    # recall을 위한 질문 키워드 설정
    context["preference1"] = "주제(subject)?"
    context["preference2"] = "장르(genre)?"
    context["preference3"] = "포맷(format)?"
    context["preference4"] = "좋아하거나 싫어하는 것?"
    context["preference5"] = "좋아하는 배우?"

    # 메모리 검색 시 사용할 컬렉션과 유사도 기준 설정
    context[sk.core_skills.TextMemorySkill.COLLECTION_PARAM] = "preferences"
    context[sk.core_skills.TextMemorySkill.RELEVANCE_PARAM] = "0.8"
    context["chat_history"] = ""

    return chat_func, context

async def chat(kernel: sk.Kernel, chat_func: sk.SKFunctionBase, context: sk.SKContext) -> bool:
    """메인 채팅 루프"""
    try:
        user_input = input("사용자:> ")
        context["user_input"] = user_input        
    except (KeyboardInterrupt, EOFError):
        print("\n\n채팅을 종료합니다...")
        return False

    if user_input.lower() == "exit":
        print("\n\n채팅을 종료합니다...")
        return False

    # 채팅 실행 및 응답 출력
    answer = await kernel.run_async(chat_func, input_vars=context.variables)
    context["chat_history"] += f"\n사용자:> {user_input}\n챗봇:> {answer}\n"

    print(f"챗봇:> {answer}")
    return True

async def main():  
    await populate_memory(kernel)    
    print("메모리 기반 채팅 서비스를 설정 중입니다...")
    chat_func, context = await setup_chat_with_memory(kernel)

    print("대화를 시작합니다 (종료하려면 'exit' 입력):\n")
    chatting = True
    while chatting:
        chatting = await chat(kernel, chat_func, context)

# 실행
if __name__ == "__main__":
    asyncio.run(main())