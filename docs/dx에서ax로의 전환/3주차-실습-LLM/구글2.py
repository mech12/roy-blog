MyKey = "YOUR_GEMINI_API_KEY"

import os
from google import genai

# 환경변수 설정 (이전에 설정되었다고 가정)
try:
    client = genai.Client(api_key=MyKey)
except Exception as e:
    print(f"클라이언트 초기화 오류: {e}. API 키 설정을 확인하세요.")
    exit()

# 2. 사용할 모델 지정 (예: gemini-2.5-flash)
MODEL_NAME = 'gemini-2.5-flash'

# --- [1단계: 외부 지식 기반 (Knowledge Base) 정의] ---
# 실제 RAG에서는 벡터 DB에 저장되는 내부 매뉴얼/지식 문서입니다.
INTERNAL_KNOWLEDGE_BASE = [
    "Gemini 모델은 2023년 12월에 처음 발표되었습니다.",
    "모델 gemini-2.5-flash는 멀티모달 기능과 빠른 응답 속도를 특징으로 합니다.",
    "Gemini 모델의 파인튜닝은 Google AI Studio를 통해 지원됩니다.",
    "LLM은 환각(Hallucination)이라는 문제를 가집니다."
]

# --- [2단계: 검색 함수 (간소화된 텍스트 매칭)] ---
def simple_knowledge_retriever(query: str) -> str:
    """질문 키워드가 포함된 문서를 찾아 반환합니다. (실제 RAG는 임베딩 벡터 검색 사용)"""
    retrieved_docs = []
    query_keywords = query.lower().split()

    for doc in INTERNAL_KNOWLEDGE_BASE:
        # 질문의 키워드가 문서에 포함되어 있으면 관련 문서로 판단
        if any(keyword in doc.lower() for keyword in query_keywords):
            retrieved_docs.append(doc)

    if not retrieved_docs:
        return "관련 내부 문서를 찾을 수 없습니다."
    
    # 찾은 문서를 하나의 문자열로 결합
    return "\n".join(retrieved_docs)


# --- [3단계: RAG 프롬프트 구성 및 호출] ---
def rag_generate_response(user_question: str):
    """검색된 문서를 프롬프트에 추가하여 응답을 생성합니다."""
    
    # 1. 지식 검색: 질문과 관련된 문서를 찾습니다.
    context_docs = simple_knowledge_retriever(user_question)

    # 2. RAG 시스템 프롬프트 구성
    # LLM에게 검색된 문서를 기반으로 답변하도록 강제합니다.
    system_prompt = f"""
    당신은 사용자 질문에 답변하는 인공지능 전문가입니다.
    답변은 반드시 [검색된 문서]에 있는 내용을 기반으로 작성해야 합니다.
    [검색된 문서]에 답변할 내용이 없다면, '정보가 부족하여 답변할 수 없습니다.'라고 응답하세요.

    [검색된 문서]:
    ---
    {context_docs}
    ---
    """
    
    # 3. 최종 프롬프트 (시스템 + 사용자 질문)
    final_prompt = f"{system_prompt}\n\n사용자 질문: {user_question}"

    # LLM 호출
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=final_prompt
    )
    return response.text

# --- 4. 실행 및 시연 예제 ---
question_1 = "Gemini 모델은 언제 발표되었고 어떤 특징이 있나요?"
print(f"--- [질문 1] {question_1} ---")
print(rag_generate_response(question_1))

question_2 = "인공지능의 윤리 문제에 대해 설명해 주세요."
print(f"\n--- [질문 2] {question_2} ---")
print(rag_generate_response(question_2))