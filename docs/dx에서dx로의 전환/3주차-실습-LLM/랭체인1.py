


# ----------------------------------------------------
# ⭐️ 1. API 키 설정 (MyKey 변수를 직접 환경 변수에 설정) ⭐️
# getpass를 제거하고 코드가 바로 환경 변수를 사용하도록 수정했습니다.
MyKey = "YOUR_GEMINI_API_KEY" # 여기에 실제 키를 넣어 사용하세요.
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from getpass import getpass

# ⭐️ API 키 설정 (키를 직접 입력하거나 환경 변수에 설정)
if "GEMINI_API_KEY" not in os.environ:
    os.environ["GEMINI_API_KEY"] = MyKey  #getpass()

# 1. 모델 인스턴스 생성
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

# 2. 프롬프트 템플릿 정의
prompt = ChatPromptTemplate.from_messages([
    ("system", "당신은 사용자에게 친절하고 유머러스하게 답변하는 챗봇입니다."),
    ("user", "{input}")
])

# 3. LCEL 체인 구축: 프롬프트 | LLM | 파서
# 이 파이프라인이 LLMChain을 대체합니다.
basic_chain = prompt | llm | StrOutputParser()

# 4. 체인 실행
question = "인공지능이란 무엇인지 아주 짧게 설명해줘."
response = basic_chain.invoke({"input": question})

print("--- 기본 LLM 호출 결과 ---")
print(response)