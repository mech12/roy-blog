---
layout: default
title: Vector RAG
parent: RAG
nav_order: 11
has_children: true
permalink: /docs/rag/vector-rag/
---

# Vector RAG 전체 구조 (Architecture)

Vector RAG 시스템은 **"문서를 벡터화해서 검색한 뒤 LLM이 답변을 생성"**하는 구조입니다.

전체 흐름은 아래 6단계로 나뉩니다.

---

## 1. 데이터 수집 (Ingestion Layer)

RAG의 시작 지점으로, 다양한 원본 문서를 수집합니다.

### Input Sources

- 문서 파일: PDF, DOCX, TXT, HTML
- 제품 매뉴얼, 의료 데이터(NHIS 기반), 보험약관
- DB의 Raw Text
- Web crawling 결과
- 내부 지식 DB

### Ingestion Pipeline 구성 요소

- File Upload API (FastAPI 등)
- Document Preprocessor
  - OCR 적용 (Tesseract 등)
  - 페이지 분해
  - 문자열 Normalize
  - 개인정보 마스킹

---

## 2. Chunking Layer (문서 분할)

LLM이 처리할 수 있도록 문서를 **적절한 크기(512~2000 tokens)**로 나누는 단계입니다.

### Chunk 전략

| 전략 | 설명 |
|------|------|
| 규칙 기반 | fixed-length chunk |
| 의미 기반 | sentence/paragraph split |
| 하이브리드 | Semantic Split + Overlap |

### Chunking의 목적

- 검색 Recall 향상
- 컨텍스트 누락 방지
- 임베딩 품질 향상

---

## 3. Embedding Layer (임베딩 생성)

문서 chunk를 벡터로 변환하는 단계입니다.

### 구성 요소

- Sentence Transformer / OpenAI embedding / Llama Embeddings
- GPU 혹은 CPU 기반 embedding server
- 병렬 처리

### 구조

```text
Chunk text → Embedding Model → Vector (float32[], dim=1536~4096)
```

### Embedding 저장

- Vector DB에 저장
- 메타데이터도 함께 저장
  - 문서명
  - 페이지 번호
  - 섹션
  - 업로드 사용자
  - 태그 등

---

## 4. Vector Indexing / Vector Storage Layer

RAG의 핵심은 Vector Retrieval입니다.

### 대표 Vector DB

| Vector DB | 특징 |
|-----------|------|
| FAISS | Self-hosted, Python 기반 |
| Milvus / Zilliz | 고성능 분산 처리 |
| Pinecone | 관리형 서비스 |
| Weaviate | GraphQL 지원 |
| Elasticsearch + kNN | 기존 ES 활용 |

### 벡터 인덱스 방식

- **HNSW** (Hierarchical Navigable Small World Graph)
- **IVF Flat / IVF PQ**
- **DiskANN**

### Metadata Filtering

- 날짜
- 문서 유형
- 카테고리
- User-scoped 데이터

---

## 5. Retriever Layer

사용자가 질문을 하면 vector 검색을 수행합니다.

### Retrieval Flow

```text
User Query → Query Embedding → Vector DB Search (kNN) → Top-k Documents
```

### Retrieval 기법

- **kNN 검색** (Similarity Search)
- **Hybrid Search** (Vector + Keyword)
- **RRF** (Reciprocal Rank Fusion)
- **Context Re-ranking** (Cross-encoder)

### Retrieval Output

- 관련 chunk들 (text)
- 메타데이터

---

## 6. Generation Layer (LLM Prompt Construction)

검색된 문서를 포함하여 LLM에 전달합니다.

### Prompt 구조

```text
SYSTEM: 제공된 문서 기반으로 답변하라.
CONTEXT: (retrieved_chunks)
QUESTION: 사용자 질문
```

### LLM 종류

- OpenAI GPT
- Mistral / Llama
- Self-hosted LLM

### 확장된 RAG 구성 (Advanced RAG)

- Re-ranking
- Answer Verification
- Citation RAG
- Chain of Density
- Memory RAG
- Agentic RAG

---

## 전체 아키텍처 다이어그램

```text
┌────────────────────┐
│   Data Sources     │
│ PDF, DOCX, DB ...  │
└─────────┬──────────┘
          │
    Ingestion API
          │
┌─────────▼──────────┐
│   Preprocessing    │
│   OCR / Cleaning   │
└─────────┬──────────┘
          │
      Chunking
          │
┌─────────▼──────────┐
│     Embedding      │
│ (GPU / CPU Model)  │
└─────────┬──────────┘
          │
 Store Vector + Metadata
          │
┌─────────▼──────────┐
│    Vector DB       │
│ (HNSW / IVF / PQ)  │
└─────────┬──────────┘
          │
   Retrieval (kNN)
          │
┌─────────▼──────────┐
│  Context Builder   │
└─────────┬──────────┘
          │
   LLM Generation
          │
┌─────────▼──────────┐
│      Answer        │
└────────────────────┘
```

---

## 핵심 포인트

### 1. Chunk 전략이 품질의 절반

- 너무 길면 검색 precision 저하
- 너무 짧으면 의미 단위 사라짐

### 2. Vector DB 선택에 따라 성능이 극적으로 달라짐

| Vector DB | 특징 |
|-----------|------|
| FAISS | 저렴하지만 self-managed |
| Milvus | 고성능 |
| Pinecone | 관리형, 비싸지만 편리함 |

### 3. 임베딩 품질이 전체 검색 품질의 결정 요소

### 4. Retrieval + Re-rank로 Recall 개선이 필수

### 5. LLM Prompt Engineering이 최종 답변 품질 결정

---

## 더 알아보기

- Vector RAG + Agents 아키텍처
- Vector RAG + Expressions RAG 구조
- 보험약관/의료데이터 최적 RAG 설계
- Vector RAG 실제 코드 구조 (Python/FastAPI)
