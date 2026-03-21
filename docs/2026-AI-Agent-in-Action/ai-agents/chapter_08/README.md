# Chapter 8: 임베딩과 시맨틱 메모리

## 개요

이 챕터에서는 AI 에이전트의 핵심 구성 요소인 **텍스트 임베딩(Embedding)**과 **시맨틱 메모리(Semantic Memory)**를 다룬다. 문서를 벡터로 변환하여 유사도를 계산하고, 벡터 데이터베이스에 저장하여 의미 기반 검색을 수행하는 전체 파이프라인을 단계별로 학습한다. TF-IDF 기반의 기초적인 벡터화부터 OpenAI 임베딩, ChromaDB 벡터 데이터베이스, LangChain 문서 분할 및 압축 검색, 그리고 Semantic Kernel을 활용한 시맨틱 메모리 통합 챗봇까지 점진적으로 확장해 나간다.

---

## 파일 설명

### 벡터 유사도 및 데이터베이스 기초

| 파일명 | 설명 |
|--------|------|
| `document_vector_database.py` | TF-IDF 벡터화와 코사인 유사도를 사용한 기본 벡터 데이터베이스 구현. scikit-learn만으로 문서 검색 시스템을 구축하는 가장 기초적인 예제이다. |
| `document_vector_similarity.py` | TF-IDF 기반 문서 간 코사인 유사도를 계산하고 Plotly 막대 그래프로 시각화하는 예제. 특정 문서와 나머지 문서 간의 유사도를 직관적으로 비교할 수 있다. |
| `document_visualizing_embeddings.py` | OpenAI의 text-embedding-ada-002 모델로 생성한 임베딩을 PCA로 3차원 축소한 뒤 Plotly 3D 산점도로 시각화한다. 의미적으로 유사한 문서가 공간상에서 가까이 위치하는 것을 확인할 수 있다. |
| `document_query_chromadb.py` | OpenAI 임베딩과 ChromaDB를 결합하여 벡터 데이터베이스를 구축하고, 사용자 쿼리에 대해 의미 기반 검색을 수행하는 예제이다. |

### LangChain 문서 처리 및 검색

| 파일명 | 설명 |
|--------|------|
| `langChain_load_splitting.py` | LangChain의 `RecursiveCharacterTextSplitter`를 사용하여 HTML 문서를 청크 단위로 분할하고 ChromaDB에 저장한 뒤 검색하는 예제이다. 문자 수 기반 분할 방식을 사용한다. |
| `langChain_token_splitting.py` | LangChain의 `CharacterTextSplitter.from_tiktoken_encoder`를 사용하여 토큰 기반으로 문서를 분할하고, Chroma 벡터스토어와 OpenAI 임베딩으로 유사도 검색을 수행한다. |
| `langChain_compression_retrieval.py` | LangChain의 `ContextualCompressionRetriever`와 `LLMChainExtractor`를 활용하여 검색 결과를 LLM으로 압축하는 고급 검색 기법을 구현한다. 검색된 문서에서 쿼리와 관련된 핵심 내용만 추출한다. |

### Semantic Kernel 시맨틱 메모리

| 파일명 | 설명 |
|--------|------|
| `SK_semantic_memory_memory.py` | Semantic Kernel의 `VolatileMemoryStore`에 사용자 선호도 정보를 저장하고, 자연어 질문으로 검색하는 기본 시맨틱 메모리 예제이다. |
| `SK_semantic_memory_prompt.py` | Semantic Kernel에서 `recall` 함수를 사용하여 메모리에 저장된 선호도를 프롬프트에 자동 주입하는 메모리 기반 챗봇을 구현한다. |
| `SK_semantic_memory_preference_skill.py` | 대화 중 사용자의 새로운 선호도를 자동 감지하여 메모리에 저장하는 기능을 추가한 챗봇이다. 대화가 진행될수록 사용자에 대한 이해도가 높아진다. |
| `SK_semantic_memory_context_skill.py` | 사용자 입력에서 관련 질문을 자동 생성하여 메모리를 동적으로 검색하고, 컨텍스트를 자동 업데이트하는 가장 발전된 형태의 메모리 기반 챗봇이다. |
| `SK_semantic_preferences_skill.py` | Semantic Kernel의 시맨틱 함수를 사용하여 대화 텍스트에서 사용자 선호도를 추출하는 독립적인 스킬 예제이다. |

### 유틸리티 및 기타

| 파일명 | 설명 |
|--------|------|
| `util_download_url.py` | Project Gutenberg에서 Mother Goose 동요집 HTML 파일을 다운로드하는 유틸리티 스크립트이다. |
| `testing.py` | LangChain의 `UnstructuredHTMLLoader`로 HTML 문서를 로드하여 내용을 확인하는 테스트 스크립트이다. |
| `requirements.txt` | 프로젝트 의존성 패키지 목록 (scikit-learn, plotly, openai, chromadb, langchain, semantic-kernel 등). |

### 샘플 데이터

