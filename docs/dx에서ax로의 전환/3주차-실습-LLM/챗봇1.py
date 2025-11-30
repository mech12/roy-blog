import os
from google import genai
from google.genai import types

# ⭐️ 환경 변수에서 API 키를 가져오거나 여기에 직접 설정해야 합니다.
# 예: os.environ.get("GEMINI_API_KEY")
# 유효한 키가 없다면 실행되지 않습니다.
# --- 설정 (실제 API 키로 대체) ---
MyKey = "YOUR_GEMINI_API_KEY"
MODEL_NAME = 'gemini-2.5-flash'
# ------------------------------

try:
    client = genai.Client(api_key=MyKey)
except Exception as e:
    print(f"클라이언트 초기화 오류: {e}")
    # 예제 실행을 위해 임시로 client를 None으로 설정 (실제 API 호출은 실패함)
    client = None 

# 챗봇을 위한 시스템 지침
SYSTEM_INSTRUCTION = (
    "당신은 친절하고 유머러스한 한국어 챗봇입니다. "
    "사용자의 질문에 대해 간결하고 명확하게 답변해 주세요."
)

def run_chatbot_session():
    if not client:
        print("\n[SKIP] 클라이언트 초기화 실패로 챗봇을 시작할 수 없습니다. API 키를 확인해 주세요.")
        return
    
    # 1. 챗 세션 생성
    # ⭐️ system_instruction을 통해 챗봇의 성격과 역할을 정의합니다.
    chat = client.chats.create(
        model='gemini-2.5-flash',
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION
        )
    )

    print("="*50)
    print("🤖 챗봇 시작: 친절한 Gemini 챗봇입니다. '종료'를 입력하면 대화가 끝납니다.")
    print("="*50)

    # 2. 무한 루프를 돌며 사용자 입력 대기
    while True:
        try:
            user_input = input("👤 나: ")
            
            if user_input.lower() == '종료':
                print("🤖 챗봇: 대화를 종료합니다. 다음에 또 만나요!")
                break

            if not user_input.strip():
                continue

            # 3. 메시지 전송 및 응답 받기
            response = chat.send_message(user_input)

            # 4. 응답 출력
            print(f"🤖 챗봇: {response.text}")

        except Exception as e:
            print(f"\n[오류 발생]: {e}")
            break

# 5. 대화 기록 출력 함수 (옵션)
def print_history(chat):
    print("\n--- 대화 기록(History) ---")
    for message in chat.get_history():
        role = message.role
        text = message.parts[0].text
        print(f"[{role.upper()}]: {text}")

# 챗봇 세션 실행
if __name__ == '__main__':
    run_chatbot_session()
    # 세션 종료 후 대화 기록을 보고 싶다면, run_chatbot_session 함수 내에서 chat 객체를 반환하도록 수정해야 합니다.
    # 예시 실행에서는 생략합니다.