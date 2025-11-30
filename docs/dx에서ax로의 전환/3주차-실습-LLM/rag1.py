import json
from google import genai
from google.genai import types
import sys

# ⭐️ 1. 설정 및 클라이언트 초기화 ⭐️
MODEL_NAME = 'gemini-2.5-flash' 
# RAG에 최적화된 시스템 지침: 검색 결과를 반드시 사용하도록 지시합니다.
SYSTEM_INSTRUCTION = (
    "당신은 전문 지식 챗봇입니다. 사용자의 질문에 답변하기 위해 'document_search' 함수를 사용하여 "
    "최대한 관련 문서를 검색해야 합니다. 검색 결과(retrieved_documents)를 바탕으로 "
    "사실에 근거한 답변을 생성하고, 답변에 출처(Source)를 명시해야 합니다."
)

MyKey = "YOUR_GEMINI_API_KEY"


# 1. 클라이언트 초기화
# 환경 변수에서 GEMINI_API_KEY를 자동으로 찾습니다.
try:
    client = genai.Client(api_key=MyKey)
except Exception as e:
    print(f"클라이언트 초기화 오류: {e}. API 키 설정을 확인하세요.")
    exit()
# ----------------------------------------------------
# 💡 2. 검색(Retrieval) 함수 정의
# ----------------------------------------------------
# 이 함수는 실제로는 벡터 DB나 검색 엔진 API를 호출하지만, 여기서는 가상 데이터를 사용합니다.
def document_search(query: str) -> str:
    """
    사용자의 질문(query)과 관련된 내부 문서를 검색하여 LLM에게 제공하는 검색 함수입니다.
    """
    print(f"\n   **[함수 실행]** 문서 검색 중... 쿼리: '{query}'")
    
    # ⭐️ 실제 데이터베이스 검색 결과 (가상 데이터)
    if "인공지능" in query.lower() or "llm" in query.lower():
        documents = [
            "Source 1: 대규모 언어 모델(LLM)은 방대한 텍스트 데이터를 학습하여 자연어 이해 및 생성을 수행합니다.",
            "Source 2: RAG는 LLM의 지식 한계를 극복하기 위해 외부 문서 검색을 결합하는 기술입니다.",
            "Source 3: Gemini는 Google에서 개발한 최신 멀티모달 LLM 제품군입니다."
        ]
    elif "뉴턴" in query.lower() or "만유인력" in query.lower():
        documents = [
            "Source 1: 아이작 뉴턴은 17세기 영국의 물리학자이자 수학자입니다.",
            "Source 2: 만유인력의 법칙은 두 질량을 가진 물체 사이에 작용하는 인력을 설명합니다."
        ]
    else:
        documents = ["Source 1: 관련된 문서를 찾을 수 없습니다."]
        
    # 검색 결과를 LLM이 이해할 수 있는 형태로 포맷하여 JSON 문자열로 반환
    return json.dumps({"retrieved_documents": documents})

