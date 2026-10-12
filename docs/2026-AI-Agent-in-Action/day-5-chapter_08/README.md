# Chapter 08 - 메모리와 지식 검색 (RAG)

AI 에이전트에 **장기 기억(Long-term Memory)** 과 **문서 기반 지식 검색(RAG)** 을 부여하는 방법을 다루는 실습 자료입니다.
TF-IDF부터 임베딩 벡터 DB(ChromaDB), LangChain 문서 파이프라인, Semantic Kernel의 Semantic Memory까지 단계별로 학습합니다.

## 학습 목표

1. **벡터 임베딩의 원리**: TF-IDF 기반 유사도 → OpenAI Embedding 기반 의미 검색으로의 발전 이해
2. **벡터 데이터베이스**: ChromaDB를 사용한 임베딩 저장/검색
3. **LangChain 문서 파이프라인**: HTML 로더 → 텍스트 분할 → 벡터화 → 검색 → 문맥 압축
4. **Semantic Kernel 메모리**: `{{recall}}` 프롬프트로 챗봇에 장기 기억 연결, 자동 선호도 학습

## 환경 설정

```bash
pip install -r requirements.txt
```

### requirements.txt 주요 패키지

| 패키지 | 용도 |
| --- | --- |
| `scikit-learn` | TF-IDF 벡터화, 코사인 유사도, PCA 차원 축소 |
| `plotly` | 2D/3D 임베딩 시각화 |
| `openai` | Embedding API (`text-embedding-3-small`, `ada-002`) |
| `chromadb` | 벡터 데이터베이스 |
| `langchain` | 문서 로더, 텍스트 분할기, Retriever |
| `unstructured` | HTML/비정형 문서 파서 |
| `python-dotenv` | `.env`에서 API 키 로드 |

### API 키 설정

`.env` 파일에 OpenAI API 키를 설정합니다.

```env
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx
```

## 실습 파일 구성

실습은 크게 **3개 트랙**으로 나뉩니다.

### 트랙 1: 벡터 임베딩 & 유사도 검색 기초

TF-IDF로 시작해서 OpenAI Embedding으로 넘어가며 "왜 의미 기반 검색이 필요한가"를 체감합니다.

| 파일 | 설명 |
| --- | --- |
| [document_vector_database.py](document_vector_database.py) | **TF-IDF + 코사인 유사도** 기본 실습. 영문 샘플 8개를 TF-IDF로 벡터화하고 쿼리 문장과의 유사도를 직접 계산. 상위 N개 검색 결과 출력 |
| [document_vector_similarity.py](document_vector_similarity.py) | 한글 샘플로 TF-IDF 유사도를 **Plotly 막대그래프**로 시각화. 선택한 문서와 나머지 문서 간의 유사도 분포 확인 |
| [document_query_chromadb.py](document_query_chromadb.py) | **OpenAI Embedding + ChromaDB** 조합. `text-embedding-3-small`로 한글 문장을 벡터화하여 ChromaDB 컬렉션에 저장 후 의미 기반 검색 수행 |
| [document_visualizing_embeddings.py](document_visualizing_embeddings.py) | OpenAI Embedding(1536차원)을 **PCA로 3차원 축소**한 뒤 Plotly 3D 산점도로 시각화. 의미적으로 유사한 문서들이 공간적으로 클러스터링되는 것을 확인 |

### 트랙 2: LangChain 문서 파이프라인 (RAG)

실제 문서(마더구스 동요집 HTML)를 로드하여 검색 가능한 형태로 가공하는 전체 파이프라인 실습입니다.

| 파일 | 설명 |
| --- | --- |
| [util_download_url.py](util_download_url.py) | Project Gutenberg에서 마더구스 동요집 HTML을 다운로드하여 `sample_documents/mother_goose.html`로 저장 |
| [testing.py](testing.py) | `UnstructuredHTMLLoader`로 HTML 로딩 동작 확인용 미니 스크립트 |
| [langChain_load_splitting.py](langChain_load_splitting.py) | **HTML 로드 → RecursiveCharacterTextSplitter로 분할(chunk=100, overlap=25) → OpenAI 임베딩 → ChromaDB 저장 → 검색**. 조각 단위(`page_content`)로 ChromaDB `add()`를 직접 호출하는 저수준 방식 |
| [langChain_token_splitting.py](langChain_token_splitting.py) | **Tiktoken 기반 분할**(chunk=50 tokens, overlap=10). `Chroma.from_documents()`로 LangChain 래퍼를 사용해 벡터 스토어를 한 번에 구성하는 고수준 방식 |
| [langChain_compression_retrieval.py](langChain_compression_retrieval.py) | **ContextualCompressionRetriever + LLMChainExtractor**. 검색된 긴 문서에서 **질문과 관련된 핵심만 LLM으로 압축 추출**하여 토큰 낭비를 줄이는 고급 검색 기법 |
| [sample_documents/mother_goose.html](sample_documents/mother_goose.html) | Project Gutenberg에서 다운로드한 마더구스 동요집 원문 (실습용 샘플) |
| [sample_documents/back_to_the_future.txt](sample_documents/back_to_the_future.txt) | 추가 실습용 텍스트 샘플 |

