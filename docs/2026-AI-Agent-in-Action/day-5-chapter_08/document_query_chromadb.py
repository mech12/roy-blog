from openai import OpenAI
from dotenv import load_dotenv
import os
import chromadb

# .env 파일에서 API 키 로드
load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')

if not api_key:
    raise ValueError("API 키를 찾을 수 없습니다. .env 파일을 확인해주세요.")

client = OpenAI(api_key=api_key)

def get_embedding(text, model="text-embedding-3-small"):
    # 최신 모델인 text-embedding-3-small 권장 (비용 저렴, 성능 우수)
    text = text.replace("\n", " ")
    return client.embeddings.create(input=[text], model=model).data[0].embedding

# 샘플 문서 (의미적 유사성을 테스트하기 좋은 문장들)
documents = [
    "하늘은 푸르고 정말 아름답습니다.",
    "이 푸르고 아름다운 하늘을 사랑해요!",
    "빠른 갈색 여우가 게으른 개를 뛰어넘습니다.",
    "왕의 아침 식사에는 소시지, 햄, 베이컨, 달걀, 토스트, 콩이 포함됩니다.",
    "나는 녹색 달걀과 햄, 소시지, 베이컨을 좋아합니다!",
    "갈색 여우는 빠르고 파란 개는 게으릅니다!",
    "오늘 하늘은 매우 푸르고 정말 아름답네요.",
    "개는 게으르지만 갈색 여우는 정말 빠릅니다!"
]

# 각 문서에 대한 임베딩 생성
embeddings = [get_embedding(doc) for doc in documents]
ids = [f"id{i}" for i in range(len(documents))]

# ChromaDB 클라이언트 및 컬렉션 생성
chroma_client = chromadb.Client()
collection = chroma_client.create_collection(name="my_documents")

# 데이터베이스에 임베딩과 문서 추가
collection.add(
    embeddings=embeddings,
    documents=documents,    
    ids=ids
)

def query_chromadb(query, top_n=2):
    """질의어에 대해 가장 유사한 상위 N개의 결과를 반환합니다."""    
    query_embedding = get_embedding(query)
    results = collection.query(
        query_embeddings=[query_embedding],    
        n_results=top_n
    )
    return [(id, score, text) for id, score, text in 
            zip(results['ids'][0], results['distances'][0], results['documents'][0])]

# 사용자 입력 루프
while True:
    query = input("검색어를 입력하세요 (종료하려면 'exit' 입력): ")
    if query.lower() == 'exit':
        break
        
    try:
        top_n = int(input("상위 몇 개의 결과를 확인하시겠습니까? "))
    except ValueError:
        print("숫자를 입력해주세요.")
        continue

    search_results = query_chromadb(query, top_n)
    
    print("\n[가장 유사한 문서 검색 결과]")
    for id, score, text in search_results:
        # DISTANCE(거리)가 0에 가까울수록 유사도가 높음
        print(f"ID: {id} | 점수(거리): {round(score, 2)} | 내용: {text}")

    print("-" * 50 + "\n")