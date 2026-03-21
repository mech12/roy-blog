# Chapter 07: Streamlit 기반 ChatGPT 클론 만들기

## 개요

이 챕터에서는 Streamlit과 OpenAI API를 활용하여 ChatGPT와 유사한 대화형 챗봇 웹 애플리케이션을 구현한다. 동일한 기능을 **일반 응답 방식**과 **스트리밍 응답 방식** 두 가지로 구현하여, 각 방식의 차이점과 사용자 경험에 미치는 영향을 비교한다.

---

## 파일 설명

| 파일명 | 설명 |
|---|---|
| `.env.example` | 환경 변수 설정 예시 파일. OpenAI API 키, 조직 ID, Azure OpenAI 관련 설정값을 정의한다. |
| `chatgpt_clone_response.py` | 일반(비스트리밍) 응답 방식의 ChatGPT 클론. 전체 응답이 생성될 때까지 대기한 후 한 번에 화면에 표시한다. `st.spinner`를 사용하여 대기 중임을 사용자에게 알린다. |
| `chatgpt_clone_streaming.py` | 스트리밍 응답 방식의 ChatGPT 클론. `stream=True` 옵션과 `st.write_stream`을 사용하여 응답이 생성되는 즉시 토큰 단위로 화면에 출력한다. |

---

## 주요 개념

### 1. Streamlit 세션 상태 관리

`st.session_state`를 활용하여 대화 이력(`messages`)과 모델 설정(`openai_model`)을 유지한다. Streamlit은 사용자 상호작용마다 스크립트를 재실행하므로, 세션 상태를 통해 이전 대화 내용을 보존하는 것이 핵심이다.

### 2. OpenAI Chat Completions API

`client.chat.completions.create()` 메서드를 사용하여 GPT-4.1 모델과 대화한다. 메시지 히스토리 전체를 매 요청마다 전달하여 맥락을 유지하는 멀티턴 대화 구조를 구현한다.

### 3. 일반 응답 vs 스트리밍 응답

- **일반 응답** (`chatgpt_clone_response.py`): API 호출 후 전체 응답을 수신할 때까지 블로킹된다. `st.spinner`로 로딩 표시를 제공한다.
- **스트리밍 응답** (`chatgpt_clone_streaming.py`): `stream=True` 파라미터를 설정하여 토큰이 생성될 때마다 점진적으로 수신한다. `st.write_stream`이 스트림 객체를 직접 처리하여 실시간으로 텍스트를 표시한다.

### 4. 환경 변수를 통한 API 키 관리

`python-dotenv`의 `load_dotenv()`를 사용하여 `.env` 파일에서 API 키를 로드한다. OpenAI 직접 연결과 Azure OpenAI 연결 모두를 지원하는 구조이다.

### 5. Streamlit 채팅 UI 컴포넌트

- `st.chat_message()`: 역할(user/assistant)에 따라 구분된 채팅 말풍선을 표시한다.
- `st.chat_input()`: 사용자 입력을 받는 채팅 입력창을 제공한다.
- `st.markdown()`: 응답 텍스트를 마크다운 형식으로 렌더링한다.

---

## 학습 교훈

1. **스트리밍은 체감 성능을 크게 향상시킨다.** 실제 응답 완료 시간은 비슷하지만, 스트리밍 방식은 첫 토큰이 즉시 표시되므로 사용자가 느끼는 대기 시간이 현저히 줄어든다.

2. **세션 상태 관리는 Streamlit 챗봇의 핵심이다.** Streamlit의 재실행 모델 특성상, `st.session_state`를 올바르게 활용하지 않으면 대화 이력이 매 상호작용마다 초기화된다.

3. **전체 메시지 히스토리 전달이 맥락 유지의 열쇠이다.** OpenAI API는 상태를 유지하지 않으므로(stateless), 매 요청 시 이전 대화 내역을 모두 포함해야 연속적인 대화가 가능하다. 이는 토큰 사용량과 비용에 직접적인 영향을 미친다.

4. **API 키는 반드시 환경 변수로 관리해야 한다.** 소스 코드에 직접 하드코딩하면 보안 위험이 발생한다. `.env` 파일과 `.env.example` 패턴을 활용하여 민감 정보를 코드와 분리하는 것이 모범 사례이다.

5. **Streamlit의 채팅 전용 컴포넌트를 활용하면 최소한의 코드로 완성도 높은 채팅 UI를 구현할 수 있다.** `st.chat_message`, `st.chat_input`, `st.write_stream` 등의 고수준 API 덕분에 40줄 미만의 코드로 기능적인 챗봇을 만들 수 있다.
