---
layout: default
title: rag1.py
parent: 3주차 코드
grand_parent: 3주차 - LLM
nav_order: 5
---

# rag1.py

RAG (Retrieval-Augmented Generation) 기본 구현

---

## 개요

| 항목 | 내용 |
|-----|------|
| **RAG** | 검색 증강 생성 - LLM + 외부 문서 검색 |
| **목적** | LLM의 지식 한계 극복, 최신 정보 활용 |
| **구성** | 검색(Retrieve) → 증강(Augment) → 생성(Generate) |

---

## RAG 아키텍처

```
사용자 질문: "RAG가 뭐야?"
         ↓
┌─────────────────────────────┐
│  1. 검색 (Retrieve)         │
│  → 관련 문서 검색            │
│  → "RAG는 LLM의 한계를..."   │
└─────────────┬───────────────┘
              ↓
┌─────────────────────────────┐
│  2. 증강 (Augment)          │
│  → 검색 결과를 프롬프트에 추가 │
└─────────────┬───────────────┘
              ↓
┌─────────────────────────────┐
│  3. 생성 (Generate)         │
│  → 컨텍스트 기반 답변 생성    │
│  → 출처 포함                 │
└─────────────────────────────┘
```

---

## 전체 소스 코드

```python
import json
from google import genai
from google.genai import types

# ⭐️ 1. 설정 및 클라이언트 초기화
MODEL_NAME = 'gemini-2.5-flash'
MyKey = "YOUR_GEMINI_API_KEY"

# RAG에 최적화된 시스템 지침
SYSTEM_INSTRUCTION = (
    "당신은 전문 지식 챗봇입니다. 사용자의 질문에 답변하기 위해 "
    "'document_search' 함수를 사용하여 관련 문서를 검색해야 합니다. "
    "검색 결과(retrieved_documents)를 바탕으로 사실에 근거한 답변을 생성하고, "
    "답변에 출처(Source)를 명시해야 합니다."
)

client = genai.Client(api_key=MyKey)

# 💡 2. 검색(Retrieval) 함수 정의
def document_search(query: str) -> str:
    """
    사용자의 질문(query)과 관련된 내부 문서를 검색합니다.
    실제로는 Vector DB를 사용하지만, 여기서는 가상 데이터로 시뮬레이션합니다.
    """
    print(f"\n   **[함수 실행]** 문서 검색 중... 쿼리: '{query}'")

    # ⭐️ 가상 검색 결과 (실제로는 Vector DB 조회)
    if "인공지능" in query.lower() or "llm" in query.lower():
        documents = [
            "Source 1: 대규모 언어 모델(LLM)은 방대한 텍스트 데이터를 학습합니다.",
            "Source 2: RAG는 LLM의 지식 한계를 극복하기 위한 기술입니다.",
            "Source 3: Gemini는 Google에서 개발한 최신 LLM입니다."
        ]
    elif "뉴턴" in query.lower() or "만유인력" in query.lower():
        documents = [
            "Source 1: 아이작 뉴턴은 17세기 영국의 물리학자입니다.",
            "Source 2: 만유인력의 법칙은 두 물체 사이의 인력을 설명합니다."
        ]
    else:
        documents = ["Source 1: 관련 문서를 찾을 수 없습니다."]

    return json.dumps({"retrieved_documents": documents})

# 💡 3. 함수 매핑
AVAILABLE_FUNCTIONS = {
    "document_search": document_search,
}

# 4. 메인 RAG 실행 로직
def run_rag_example(user_query: str):
    print("=" * 60)
    print(f"사용자 입력: {user_query}")
    print("=" * 60)

    tools = [document_search]
    messages = [{"role": "user", "parts": [types.Part(text=user_query)]}]

    # 1차 API 호출: LLM에게 질문과 검색 함수 제공
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

        print(f"🤖 1차 응답: '{function_name}' 호출 요청")

        # 3단계: 로컬에서 검색 함수 실행
        function_to_call = AVAILABLE_FUNCTIONS.get(function_name)
        tool_response_json = function_to_call(**function_args)

        print(f"   🐍 함수 실행 완료.")

        # 4단계: 검색 결과를 모델에게 다시 전달 (Augmentation)
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

        # 5단계: 최종 답변 요청 (2차 API 호출)
        final_response = client.models.generate_content(
            model=MODEL_NAME,
            contents=messages,
        )

        print(f"\n✅ 최종 AI 답변:\n{final_response.text.strip()}")

    else:
        print(f"\n**AI 응답:** 함수 호출 없이 바로 답변")
        print(response.text.strip())

# --- 실행 예제 ---

# 예제 1: RAG 작동 (검색 함수 호출)
query1 = "RAG가 무엇인지 자세히 설명해줘."
run_rag_example(query1)

print("\n" + "=" * 60 + "\n")

# 예제 2: 다른 주제 검색
query2 = "아이작 뉴턴은 어떤 사람이야?"
run_rag_example(query2)
```

---

## 핵심 개념

### 1. 검색 함수 정의

```python
def document_search(query: str) -> str:
    # 실제로는 Vector DB에서 유사 문서 검색
    # 여기서는 키워드 기반 시뮬레이션
    if "llm" in query.lower():
        documents = ["Source 1: LLM은...", "Source 2: RAG는..."]
    return json.dumps({"retrieved_documents": documents})
```

---

### 2. 시스템 지침 설정

```python
SYSTEM_INSTRUCTION = (
    "검색 결과를 바탕으로 답변하고, 출처를 명시하세요."
)
```

LLM이 항상 검색 함수를 사용하도록 유도

---

### 3. 검색 결과를 LLM에 전달

```python
messages.append(
    types.Content(
        role='tool',
        parts=[
            types.Part.from_function_response(
                name="document_search",
                response={"result": tool_response_json}
            )
        ]
    )
)
```

---

## 실행 예시

```
============================================================
사용자 입력: RAG가 무엇인지 자세히 설명해줘.
============================================================
🤖 1차 응답: 'document_search' 호출 요청

   **[함수 실행]** 문서 검색 중... 쿼리: 'RAG'
   🐍 함수 실행 완료.

✅ 최종 AI 답변:
RAG(Retrieval-Augmented Generation)는 대규모 언어 모델(LLM)의 한계를
극복하기 위한 기술입니다.

LLM은 학습 데이터에 없는 최신 정보나 특정 도메인 지식에 취약할 수 있는데,
RAG는 외부 문서를 검색하여 이러한 한계를 보완합니다.

**출처:**
- Source 1: LLM은 방대한 텍스트 데이터를 학습합니다.
- Source 2: RAG는 LLM의 지식 한계를 극복하기 위한 기술입니다.
```

---

## 실제 RAG 시스템 구성

| 구성요소 | 설명 | 도구 예시 |
|---------|------|----------|
| **Vector DB** | 문서를 벡터로 저장 | Pinecone, ChromaDB, Weaviate |
| **Embedding** | 텍스트 → 벡터 변환 | text-embedding-004 |
| **Chunking** | 문서 분할 | LangChain TextSplitter |
| **Retriever** | 유사 문서 검색 | 코사인 유사도 |
