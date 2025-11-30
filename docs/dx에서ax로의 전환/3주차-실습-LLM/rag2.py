import os
import json
from google import genai
from google.genai import types
import sys
from DBModule import Database # DBModule의 Database 클래스 사용 가정

# ⭐️ 1. 설정 및 클라이언트 초기화 ⭐️
MODEL_NAME = 'gemini-2.5-flash' 
# RAG에 최적화된 시스템 지침: 검색 대상을 명확히 합니다.
SYSTEM_INSTRUCTION = (
    "당신은 영화 및 배우 정보에 특화된 전문 지식 챗봇입니다. "
    "사용자의 질문이 **배우 이름**이나 **영화 제목**과 관련이 있을 경우에만 'document_search' 함수를 호출해야 합니다. "
    "검색 결과(retrieved_documents)를 바탕으로 사실에 근거한 답변을 생성하고, 답변에 출처(Source)를 명시해야 합니다. "
    "일반적인 지식 질문(예: 역사, 과학 등)은 함수 호출 없이 답변하세요."
)

MyKey = "YOUR_GEMINI_API_KEY"

# 1. 클라이언트 초기화
if "GEMINI_API_KEY" not in os.environ:
    os.environ["GEMINI_API_KEY"] = MyKey
    
try:
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
except Exception as e:
    print(f"클라이언트 초기화 오류: {e}. API 키 설정을 확인하세요.")
    sys.exit()
# ----------------------------------------------------

# 💡 2. 검색(Retrieval) 함수 정의
# ----------------------------------------------------
def document_search(actor_name: str) -> str:
    """
    영화 데이터베이스에서 특정 배우의 출연 영화 정보를 검색하는 함수입니다.
    배우 이름(actor_name)은 첫 번째 이름(first_name)을 기반으로 검색됩니다.
    """
    
    # ⭐️ 쿼리를 위해 입력받은 배우 이름 준비 ⭐️
    # DB의 first_name LIKE '%[actor_name]%' 검색을 위해 대문자 처리
    search_name = f"%{actor_name.upper()}%" 
    
    actors_data = []
    try:
        with Database() as db:
            sql = """
            SELECT a.actor_id, first_name, last_name, title, description 
            FROM actor as a 
            LEFT OUTER JOIN film_actor as b ON a.actor_id=b.actor_id
            LEFT OUTER JOIN film as c ON b.film_id=c.film_id -- ⭐️ b.film_id=b.film_id -> b.film_id=c.film_id 로 수정 가정
            WHERE first_name LIKE :actor_name OR last_name LIKE :actor_name
            LIMIT 5 -- 너무 많은 데이터 방지
            """
            
            # 쿼리 매개변수에 actor_name 사용
            actors_data = db.executeAll(sql, {"actor_name": search_name})
            
    except Exception as e:
        # DB 연결 오류 시 빈 리스트 반환
        return json.dumps({"error": str(e)})

    # 검색 결과를 LLM이 이해할 수 있는 형태로 포맷하여 JSON 문자열로 반환
    # 데이터가 없으면 빈 리스트를 반환하여 LLM에게 정보가 없음을 알립니다.
    return json.dumps({"retrieved_documents": actors_data})

# 💡 3. 함수 매핑 딕셔너리
AVAILABLE_FUNCTIONS = {
    "document_search": document_search,
}

# ----------------------------------------------------
# 4. 메인 RAG 실행 로직 (수정 없음)
# ----------------------------------------------------
def run_rag_example(user_query: str):
    print("="*60)
    print(f"사용자 입력: {user_query}")
    print("="*60)
    
    # functions 대신 tools 리스트 사용
    tools = [document_search]
    messages = [{"role": "user", "parts": [types.Part.from_text(user_query)]}]

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
        
        print(f"   🐍 함수 실행 완료.")
        
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

# ⭐️ 예제 1: RAG 작동 (영화 관련 질문 -> 함수 호출 예상)
query_rag_1 = "NICK이 출연한 영화제목들을 알려줘."
run_rag_example(query_rag_1)

print("\n" + "="*60 + "\n")

# ⭐️ 예제 2: RAG 작동 (영화 관련 질문 -> 함수 호출 예상)
query_rag_2 = "penelope의 필모그래피를 검색해줘"
run_rag_example(query_rag_2)

print("\n" + "="*60 + "\n")

# ⭐️ 예제 3: 일반 지식 질문 (함수 호출 없음 예상)
query_general = "아이작 뉴턴은 언제 사람이고 무엇을 했는지 설명해봐."
run_rag_example(query_general)