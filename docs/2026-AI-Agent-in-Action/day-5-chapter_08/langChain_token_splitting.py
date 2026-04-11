from dotenv import load_dotenv
import os
from langchain.document_loaders import UnstructuredHTMLLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import CharacterTextSplitter

# .env 파일에서 API 키 로드
load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')

if not api_key:
    raise ValueError("API 키를 찾을 수 없습니다. .env 파일을 확인해주세요.")

# HTML 문서 로더 설정 (샘플: 마더구스 동요집)
loader = UnstructuredHTMLLoader("sample_documents/mother_goose.html")
data = loader.load()

# 텍스트 분할기 설정 (tiktoken 인코더 사용)
# chunk_size: 50토큰씩 자름, chunk_overlap: 문맥 유지를 위해 10토큰씩 중첩
text_splitter = CharacterTextSplitter.from_tiktoken_encoder(
    chunk_size=50, chunk_overlap=10
)

# 문서 분할 실행
documents = text_splitter.split_documents(data)

# 실제 동요 내용이 포함된 부분만 슬라이싱 (8번째부터 93번째 조각까지)
documents = [doc for doc in documents][8:94]

# Chroma 벡터 데이터베이스 생성 및 문서 임베딩 저장
# 내부적으로 OpenAI의 임베딩 모델을 사용하여 텍스트를 벡터로 변환합니다.
db = Chroma.from_documents(documents, OpenAIEmbeddings())

def query_documents(query, top_n=2):
    """사용자 질의에 대해 가장 유사한 문서를 검색합니다."""
    docs = db.similarity_search(query, k=top_n)    
    return docs         

# 사용자 검색 입력 루프
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

    search_results = query_documents(query, top_n)
    
    print("\n[가장 유사한 문서 검색 결과]")
    for i, doc in enumerate(search_results):
        print(f"문서 {i+1}: {doc.page_content}")

    print("-" * 50 + "\n")