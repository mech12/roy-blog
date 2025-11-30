#conda activate llm_env
#pip install openai


MYKEY="YOUR_OPENAI_API_KEY"

import openai
print(openai.__version__)



from openai import OpenAI
import json

# 클라이언트 초기화 (API 키는 환경 변수에서 자동 로드됨)
client = OpenAI(api_key=MYKEY)

def run_chat_example():
    """챗봇 대화 예제 실행"""
    print("--- 1. 챗봇 대화 예제 시작 ---")

    # 대화 기록 (History)을 저장할 리스트
    messages = [
        {"role": "system", "content": "당신은 친절하고 전문적인 과학 교육 전문가입니다. 답변은 항상 한국어로 해 주세요."},
        {"role": "user", "content": "태양이 빛나는 원리는 무엇인가요? 간단하게 설명해 주세요."}
    ]

    # 첫 번째 요청
    response1 = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages
    )

    # 응답 출력 및 대화 기록에 추가
    answer1 = response1.choices[0].message.content
    print(f"🤖 AI 응답 (1): {answer1}")
    messages.append({"role": "assistant", "content": answer1})

    # 맥락을 이어가는 두 번째 질문
    user_question2 = "그 에너지가 지구까지 오는 데 얼마나 걸리나요?"
    print(f"\n👤 사용자 질문 (2): {user_question2}")
    messages.append({"role": "user", "content": user_question2})

    # 두 번째 요청
    response2 = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages
    )

    # 응답 출력
    answer2 = response2.choices[0].message.content
    print(f"🤖 AI 응답 (2): {answer2}")
    print("--- 챗봇 대화 예제 종료 ---\n")

run_chat_example()