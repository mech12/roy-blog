from openai import OpenAI
from dotenv import load_dotenv
import os
import chromadb
from langchain.document_loaders import UnstructuredHTMLLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

# .env 파일에서 API 키 로드
load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')

if not api_key:
    raise ValueError("API 키를 찾을 수 없습니다. .env 파일을 확인해주세요.")
client = OpenAI(api_key=api_key)

def get_embedding(text, model="text-embedding-3-small"):
    # 최신 임베딩 모델 사용 (성능/비용 효율적)
    text = text.replace("\n", " ")
    return client.embeddings.create(input=[text], model=model).data[0].embedding

# HTML 문서 로드 (샘플: 마더구스 동요집)
loader = UnstructuredHTMLLoader("sample_documents/mother_goose.html")
data = loader.load()

# 재귀적 캐릭터 텍스트 분할기 설정
# 문단, 문장, 단어 순으로 적절한 지점을 찾아 의미가 끊기지 않게 분할함
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=100,        # 각 조각(Chunk)의 최대 길이
    chunk_overlap=25,      # 조각 간의 중첩 길이 (문맥 유지용)
    length_function=len,
    add_start_index=True,
)
documents = text_splitter.split_documents(data)

# 문서 슬라이싱: 비용과 속도를 위해 일부 구간(250개 조각)만 사용
# page_content만 추출하여 리스트로 만듭니다.
document_contents = [doc.page_content for doc in documents][100:350]

# 각 조각에 대한 임베딩 생성
embeddings = [get_embedding(doc) for doc in document_contents]
ids = [f"id{i}" for i in range(len(document_contents))]

# ChromaDB 클라이언트 및 컬렉션 생성
chroma_client = chromadb.Client()
collection = chroma_client.create_collection(name="mother_goose_collection")

# 데이터베이스에 데이터 추가
collection.add(
    embeddings=embeddings,
    documents=document_contents,    
    ids=ids
)

def query_chromadb(query, top_n=2):
    """질의어에 대해 ChromaDB에서 가장 유사한 상위 결과들을 반환합니다."""    
    query_embedding = get_embedding(query)
    results = collection.query(
        query_embeddings=[query_embedding],    
        n_results=top_n
    )
    return [(id, score, text) for id, score, text in 
            zip(results['ids'][0], results['distances'][0], results['documents'][0])]

# 사용자 검색 루프
while True:
    query = input("검색어를 입력하세요 (종료하려면 'exit' 입력): ")
    if query.lower() == 'exit':
        print("프로그램을 종료합니다.")
        break
        
    try:
        top_n = int(input("상위 몇 개의 결과를 확인하시겠습니까? "))
    except ValueError:
        print("숫자를 입력해주세요.")
        continue

    search_results = query_chromadb(query, top_n)
    
    print("\n[가장 유사한 문서 검색 결과]")
    for id, score, text in search_results:
        # SCORE(거리)는 0에 가까울수록 더 유사한 문서입니다.
        print(f"ID: {id} | 점수: {round(score, 2)} | 내용: {text}")

    print("-" * 50 + "\n")