### 트랙 3: Semantic Kernel Memory — 에이전트 장기 기억

Semantic Kernel의 `VolatileMemoryStore`와 `TextMemorySkill`을 사용해 **챗봇에 장기 기억**을 부여하는 실습입니다.
점진적으로 복잡도가 올라가는 5단계 구성입니다.

| 단계 | 파일 | 설명 |
| --- | --- | --- |
| 1 | [SK_semantic_preferences_skill.py](SK_semantic_preferences_skill.py) | **가장 단순한 시작점**. 시맨틱 함수(`preferences`)를 정의하여 자유 형식의 대화 문장에서 사용자의 선호도를 쉼표 구분 리스트로 추출 |
| 2 | [SK_semantic_memory_memory.py](SK_semantic_memory_memory.py) | SK의 **`VolatileMemoryStore`에 선호도 5건 저장** 후 자연어 질문으로 유사도 검색(`kernel.memory.search_async`). 메모리의 기본 CRUD/검색 동작 확인 |
| 3 | [SK_semantic_memory_prompt.py](SK_semantic_memory_prompt.py) | 프롬프트에 **`{{recall $변수}}` 구문**을 삽입하여, 챗봇이 응답할 때 사용자의 저장된 선호도를 자동 회상하도록 구성. 메모리 기반 대화의 핵심 패턴 |
| 4 | [SK_semantic_memory_preference_skill.py](SK_semantic_memory_preference_skill.py) | 위 (3)에 **선호도 자동 학습** 추가. 매 턴마다 `preferences` 시맨틱 함수로 새 선호도를 추출하여 메모리에 저장하고, 다음 턴부터 회상됨 |
| 5 | [SK_semantic_memory_context_skill.py](SK_semantic_memory_context_skill.py) | **질문 맥락 추출기**(`question_context`)를 추가. 사용자 입력에서 5개의 관련 질문을 동적으로 뽑아 `{{recall}}` 키워드로 사용 → 고정된 질문 템플릿 대신 **대화 맥락에 맞는 적응적 메모리 회상** |

## 실행 예시

```bash
# 트랙 1: TF-IDF 유사도 실습
python document_vector_database.py

# 트랙 1: ChromaDB + OpenAI Embedding
python document_query_chromadb.py

# 트랙 2: LangChain RAG 파이프라인 (HTML 다운로드 선행 필요)
python util_download_url.py
python langChain_load_splitting.py

# 트랙 3: SK 메모리 기반 챗봇
python SK_semantic_memory_prompt.py
```

## 핵심 개념 요약

- **TF-IDF vs Embedding**: TF-IDF는 단어 빈도 기반이라 의미 유사도(예: "하늘"과 "sky")를 잡지 못함. Embedding은 의미 공간에서 거리 계산이 가능
- **Chunking 전략**: 문자 단위(`RecursiveCharacterTextSplitter`) vs 토큰 단위(`from_tiktoken_encoder`). LLM 컨텍스트 제한에 맞춘 분할이 RAG 품질을 좌우
- **Contextual Compression**: 검색된 문서 전체를 LLM에 넘기지 않고, LLM 자체로 **질문 관련 문장만 추출**하여 토큰 비용/품질을 최적화
- **SK `{{recall}}`**: 프롬프트 렌더링 시점에 메모리에서 관련 정보를 자동 주입하는 선언적 메모리 인터페이스. RAG를 프롬프트 레벨에서 추상화한 형태

## 참고

- 일부 SK 예제는 구버전 API(`import_skill`, `create_semantic_function`, `add_chat_service`)를 사용합니다. 최신 `semantic-kernel` 버전에서는 API 명칭이 변경될 수 있습니다
- `VolatileMemoryStore`는 프로세스 종료 시 소실됩니다. 영속 저장이 필요하면 Chroma/Qdrant/Weaviate 커넥터로 교체하세요
- OpenAI Embedding API 호출에는 비용이 발생하므로 샘플 문서를 슬라이싱(예: `[100:350]`)하여 실습합니다
