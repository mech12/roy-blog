from openai import OpenAI
from dotenv import load_dotenv


load_dotenv()  # loading and setting the api key can be done in one step
client = OpenAI()


# Example function to query ChatGPT
def ask_chatgpt(messages):
    response = client.chat.completions.create(
        model="gpt-4.1", # 사용할 모델 이름 (주의: 현재 gpt-4.1이라는 명칭은 공식적으로 없으며 gpt-4o 또는 gpt-4-turbo 등을 주로 씁니다)
        messages=messages,
        temperature=1,   # 창의성 조절 (0~2 사이, 0.7은 적당히 유연한 답변을 생성)
        response_format={"type": "json_object"}, # 응답을 반드시 JSON 객체 형태로 받도록 강제함
    )  
    
    return response.choices[0].message.content


#ai에게 기억력을 부여한다 
#AI 모델은 기본적으로 방금 자기가 한말을 기억하지 못한다 
#"system" : 이 범위내에서 대답하라 이런 규칙을 지켜라  
#"user": 실제적인 질문 
#"assistant": AI의 이전 답변 (문맥 유지용)
#예)
"""
1단계: "프랑스 수도가 어디야?" → "파리입니다."

2단계: "거기 맛집 알려줘." (이것만 보내면 AI는 '거기'가 어디인지 모릅니다.)

해결책: user(프랑스 수도?) + assistant(파리입니다) + user(거기 맛집?)를 세트로 묶어서 보내면 AI가 "아, 파리 맛집을 찾는구나!"라고 이해합니다.
예시를 통한 학습 (Few-shot Prompting)
"""
messages = [
    {"role": "system", "content": "당신은 유능한 어시스턴트 입니다. 응답은 반드시 JSON형태로 해주세요"}, # AI의 역할과 출력 형식 정의
    {"role": "user", "content": "프랑스의 수도는 어디인가요?"}, # 사용자의 첫 질문
    {"role": "assistant", "content": "프랑스의 수도는 파리입니다."}, # AI의 이전 답변 (문맥 유지용)
    {"role": "user", "content": "파리에 대해 재미있는 사실을 알려줘"} # 사용자의 새로운 질문
]

"""
system: AI의 페르소나나 제약 사항 설정.
user: 실제 사용자가 던지는 질문.
assistant: AI가 이전에 했던 답변. 이를 포함해야 AI가 앞선 대화 흐름을 이해합니다.
"""
response = ask_chatgpt(messages)
print(response)