# ⭐️ 1. 핵심 변화: 외부 Vector DB와 유사성 검색을 시뮬레이션하는 함수 ⭐️
def retrieve_relevant_documents(user_query: str) -> str:
    """
    사용자의 질문을 벡터로 변환하고, Vector Database에 접근하여 
    유사도가 높은 상위 3개의 문서를 검색(Retrieval)한 결과를 반환합니다.
    """
    print(f"\n   **[함수 실행]** 1. 질문 임베딩 변환 및 2. Vector DB 유사성 검색 중... (쿼리: '{user_query}')")
    
    # ⭐️ 실제 RAG 환경의 시뮬레이션:
    # 1) user_query를 임베딩 모델(예: text-embedding-004)로 벡터화합니다.
    # 2) 벡터를 Vector DB(예: Pinecone, Weaviate, ChromaDB)에 전달하여 검색합니다.
    # 3) DB는 가장 유사한 문서 조각(Chunk)을 반환합니다.

    # ⭐️ 가상 검색 결과 (유사도 기반으로 데이터를 가져왔다고 가정)
    if "정책" in user_query.lower() or "규정" in user_query.lower():
        # 정책 관련 질문의 검색 결과
        retrieved_chunks = [
            "Source A (2025년 업데이트): 연차 휴가는 최소 15일이며, 미사용 시 익년 2월까지 보상 가능함.",
            "Source B (근무 지침): 재택 근무는 주 2회까지 허용되며, 상사의 승인이 필요함.",
            "Source C (복리후생): 사내 피트니스 시설은 모든 직원이 무료로 사용할 수 있습니다."
        ]
        
    elif "신제품" in user_query.lower() or "출시" in user_query.lower():
        # 신제품 관련 질문의 검색 결과
        retrieved_chunks = [
            "Source D (제품 로드맵): 'Project Nova'는 2026년 3분기에 출시 예정인 AI 기반 데이터 분석 솔루션입니다.",
            "Source E (마케팅): 새 제품의 초기 목표 고객은 중소기업의 마케팅 팀입니다."
        ]
        
    else:
        retrieved_chunks = ["Source Z: 내부 데이터베이스에서 질문과 관련된 문서를 찾지 못했습니다."]

    # LLM이 사용할 수 있도록 결과를 JSON 형식으로 포맷합니다.
    return json.dumps({"retrieved_documents": retrieved_chunks})

# 💡 3. 함수 매핑 딕셔너리
AVAILABLE_FUNCTIONS = {
    "document_search": document_search,
}

# ----------------------------------------------------
# 4. 메인 RAG 실행 로직
# ----------------------------------------------------
def run_rag_example(user_query: str):
    print("="*60)
    print(f"사용자 입력: {user_query}")
    print("="*60)
    
    tools = [document_search]
    messages = [{"role": "user", "parts": [types.Part(text=user_query)]}]

    # 1차 API 호출: LLM에게 질문과 검색 함수를 제공하고 판단을 요청합니다.
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=messages,
        config=types.GenerateContentConfig(
            tools=tools,
            system_instruction=SYSTEM_INSTRUCTION
        )
    )

    # 2단계: LLM이 검색 함수 호출을 요청했는지 확인
    if response.function_calls:
        function_call = response.function_calls[0]
        function_name = function_call.name
        function_args = dict(function_call.args)

        print(f"🤖 1차 응답: '{function_name}' 호출 요청 (인수: {function_args})")
        
        # 3단계: 로컬에서 검색 함수 실행
        function_to_call = AVAILABLE_FUNCTIONS.get(function_name)
        tool_response_json = function_to_call(**function_args)
        
        print(f"   🐍 함수 실행 완료.")
        
        # 4단계: 검색 결과를 모델에게 다시 전달 (Augmentation 단계)
        messages.append(response.candidates[0].content)
        messages.append(
            types.Content(
                role='tool',
                parts=[
                    types.Part.from_function_response(
                        name=function_name, 
                        response={"result": tool_response_json}
                    )
                ]
            )
        )

        # 5단계: 최종 답변 요청 (2차 API 호출) - 검색 결과를 바탕으로 답변을 생성합니다.
        final_response = client.models.generate_content(
            model=MODEL_NAME,
            contents=messages,
        )

        print(f"\n✅ 최종 AI 답변:\n{final_response.text.strip()}")
            
    else:
        print(f"\n**AI 응답:** 함수 호출 없이 바로 답변합니다.")
        print(response.text.strip())

# --- 실행 예제 ---

# ⭐️ 예제 1: RAG 작동 (검색 함수 호출 예상)
query_rag_1 = "RAG가 무엇인지 자세히 설명해주고, LLM의 한계를 어떻게 극복하는지 알려줘."
run_rag_example(query_rag_1)

print("\n" + "="*60 + "\n")

# ⭐️ 예제 2: RAG 작동 (다른 주제 검색)
query_rag_2 = "아이작 뉴턴은 언제 사람이고 무엇을 했는지 설명해봐."
run_rag_example(query_rag_2)