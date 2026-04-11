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

# Azure OpenAI 사용 여부 설정
useAzureOpenAI = False

# 커널에서 사용할 AI 서비스 구성
if useAzureOpenAI:
    deployment, api_key, endpoint = sk.azure_openai_settings_from_dot_env()
    # Azure 채팅 서비스 등록
    azure_chat_service = AzureChatCompletion(deployment_name="turbo", endpoint=endpoint, api_key=api_key)
    # Azure 임베딩 서비스 등록
    azure_text_embedding = AzureTextEmbedding(deployment_name="text-embedding", endpoint=endpoint, api_key=api_key)
    kernel.add_chat_service("chat_completion", azure_chat_service)
    kernel.add_text_embedding_generation_service("ada", azure_text_embedding)
else:
    api_key, _ = sk.openai_settings_from_dot_env()
    # OpenAI 채팅 모델 설정 (GPT-4.1 예시)
    oai_chat_service = OpenAIChatCompletion(ai_model_id="gpt-4.1", api_key=api_key)
    # OpenAI 임베딩 모델 설정 (text-embedding-ada-002)
    oai_text_embedding = OpenAITextEmbedding(ai_model_id="text-embedding-ada-002", api_key=api_key)
    kernel.add_chat_service("chat-gpt", oai_chat_service)
    kernel.add_text_embedding_generation_service("ada", oai_text_embedding)

# 휘발성 메모리 저장소 등록 및 텍스트 메모리 스킬 임포트
kernel.register_memory_store(memory_store=sk.memory.VolatileMemoryStore())
kernel.import_skill(sk.core_skills.TextMemorySkill())

async def populate_memory(kernel: sk.Kernel) -> None:
    """시맨틱 메모리에 샘플 데이터(사용자 선호도)를 저장합니다."""
    # 정보를 벡터화하여 'preferences' 컬렉션에 저장
    await kernel.memory.save_information_async(
        collection="preferences",
        id="info1", 
        text="내가 선호하는 주제는 시간 여행이야."
    )
    await kernel.memory.save_information_async(
        collection="preferences", 
        id="info2", 
        text="내가 선호하는 장르는 SF(공상과학)야."
    )
    await kernel.memory.save_information_async(
       collection= "preferences",
       id="info3", 
       text="내가 선호하는 포맷은 TV 프로그램이야."
    )
    await kernel.memory.save_information_async(
        collection="preferences",
        id="info4",
        text="나는 1960년 이전의 고전 영화는 좋아하지 않아."
    )
    await kernel.memory.save_information_async(
        collection="preferences",
        id="info5",
        text="내가 가장 좋아하는 배우는 크리스 파인이야."
    )    

async def search_memory_examples(kernel: sk.Kernel) -> None:
    """저장된 메모리를 대상으로 유사도 검색을 수행합니다."""
    # 검색할 질문 리스트
    questions = [
        "선호하는 주제는?",
        "어떤 장르를 좋아해?",
        "어떤 포맷으로 보는 걸 좋아해?",
        "좋아하거나 싫어하는 게 있어?",
        "가장 좋아하는 배우는 누구야?",
    ]

    print("[메모리 검색 결과]\n")
    for question in questions:
        print(f"질문: {question}")
        # 질문과 가장 유사한 정보를 메모리에서 검색
        result = await kernel.memory.search_async("preferences", question)
        if result:
            print(f"답변: {result[0].text}\n")
        else:
            print("관련된 정보를 찾을 수 없습니다.\n")
        
async def main():
    print("메모리에 데이터를 채우는 중...")
    await populate_memory(kernel)
    
    print("메모리 검색 테스트를 시작합니다...\n")
    await search_memory_examples(kernel)

# 이벤트 루프 실행
if __name__ == "__main__":
    asyncio.run(main())