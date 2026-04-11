import semantic_kernel as sk
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion, AzureChatCompletion

# 시맨틱 커널 초기화
kernel = sk.Kernel()

# .env 파일에서 OpenAI API 키 로드 및 서비스 등록
api_key, _ = sk.openai_settings_from_dot_env()
# gpt-4 모델을 사용하여 채팅 서비스 추가
kernel.add_chat_service("chat-gpt", OpenAIChatCompletion("gpt-4", api_key))

# Azure OpenAI를 사용할 경우 (대체 코드):
# deployment, api_key, endpoint = sk.azure_openai_settings_from_dot_env()
# kernel.add_chat_service("dv", AzureChatCompletion(deployment, endpoint, api_key))

# 프롬프트를 하나의 '시맨틱 함수'로 정의
# {{$input}}은 함수 호출 시 전달되는 입력값이 들어가는 자리입니다.
preferences = kernel.create_semantic_function("""
당신은 사용자의 선호도를 감지하는 전문가입니다.
대화 기록에서 사용자의 취향이나 선호도를 추출할 수 있습니다.
새로운 선호도를 쉼표로 구분된 문장 목록으로 추출하세요.
[입력 데이터]
{{$input}}
[입력 종료]
""")

# 정의한 시맨틱 함수 실행 및 결과 출력
result = preferences("""
나는 SF 영화를 좋아하지만, 고전 영화는 좋아하지 않아.
또한 판타지 테마의 TV 쇼도 즐겨 봐.
내가 가장 좋아하는 배우는 크리스 파인이야.
""")

print("[추출된 사용자 선호도 목록]")
print(result)