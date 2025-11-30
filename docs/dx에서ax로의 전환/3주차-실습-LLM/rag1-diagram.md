# RAG (Retrieval-Augmented Generation) 흐름도

`rag1.py` 코드의 RAG 아키텍처를 시각화한 다이어그램입니다.

## 전체 아키텍처

![전체 아키텍처](rag1-architecture.png)

<details>
<summary>Mermaid 소스 코드</summary>

```mermaid
flowchart TB
    subgraph User["👤 사용자"]
        Q[질문 입력]
    end

    subgraph LLM["🤖 Gemini LLM"]
        M1[1차 API 호출<br/>질문 분석]
        M2[2차 API 호출<br/>최종 답변 생성]
    end

    subgraph Retrieval["📚 검색 시스템"]
        DF[document_search 함수]
        DB[(가상 문서 DB)]
    end

    Q --> M1
    M1 -->|Function Call 요청| DF
    DF --> DB
    DB -->|검색 결과| DF
    DF -->|retrieved_documents| M2
    M2 -->|최종 답변| A[답변 출력]

    style User fill:#e1f5fe
    style LLM fill:#fff3e0
    style Retrieval fill:#e8f5e9
```

</details>

## 상세 실행 흐름

![상세 실행 흐름](rag1-sequence.png)

<details>
<summary>Mermaid 소스 코드</summary>

```mermaid
sequenceDiagram
    autonumber
    participant U as 👤 사용자
    participant C as 🐍 Python Client
    participant G as 🤖 Gemini API
    participant F as 📚 document_search

    U->>C: 질문 입력
    Note over C: messages 리스트 생성<br/>tools=[document_search]

    C->>G: 1차 API 호출<br/>(질문 + 시스템 지침 + 도구 정의)

    G-->>C: Function Call 응답<br/>{name: "document_search", args: {query: "..."}}

    Note over C: function_calls 확인

    C->>F: 함수 실행<br/>document_search(query)

    Note over F: 쿼리 키워드 매칭<br/>(인공지능/LLM/뉴턴 등)

    F-->>C: JSON 결과 반환<br/>{retrieved_documents: [...]}

    Note over C: messages에 추가<br/>- LLM 응답<br/>- 함수 결과 (role: tool)

    C->>G: 2차 API 호출<br/>(전체 대화 히스토리)

    G-->>C: 최종 답변 텍스트

    C->>U: 답변 출력
```

</details>

## 코드 구조

![코드 구조](rag1-class.png)

<details>
<summary>Mermaid 소스 코드</summary>

```mermaid
classDiagram
    class Configuration {
        +MODEL_NAME: gemini-2.5-flash
        +SYSTEM_INSTRUCTION: str
        +MyKey: API_KEY
        +client: genai.Client
    }

    class DocumentSearch {
        +document_search(query: str) str
        +retrieve_relevant_documents(query: str) str
        -가상 문서 데이터
    }

    class RAGEngine {
        +run_rag_example(user_query: str)
        -tools: list
        -messages: list
    }

    class AVAILABLE_FUNCTIONS {
        +document_search: function
    }

    Configuration --> RAGEngine : 설정 제공
    DocumentSearch --> AVAILABLE_FUNCTIONS : 함수 등록
    AVAILABLE_FUNCTIONS --> RAGEngine : 함수 조회
    RAGEngine --> DocumentSearch : 함수 호출
```

</details>

## 검색 로직 분기

![검색 로직 분기](rag1-search-logic.png)

<details>
<summary>Mermaid 소스 코드</summary>

```mermaid
flowchart TD
    Q[query 입력] --> C1{인공지능 OR LLM<br/>키워드 포함?}

    C1 -->|Yes| R1["📄 LLM/RAG 관련 문서 3개<br/>- LLM 정의<br/>- RAG 설명<br/>- Gemini 소개"]

    C1 -->|No| C2{뉴턴 OR 만유인력<br/>키워드 포함?}

    C2 -->|Yes| R2["📄 뉴턴 관련 문서 2개<br/>- 뉴턴 소개<br/>- 만유인력 법칙"]

    C2 -->|No| R3["⚠️ 관련 문서 없음"]

    R1 --> J[JSON 변환]
    R2 --> J
    R3 --> J

    J --> RET[retrieved_documents 반환]

    style R1 fill:#c8e6c9
    style R2 fill:#c8e6c9
    style R3 fill:#ffcdd2
```

</details>

## 핵심 개념

| 단계 | 설명 |
|------|------|
| **Retrieval** | 사용자 질문을 기반으로 관련 문서 검색 |
| **Augmentation** | 검색된 문서를 LLM 컨텍스트에 추가 |
| **Generation** | 검색 결과를 참고하여 최종 답변 생성 |
