---
layout: default
title: 3주차 - LLM
parent: DX 전환
nav_order: 3
has_children: true
---

# 3주차: LLM이란

## 이론 자료

[📥 3주차-LLM이란-2025-1129.pptx 다운로드](3주차-LLM이란-2025-1129.pptx)

---

## 실습: LLM 활용

### 환경 설정

```bash
conda activate myenv

# 필요 라이브러리 설치
pip install langchain langchain-google-genai google-generativeai
```

### 실습 1: LangChain 기본 사용법

```python
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# API 키 설정
os.environ["GEMINI_API_KEY"] = "your-api-key"

# 1. 모델 생성
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

# 2. 프롬프트 템플릿
prompt = ChatPromptTemplate.from_messages([
    ("system", "당신은 친절한 AI 어시스턴트입니다."),
    ("user", "{input}")
])

# 3. LCEL 체인 구축
chain = prompt | llm | StrOutputParser()

# 4. 실행
response = chain.invoke({"input": "인공지능이란 무엇인가요?"})
print(response)
```

### 실습 2: RAG (Retrieval-Augmented Generation)

```python
import json
from google import genai
from google.genai import types

# RAG 시스템 구성요소
# 1. 검색 함수 (Vector DB 시뮬레이션)
def document_search(query: str) -> str:
    """문서 검색 함수"""
    if "정책" in query or "규정" in query:
        documents = [
            "연차 휴가는 최소 15일이며, 미사용 시 익년 2월까지 보상 가능",
            "재택 근무는 주 2회까지 허용, 상사 승인 필요"
        ]
    else:
        documents = ["관련 문서를 찾을 수 없습니다."]

    return json.dumps({"retrieved_documents": documents})

# 2. RAG 파이프라인
# Query → 문서 검색 → LLM에 컨텍스트 전달 → 답변 생성
```

### 핵심 개념

| 용어 | 설명 |
|------|------|
| **LLM** | Large Language Model, 대규모 언어 모델 |
| **LangChain** | LLM 애플리케이션 개발 프레임워크 |
| **LCEL** | LangChain Expression Language, 체인 구성 문법 |
| **RAG** | Retrieval-Augmented Generation, 검색 증강 생성 |
| **프롬프트** | LLM에 전달하는 입력 텍스트 |
| **Function Calling** | LLM이 외부 함수를 호출하는 기능 |

### RAG 아키텍처

```
사용자 질문
    ↓
┌─────────────────┐
│  1. 검색(Retrieve)  │ → Vector DB에서 관련 문서 검색
└─────────────────┘
    ↓
┌─────────────────┐
│  2. 증강(Augment)   │ → 검색 결과를 프롬프트에 추가
└─────────────────┘
    ↓
┌─────────────────┐
│  3. 생성(Generate)  │ → LLM이 컨텍스트 기반 답변 생성
└─────────────────┘
    ↓
최종 답변
```

### 실습 파일 목록

**[전체 실습 코드 보기](3주차-코드/)** - 클릭하면 소스 코드 확인 가능

| 파일 | 설명 |
|------|------|
| [랭체인1.py](3주차-코드/랭체인1) | LangChain + Gemini 기본 사용법 |
| [구글1.py](3주차-코드/구글1) | Google Gemini API 기본 호출 |
| [챗봇1.py](3주차-코드/챗봇1) | 대화형 챗봇 (세션 관리) |
| [함수1.py](3주차-코드/함수1) | Function Calling 구현 |
| [rag1.py](3주차-코드/rag1) | RAG 기본 구현 |
| [오픈1.py](3주차-코드/오픈1) | OpenAI GPT API 대화 예제 |
