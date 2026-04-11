from dotenv import load_dotenv
import os
from langchain.document_loaders import UnstructuredHTMLLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chat_models import ChatOpenAI
from langchain.text_splitter import CharacterTextSplitter
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor

# .env 파일에서 API 키 로드
load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')

if not api_key:
    raise ValueError("API 키를 찾을 수 없습니다. .env 파일을 확인해주세요.")

# HTML 문서 로드 (샘플: 마더구스 동요집)
loader = UnstructuredHTMLLoader("sample_documents/mother_goose.html")
data = loader.load()

# 텍스트 분할 (Token 단위로 자르기)
text_splitter = CharacterTextSplitter.from_tiktoken_encoder(
    chunk_size=50, chunk_overlap=10, add_start_index=True
)
documents = text_splitter.split_documents(data)

# 문서 슬라이싱 (동요 내용이 있는 부분만 추출)
documents = [doc for doc in documents][8:94]

# Chroma 벡터 데이터베이스 생성
db = Chroma.from_documents(documents, OpenAIEmbeddings())

# 문맥 압축기(Compressor) 설정: 검색된 문서에서 질문과 관련된 핵심만 추출
llm = ChatOpenAI(temperature=0)
compressor = LLMChainExtractor.from_llm(llm)

# 압축 리트리버 구성
compression_retriever = ContextualCompressionRetriever(
    base_compressor=compressor, base_retriever=db.as_retriever()
)

def retrieve_documents(query, top_n=2):
    """압축된 형태의 관련 문서를 검색하여 반환합니다."""
    response = compression_retriever.get_relevant_documents(query=query)
    return response[:top_n]         

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

    search_results = retrieve_documents(query, top_n)
    
    print("\n[문맥 압축 검색 결과 - 핵심 요약본]")
    for i, doc in enumerate(search_results):
        print(f"문서 {i+1}: {doc.page_content}")

    print("-" * 50 + "\n")