| 파일명 | 설명 |
|--------|------|
| `sample_documents/mother_goose.html` | Project Gutenberg에서 가져온 Mother Goose 동요집 HTML 문서. LangChain 문서 분할 및 검색 예제에서 사용된다. |
| `sample_documents/back_to_the_future.txt` | 백 투 더 퓨처 관련 텍스트 데이터. |

---

## 핵심 개념

### 1. 텍스트 임베딩 (Text Embedding)
- **TF-IDF 벡터화**: 단어 빈도 기반의 전통적인 문서 벡터화 방식
- **OpenAI 임베딩**: text-embedding-ada-002 모델을 사용한 밀집 벡터(dense vector) 생성
- **PCA 차원 축소**: 고차원 임베딩을 3차원으로 축소하여 시각적으로 이해

### 2. 벡터 유사도 검색
- **코사인 유사도(Cosine Similarity)**: 두 벡터 간의 방향 유사성을 측정하는 핵심 지표
- **유사도 기반 랭킹**: 쿼리 벡터와 문서 벡터 간 유사도를 계산하여 관련 문서를 순위별로 반환

### 3. 벡터 데이터베이스
- **ChromaDB**: 인메모리 벡터 데이터베이스로 임베딩 저장 및 유사도 검색 수행
- **컬렉션(Collection)**: 관련 문서들을 그룹화하여 관리하는 단위

### 4. 문서 분할 (Document Splitting)
- **문자 기반 분할**: `RecursiveCharacterTextSplitter`로 문자 수 기준 청크 생성
- **토큰 기반 분할**: `tiktoken` 인코더를 활용한 토큰 수 기준 정밀 분할
- **청크 오버랩(Chunk Overlap)**: 분할 경계에서 문맥 손실을 방지하기 위한 겹침 영역 설정

### 5. 압축 검색 (Contextual Compression Retrieval)
- **LLMChainExtractor**: 검색된 문서에서 쿼리와 관련된 핵심 내용만 LLM으로 추출
- **ContextualCompressionRetriever**: 기본 검색기 위에 압축 계층을 추가하여 정밀도를 향상

### 6. 시맨틱 메모리 (Semantic Memory)
- **VolatileMemoryStore**: Semantic Kernel의 인메모리 시맨틱 저장소
- **recall 함수**: 프롬프트 내에서 메모리를 자연어로 검색하여 컨텍스트에 주입
- **동적 선호도 학습**: 대화 중 사용자 선호도를 자동 감지하고 메모리에 축적

---

## 학습 교훈

1. **벡터 표현의 본질 이해가 중요하다.** TF-IDF와 같은 전통적 방법부터 시작하면 임베딩의 원리를 직관적으로 파악할 수 있다. 단어 빈도 기반 희소 벡터(sparse vector)의 한계를 경험한 후 OpenAI 밀집 벡터(dense vector)로 넘어가면, 왜 딥러닝 임베딩이 의미 검색에 더 효과적인지 체감할 수 있다.

2. **시각화는 임베딩을 이해하는 가장 강력한 도구이다.** PCA로 차원을 축소하고 3D 플롯으로 시각화하면, 의미적으로 유사한 문서들이 벡터 공간에서 가까이 군집하는 현상을 눈으로 확인할 수 있다. 이는 벡터 검색이 "왜 작동하는지"를 설명하는 데 핵심적이다.

3. **문서 분할 전략이 검색 품질을 결정한다.** 청크 크기가 너무 크면 관련 없는 내용이 포함되고, 너무 작으면 문맥이 손실된다. 문자 기반 분할과 토큰 기반 분할의 차이를 이해하고, 청크 오버랩을 적절히 설정하는 것이 실전에서 매우 중요하다.

4. **압축 검색은 검색과 생성의 중간 단계이다.** 단순히 유사한 문서를 반환하는 것에서 나아가, LLM을 활용하여 검색 결과에서 쿼리와 직접 관련된 내용만 추출하면 후속 처리의 정확도와 효율성이 크게 향상된다. 이는 RAG(Retrieval-Augmented Generation) 파이프라인의 핵심 기법이다.

5. **시맨틱 메모리는 에이전트에 개인화와 연속성을 부여한다.** 단순한 대화 기록(chat history) 저장을 넘어, 사용자의 선호도와 맥락 정보를 의미 기반으로 저장하고 검색하면 에이전트가 사용자를 "기억"하는 경험을 제공할 수 있다. Semantic Kernel의 recall 함수처럼 프롬프트에 메모리를 자동 주입하는 패턴은 개인화된 AI 에이전트 구축의 핵심이다.

6. **동적 메모리 업데이트가 정적 메모리보다 강력하다.** 대화에서 새로운 선호도를 자동 감지하여 메모리에 추가하는 방식은, 에이전트가 상호작용을 통해 점진적으로 학습하는 효과를 만든다. 다만 메모리가 무한히 늘어나는 것을 방지하는 관리 전략도 함께 고려해야 한다.
