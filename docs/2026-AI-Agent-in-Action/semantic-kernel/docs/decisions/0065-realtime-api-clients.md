---
# 이것들은 선택적 요소입니다. 필요 없는 항목은 자유롭게 제거하세요.
status:  proposed 
contact:  eavanvalkenburg
date:  2025-01-31 
deciders:  eavanvalkenburg, markwallace, alliscode, sphenry
consulted:  westey-m, rbarreto, alliscode, markwallace, sergeymenshykh, moonbox3
informed: taochenosu, dmytrostruk
---

# 멀티모달 실시간 API 클라이언트

## 맥락과 문제 설명

여러 모델 공급자가 실시간 음성 대 음성 또는 심지어 멀티모달, 실시간, 양방향 통신을 모델과 함께 가능하게 하기 시작했습니다. 여기에는 OpenAI의 [Realtime API][openai-realtime-api]와 [Google Gemini][google-gemini]가 포함됩니다. 이러한 API는 LLM을 다양한 시나리오에 사용하는 매우 흥미로운 새로운 방법을 약속하며, 우리는 이를 Semantic Kernel로 가능하게 하고자 합니다.

Semantic Kernel이 이 시스템에 가져오는 핵심 기능은 Semantic Kernel 함수를 이러한 API의 도구로 (재)사용할 수 있는 능력입니다. Google의 경우 비디오와 이미지를 입력으로 사용하는 옵션도 있으며, 이는 처음에 구현되지 않을 가능성이 높지만 추상화는 이를 처리할 수 있어야 합니다.

> [!IMPORTANT] 
> OpenAI와 Google 실시간 API 모두 프리뷰/베타 상태이므로, 향후 작동 방식에 호환성을 깨는 변경이 있을 수 있습니다. 따라서 이러한 API를 지원하기 위해 구축된 클라이언트는 API가 안정화될 때까지 실험적으로 유지됩니다.

현재 이러한 API가 사용하는 프로토콜은 웹소켓과 WebRTC입니다.

두 경우 모두 서비스와 이벤트가 송수신되며, 일부 이벤트는 콘텐츠(텍스트, 오디오 또는 비디오(현재까지는 보내기만, 받기 안 됨))를 포함하고, 일부 이벤트는 콘텐츠 생성, 함수 호출 요청 등과 같은 "제어" 이벤트입니다. 보내기 이벤트에는 콘텐츠 보내기(음성, 텍스트 또는 함수 호출 출력) 또는 이벤트(입력 오디오 커밋 및 응답 요청 등)가 포함됩니다.

### 웹소켓
웹소켓은 오랫동안 존재해온 잘 알려진 기술로, 단일 장기 연결을 통한 전이중 통신 프로토콜입니다. 실시간으로 클라이언트와 서버 간에 메시지를 보내고 받는 데 사용됩니다. 각 이벤트는 메시지를 포함할 수 있으며, 콘텐츠 항목이나 제어 이벤트를 포함할 수 있습니다. 오디오는 이벤트 내에서 base64 인코딩된 문자열로 전송됩니다.

### WebRTC
WebRTC는 간단한 API를 통해 웹 브라우저와 모바일 애플리케이션에 실시간 통신을 제공하는 Mozilla 프로젝트입니다. 직접적인 피어 투 피어 통신을 허용하여 플러그인 설치나 네이티브 앱 다운로드 없이 웹 페이지와 기타 애플리케이션 내에서 오디오 및 비디오 통신이 작동하게 합니다. 웹소켓과의 큰 차이점은 오디오와 비디오를 위한 채널과 "데이터"를 위한 별도 채널을 명시적으로 생성한다는 것입니다. 이 공간에서 데이터는 비AV 콘텐츠, 텍스트, 함수 호출, 함수 결과 및 오류나 확인과 같은 제어 이벤트를 포함하는 이벤트입니다.


### 이벤트 타입 (웹소켓 및 부분적으로 WebRTC)

#### 클라이언트 측 이벤트:
| **콘텐츠/제어 이벤트** | **이벤트 설명** | **OpenAI 이벤트** | **Google 이벤트** |
| ------------------------- | --------------------------------- | ---------------------------- | ---------------------------------- |
| 제어 | 세션 구성 | `session.update` | `BidiGenerateContentSetup` |
| 콘텐츠 | 음성 입력 전송 | `input_audio_buffer.append` | `BidiGenerateContentRealtimeInput` |
| 제어 | 입력 커밋 및 응답 요청 | `input_audio_buffer.commit` | `-` |
| 제어 | 오디오 입력 버퍼 비우기 | `input_audio_buffer.clear` | `-` |
| 콘텐츠 | 텍스트 입력 전송 | `conversation.item.create` | `BidiGenerateContentClientContent` |
| 제어 | 오디오 중단 | `conversation.item.truncate` | `-` |
| 제어 | 콘텐츠 삭제 | `conversation.item.delete` | `-` |
| 제어 | 함수 호출 요청에 응답 | `conversation.item.create` | `BidiGenerateContentToolResponse` |
| 제어 | 응답 요청 | `response.create` | `-` |
| 제어 | 응답 취소 | `response.cancel` | `-` |

#### 서버 측 이벤트:
| **콘텐츠/제어 이벤트** | **이벤트 설명** | **OpenAI 이벤트** | **Google 이벤트** |
| ------------------------- | -------------------------------------- | ------------------------------------------------------- | ----------------------------------------- |
| 제어 | 오류 | `error` | `-` |
| 제어 | 세션 생성됨 | `session.created` | `BidiGenerateContentSetupComplete` |
| 제어 | 세션 업데이트됨 | `session.updated` | `BidiGenerateContentSetupComplete` |
| 제어 | 대화 생성됨 | `conversation.created` | `-` |
| 제어 | 입력 오디오 버퍼 커밋됨 | `input_audio_buffer.committed` | `-` |
| 제어 | 입력 오디오 버퍼 비워짐 | `input_audio_buffer.cleared` | `-` |
| 제어 | 입력 오디오 버퍼 음성 시작됨 | `input_audio_buffer.speech_started` | `-` |
| 제어 | 입력 오디오 버퍼 음성 중지됨 | `input_audio_buffer.speech_stopped` | `-` |
| 콘텐츠 | 대화 항목 생성됨 | `conversation.item.created` | `-` |
| 콘텐츠 | 입력 오디오 전사 완료됨 | `conversation.item.input_audio_transcription.completed` | |
| 콘텐츠 | 입력 오디오 전사 실패함 | `conversation.item.input_audio_transcription.failed` | |
| 제어 | 대화 항목 잘림 | `conversation.item.truncated` | `-` |
| 제어 | 대화 항목 삭제됨 | `conversation.item.deleted` | `-` |
| 제어 | 응답 생성됨 | `response.created` | `-` |
| 제어 | 응답 완료됨 | `response.done` | `-` |
| 콘텐츠 | 응답 출력 항목 추가됨 | `response.output_item.added` | `-` |
| 콘텐츠 | 응답 출력 항목 완료됨 | `response.output_item.done` | `-` |
| 콘텐츠 | 응답 콘텐츠 부분 추가됨 | `response.content_part.added` | `-` |
| 콘텐츠 | 응답 콘텐츠 부분 완료됨 | `response.content_part.done` | `-` |
| 콘텐츠 | 응답 텍스트 델타 | `response.text.delta` | `BidiGenerateContentServerContent` |
| 콘텐츠 | 응답 텍스트 완료됨 | `response.text.done` | `-` |
| 콘텐츠 | 응답 오디오 전사 델타 | `response.audio_transcript.delta` | `BidiGenerateContentServerContent` |
| 콘텐츠 | 응답 오디오 전사 완료됨 | `response.audio_transcript.done` | `-` |
| 콘텐츠 | 응답 오디오 델타 | `response.audio.delta` | `BidiGenerateContentServerContent` |
| 콘텐츠 | 응답 오디오 완료됨 | `response.audio.done` | `-` |
| 콘텐츠 | 응답 함수 호출 인수 델타 | `response.function_call_arguments.delta` | `BidiGenerateContentToolCall` |
| 콘텐츠 | 응답 함수 호출 인수 완료됨 | `response.function_call_arguments.done` | `-` |
| 제어 | 함수 호출 취소됨 | `-` | `BidiGenerateContentToolCallCancellation` |
| 제어 | 속도 제한 업데이트됨 | `rate_limits.updated` | `-` |


## 전체 결정 동인
- 기저 프로토콜을 추상화하여, 개발자가 모델이나 프로토콜을 변경할 때 클라이언트 코드를 변경하지 않고도 원하는 프로토콜을 지원하는 애플리케이션을 구축할 수 있도록 합니다.
  - WebRTC는 웹소켓과 다른 정보를 세션 생성 시 필요로 하는 등 일부 제한이 예상됩니다.
- 향후 실시간 API와 기존 API의 발전을 처리할 수 있는 간단한 프로그래밍 모델.
- 가능한 한 수신 콘텐츠를 Semantic Kernel 콘텐츠로 변환하되, 모든 것을 노출하여 개발자와 향후를 위해 확장 가능하게 합니다.

결정해야 할 여러 영역이 있습니다:
- 콘텐츠와 이벤트
- 프로그래밍 모델
- 오디오 스피커/마이크 처리
- 인터페이스 설계 및 이름 지정

# 콘텐츠와 이벤트

## 검토한 옵션 - 콘텐츠와 이벤트
이러한 통합의 보내기 및 받기 측면 모두 이벤트를 어떻게 처리할지 결정해야 합니다.

1. 콘텐츠를 제어와 별도로 처리
1. 모든 것을 콘텐츠 항목으로 처리
1. 모든 것을 이벤트로 처리

### 1. 콘텐츠를 제어와 별도로 처리
이는 클라이언트에 두 가지 메커니즘이 있음을 의미합니다. 하나는 콘텐츠를, 하나는 제어 이벤트를 처리합니다.

- 장점:
    - 알려진 콘텐츠에 대한 강타입 응답
    - 주요 상호작용이 익숙한 SK 콘텐츠 타입으로 명확하여 사용하기 쉽고, 나머지는 별도 메커니즘을 통해 처리
- 단점:
    - 새 콘텐츠 지원은 코드베이스 업데이트가 필요하며 호환성을 깨는 것으로 간주될 수 있음(잠재적으로 추가 타입을 반환)
    - 두 데이터 스트림을 처리하는 추가 복잡성
    - 함수 호출과 같은 일부 항목은 콘텐츠와 제어 모두로 간주될 수 있음 - 자동 함수 호출 시 제어, 개발자가 직접 처리하려 할 때 콘텐츠

### 2. 모든 것을 콘텐츠 항목으로 처리
이는 모든 이벤트가 Semantic Kernel 콘텐츠 항목으로 변환됨을 의미하며, 제어 이벤트를 위한 추가 콘텐츠 타입을 정의해야 합니다.

- 장점:
  - 모든 것이 콘텐츠 항목이므로 처리하기 쉬움
- 단점:
  - 제어 이벤트를 위한 새로운 콘텐츠 타입이 필요

### 3. 모든 것을 이벤트로 처리
이는 이벤트를 도입하는 것입니다. 각 이벤트에는 타입이 있으며, 위의 핵심 콘텐츠 타입(오디오, 비디오, 이미지, 텍스트, 함수 호출 또는 함수 응답)일 수 있고, 콘텐츠가 없는 제어 이벤트를 위한 일반 이벤트도 있습니다. 각 이벤트에는 위의 SK 타입과 서비스의 이벤트 타입을 포함하는 service_event_type 필드가 있습니다. 마지막으로 이벤트에는 타입에 해당하는 콘텐츠 필드가 있으며, 일반 이벤트의 경우 서비스의 원시 이벤트를 포함합니다.

- 장점:
  - 서비스 이벤트에 대한 변환이 필요 없음
  - 유지보수 및 확장이 쉬움
- 단점:
  - 새로운 개념 도입
  - SK 타입이 있는 콘텐츠와 없는 콘텐츠가 혼재되어 혼란스러울 수 있음

## 결정 결과 - 콘텐츠와 이벤트

선택한 옵션: 3 모든 것을 이벤트로 처리

이 옵션은 원시 이벤트에서의 추상화를 허용하면서도 개발자가 필요한 경우 원시 이벤트에 접근할 수 있도록 하기 위해 선택되었습니다.
`RealtimeEvent`라는 기본 이벤트 타입이 추가되며, `event_type`, `service_event_type`, `service_event` 세 가지 필드를 가집니다. 그런 다음 오디오, 텍스트, 함수 호출, 함수 결과 각각에 대한 네 가지 하위 클래스가 있습니다.

알려진 콘텐츠가 수신되면, SK 콘텐츠 타입으로 파싱되어 추가됩니다. 이 콘텐츠는 inner_content에도 원시 이벤트를 가져야 하므로, 이벤트가 이벤트와 콘텐츠에 두 번 저장됩니다. 이는 설계에 의한 것으로, 개발자가 이벤트 레이어를 제거하더라도 원시 이벤트에 쉽게 접근할 수 있도록 합니다.

서비스의 단일 이벤트가 여러 콘텐츠 항목을 포함할 수도 있습니다. 예를 들어 응답에 텍스트와 오디오가 모두 포함될 수 있으며, 이 경우 여러 이벤트가 발생합니다. 원칙적으로 이벤트는 한 번 처리되어야 하므로, 파싱 가능한 이벤트가 있으면 하위 타입만 반환됩니다. `RealtimeEvent`와 동일한 정보를 모두 가지고 있으므로, 개발자가 추상화된 타입을 사용하고 싶지 않은 경우 service_event_type과 service_event에서 직접 트리거할 수 있습니다.

```python
RealtimeEvent(
  event_type="service", # 쉬운 구분을 위한 단일 기본값
  service_event_type="conversation.item.create", # 선택사항
  service_event: { ... } # 선택사항, 일부 이벤트에는 콘텐츠가 없기 때문.
)
```

```python
RealtimeAudioEvent(RealtimeEvent)(
  event_type="audio", # 쉬운 구분을 위한 단일 기본값
  service_event_type="response.audio.delta", # 선택사항
  service_event: { ... } 
  audio: AudioContent(...)
)
```

```python
RealtimeTextEvent(RealtimeEvent)(
  event_type="text", # 쉬운 구분을 위한 단일 기본값
  service_event_type="response.text.delta", # 선택사항
  service_event: { ... } 
  text: TextContent(...)
)
```

```python
RealtimeFunctionCallEvent(RealtimeEvent)(
  event_type="function_call", # 쉬운 구분을 위한 단일 기본값
  service_event_type="response.function_call_arguments.delta", # 선택사항
  service_event: { ... } 
  function_call: FunctionCallContent(...)
)
```

```python
RealtimeFunctionResultEvent(RealtimeEvent)(
  event_type="function_result", # 쉬운 구분을 위한 단일 기본값
  service_event_type="response.output_item.added", # 선택사항
  service_event: { ... } 
  function_result: FunctionResultContent(...)
)
```

```python
RealtimeImageEvent(RealtimeEvent)(
  event_type="image", # 쉬운 구분을 위한 단일 기본값
  service_event_type="response.image.delta", # 선택사항
  service_event: { ... } 
  image: ImageContent(...)
)
```

이를 통해 event_type에 대한 패턴 매칭을 쉽게 하거나, 서비스 이벤트의 특정 이벤트 타입을 필터링하기 위해 service_event_type을 사용하거나, 이벤트 타입에 매칭하여 SK 콘텐츠를 가져올 수 있습니다.

어느 시점에서 오류나 세션 업데이트와 같은 다른 추상화된 타입이 필요할 수 있지만, 현재 두 서비스가 이러한 이벤트의 존재와 구조에 대해 합의하지 않았으므로, 필요할 때까지 기다리는 것이 좋습니다.

### 거부된 아이디어

#### ID 처리
관련 조각을 추적하기 위해 이러한 타입에 추가 필드를 포함할지 여부가 미해결 사항이지만, ID가 생성되는 방식이 서비스마다 다르고 상당히 복잡하여 문제가 됩니다. 예를 들어 OpenAI API는 다음 ID와 함께 오디오 전사 조각을 반환합니다:
- `event_id`: 이벤트의 고유 ID
- `response_id`: 응답의 ID
- `item_id`: 항목의 ID
- `output_index`: 응답에서 출력 항목의 인덱스
- `content_index`: 항목의 콘텐츠 배열에서 콘텐츠 부분의 인덱스

OpenAI에서 발생하는 이벤트의 예시는 아래 [세부사항](#background-info)을 참조하세요.

Google은 함수 호출과 같은 일부 콘텐츠 항목에만 ID가 있고, 오디오나 텍스트 콘텐츠에는 없습니다.

ID는 항상 원시 이벤트(inner_content 또는 .event)를 통해 사용 가능하므로, 콘텐츠 타입에 추가할 필요가 없으며, 콘텐츠 타입을 더 복잡하게 만들고 서비스 간 재사용을 어렵게 만듭니다.

#### 콘텐츠를 (Streaming)ChatMessageContent로 감싸기
콘텐츠를 먼저 `(Streaming)ChatMessageContent`로 감싸면, 또 다른 복잡성 레이어가 추가되고 CMC가 여러 항목을 포함할 수 있으므로, 오디오에 접근하려면 `service_event.content.items[0].audio.data`처럼 보이게 되며, 이는 `service_event.audio.data`만큼 명확하지 않습니다.

# 프로그래밍 모델

## 검토한 옵션 - 프로그래밍 모델
클라이언트의 프로그래밍 모델은 간단하고 사용하기 쉬워야 하면서도 실시간 API의 복잡성을 처리할 수 있어야 합니다.

_이 섹션에서는 이전 섹션에서 내린 결정과 관계없이 콘텐츠와 이벤트 모두에 대해 이벤트라고 합니다._

이는 주로 받기 측면에 관한 것이며, 보내기는 훨씬 간단합니다.

1. 이벤트 핸들러, 개발자가 특정 이벤트에 대한 핸들러를 등록하고 이벤트가 수신될 때 클라이언트가 이 핸들러를 호출
   - 1a: 단일 이벤트 핸들러, 각 이벤트가 핸들러에 전달
   - 1b: 다중 이벤트 핸들러, 각 이벤트 타입이 자체 핸들러를 가짐
2. 개발자에게 노출되는 이벤트 버퍼/큐, 보내기 시작 및 받기 시작 메서드, 이벤트의 보내기와 받기를 시작하여 버퍼를 채움
3. 이벤트를 yield하는 AsyncGenerator

### 1. 이벤트 핸들러
이벤트 핸들러를 등록하는 메커니즘이 있고, 이벤트가 수신되면 통합이 이 핸들러를 호출합니다. 이벤트를 보내기 위해 서비스에 이벤트를 보내는 함수가 생성됩니다.

- 장점:
  - async generator와 같은 복잡한 것을 처리할 필요가 없고 어떤 이벤트에 응답할지 추적하기 쉬움
- 단점:
  - 번거로울 수 있으며, 1b의 경우 새 이벤트를 지원하기 위해 업데이트가 필요
  - 순서(어떤 이벤트 핸들러가 먼저 호출되는지)가 개발자에게 불명확

### 2. 이벤트 버퍼/큐
보내기와 받기를 위한 두 개의 큐가 있고, 개발자는 받기 큐를 수신하고 보내기 큐에 전송할 수 있습니다. 이벤트를 콘텐츠 타입으로 파싱하고 자동 함수 호출과 같은 내부 작업이 먼저 처리되고, 결과가 큐에 넣어집니다. 콘텐츠 타입은 전체 이벤트를 캡처하기 위해 inner_content를 사용해야 하며, 보내기 큐에 메시지를 추가할 수도 있습니다.

- 장점:
  - 간단하게 사용, 보내기 시작 및 받기 시작만 하면 됨
  - 큐는 잘 알려진 개념이므로 이해하기 쉬움
  - 개발자가 관심 없는 이벤트를 건너뛸 수 있음
- 단점:
  - 큐잉 메커니즘으로 인해 잠재적으로 오디오 지연 발생

### 2b. 옵션 2와 동일하지만 오디오 콘텐츠 우선 처리
오디오 콘텐츠가 먼저 처리되어 개발자가 가능한 빨리 재생하거나 전달할 수 있도록 콜백으로 직접 전송되고, 그런 다음 다른 모든 이벤트(텍스트, 함수 호출 등)가 처리되어 큐에 넣어집니다.

- 장점:
  - 오디오 지연 완화
  - 큐는 잘 알려진 개념이므로 이해하기 쉬움
  - 개발자가 관심 없는 이벤트를 건너뛸 수 있음
- 단점:
  - 오디오 콘텐츠와 이벤트에 두 가지 별도 메커니즘 사용

### 3. 이벤트를 yield하는 AsyncGenerator
클라이언트가 이벤트를 yield하는 함수를 구현하고, 개발자가 이를 순회하며 이벤트가 오는 대로 처리합니다.

- 장점:
  - 이벤트를 순회하기만 하면 되어 사용하기 쉬움
  - async generator는 잘 알려진 개념이므로 이해하기 쉬움
  - 개발자가 관심 없는 이벤트를 건너뛸 수 있음
- 단점:
  - 제너레이터의 비동기 특성으로 인해 잠재적으로 오디오 지연 발생
  - 많은 이벤트 타입은 이를 모두 처리하기 위한 큰 단일 코드 세트를 의미

### 3b. 옵션 3과 동일하지만 오디오 콘텐츠 우선 처리
오디오 콘텐츠가 먼저 처리되어 개발자가 가능한 빨리 재생하거나 전달할 수 있도록 콜백으로 직접 전송되고, 그런 다음 다른 모든 이벤트가 파싱되어 yield됩니다.

- 장점:
  - 오디오 지연 완화
  - async generator는 잘 알려진 개념이므로 이해하기 쉬움
- 단점:
  - 오디오 콘텐츠와 이벤트에 두 가지 별도 메커니즘 사용
  
## 결정 결과 - 프로그래밍 모델

선택한 옵션: 3b 콜백을 통한 오디오 콘텐츠 우선 처리와 결합된 이벤트를 yield하는 AsyncGenerator

이는 프로그래밍 모델을 매우 쉽게 만들며, 모든 서비스와 프로토콜에서 작동해야 하는 최소 설정은 다음과 같습니다:
```python
async for event in realtime_client.start_streaming():
    match event:
        case AudioEvent():
            await audio_player.add_audio(event.audio)
        case TextEvent():
            print(event.text.text)
```

# 오디오 스피커/마이크 처리

## 검토한 옵션 - 오디오 스피커/마이크 처리

1. 오디오를 녹음하고 재생하기 위해 실시간 클라이언트에 전달할 수 있는 오디오 핸들러에 대한 추상화를 SK에서 생성
2. 클라이언트에 AudioContent를 보내고 받으며, 클라이언트가 오디오 녹음과 재생을 처리하도록 함

### 1. 오디오 핸들러에 대한 추상화를 SK에서 생성
클라이언트가 오디오 핸들러를 등록하는 메커니즘이 있고, 오디오가 수신되거나 전송되어야 할 때 통합이 이 핸들러를 호출합니다. 이를 위해 Semantic Kernel에서 추가 추상화를 생성해야 합니다(또는 표준에서 가져옴).

- 장점:
  - 간단한/로컬 오디오 핸들러를 SK와 함께 출시하여 사용하기 쉽게 만들 수 있음
  - 제3자가 다른 시스템(예: Azure Communications Service)에 통합하기 위해 확장 가능
  - 오디오 콘텐츠가 핸들러에 우선적으로 전송되어 버퍼 문제를 완화할 수 있음
- 단점:
  - SK에 유지보수가 필요한 추가 코드가 있으며, 잠재적으로 제3자 코드에 의존
  - 오디오 드라이버가 플랫폼별일 수 있어 모든 플랫폼에서 잘 작동하지 않거나 전혀 작동하지 않을 수 있음

### 2. AudioContent를 보내고 받으며 클라이언트가 처리
클라이언트가 AudioContent 항목을 수신하고, 녹음과 재생을 포함하여 직접 처리해야 합니다.

- 장점:
  - SK에 유지보수가 필요한 추가 코드가 없음
- 단점:
  - 개발자에게 오디오 처리에 대한 추가 부담
  - 시작하기 어려움

## 결정 결과 - 오디오 스피커/마이크 처리

선택한 옵션: 옵션 2: 오디오 형식, 프레임 지속시간, 샘플 레이트 및 기타 오디오 설정에 큰 차이가 있어 *항상* 작동하는 기본값은 실현 불가능하며, 개발자가 어쨌든 이를 처리해야 하므로 처음부터 처리하게 하는 것이 좋습니다. 사람들이 쉽게 시작할 수 있도록 샘플에 샘플 오디오 핸들러를 추가할 것입니다.

# 인터페이스 설계

다음 기능을 지원해야 합니다:
- 세션 생성
- 세션 업데이트
- 세션 종료
- 이벤트 수신/대기
- 이벤트 전송

## 검토한 옵션 - 인터페이스 설계

1. 모든 것에 단일 클래스 사용
2. 서비스 클래스와 세션 클래스 분리

### 1. 모든 것에 단일 클래스 사용

각 구현은 위의 모든 메서드를 구현해야 합니다. 이는 프로토콜별이 아닌 요소가 프로토콜별 요소와 같은 클래스에 있게 되어 코드 중복을 초래합니다.

### 2. 서비스 클래스와 세션 클래스 분리

두 개의 인터페이스가 생성됩니다:
- 서비스: 세션 생성, 세션 업데이트, 세션 삭제, 세션 목록 조회?
- 세션: 이벤트 수신/대기, 이벤트 전송, 세션 업데이트, 세션 종료

현재 Google이나 OpenAI API 모두 세션 재시작을 지원하지 않으므로, 분리의 장점은 주로 구현 문제이며 개발자에게 어떤 이점도 추가하지 않습니다. 이는 결과적인 분리가 실제로 훨씬 간단해짐을 의미합니다:
- 서비스: 세션 생성
- 세션: 이벤트 수신/대기, 이벤트 전송, 세션 업데이트, 세션 종료

## 이름 지정

보내기 및 수신/대기 메서드는 이름이 명확해야 하며, 이러한 API를 다룰 때 혼란스러워질 수 있습니다. 다음 옵션을 검토했습니다:

이벤트를 코드에서 서비스로 보내는 옵션:
- Google은 클라이언트에서 .send를 사용합니다.
- OpenAI도 클라이언트에서 .send를 사용합니다
- send 또는 send_message가 Azure Communication Services와 같은 다른 클라이언트에서 사용됩니다

코드에서 서비스의 이벤트를 수신하는 옵션:
- Google은 클라이언트에서 .receive를 사용합니다.
- OpenAI는 클라이언트에서 .recv를 사용합니다.
- 다른 클라이언트에서는 receive 또는 receive_messages를 사용합니다.

### 결정 결과 - 인터페이스 설계

선택한 옵션: 모든 것에 단일 클래스 사용
send와 receive를 동사로 선택.

이는 인터페이스가 다음과 같이 보일 것임을 의미합니다:
```python

class RealtimeClient:
    async def create_session(self, chat_history: ChatHistory, settings: PromptExecutionSettings, **kwargs) -> None:
        ...

    async def update_session(self, chat_history: ChatHistory, settings: PromptExecutionSettings, **kwargs) -> None:
        ...

    async def close_session(self, **kwargs) -> None:
        ...

    async def receive(self, chat_history: ChatHistory, **kwargs) -> AsyncGenerator[RealtimeEvent, None]:
        ...

    async def send(self, event: RealtimeEvent) -> None:
        ...
```

대부분의 경우, `create_session`은 동일한 매개변수로 `update_session`을 호출해야 합니다. update session은 나중에 동일한 입력으로 별도로 수행할 수도 있기 때문입니다.

Python의 경우, `async with` 문에서 사용할 수 있도록 기본 `__aenter__` 및 `__aexit__` 메서드가 클래스에 추가되어야 하며, 각각 create_session과 close_session을 호출합니다.

세션이 설정되기 전에 이벤트가 손실되거나 예외가 발생하지 않도록 버퍼/큐를 통해 send 메서드를 구현하는 것이 권장됩니다(필수는 아님). 세션 생성에 몇 초가 걸릴 수 있으며 그 시간 동안 단일 send 호출은 애플리케이션을 차단하거나 예외를 발생시킵니다.

send 메서드는 모든 이벤트 타입을 처리해야 하지만, 동일한 것을 두 가지 방법으로 처리해야 할 수 있습니다. 예를 들어(OpenAI API의 경우):
```python
audio = AudioContent(...)

await client.send(AudioEvent(audio=audio))
```

는 다음과 동등해야 합니다:
```python
audio = AudioContent(...)

await client.send(ServiceEvent(service_event_type='input_audio_buffer.append', service_event=audio))
```

첫 번째 버전은 모든 서비스에 대해 정확히 동일한 코드를 가질 수 있게 하고, 두 번째 버전도 올바르며 올바르게 처리되어야 합니다. 이는 유연성과 단순성을 다시 허용합니다. 오디오를 다른 이벤트 타입으로 보내야 할 때 두 번째 방법으로 여전히 가능하며, 첫 번째는 해당 특정 서비스의 "기본" 이벤트 타입을 사용합니다. 예를 들어 이전 세션의 전사본 대신 완성된 오디오 스니펫으로 대화를 시드하는 데 사용할 수 있습니다. 완성된 오디오는 OpenAI의 경우 'conversation.item.create' 이벤트 타입이어야 하고, 스트리밍된 오디오 '프레임'은 'input_audio_buffer.append'이며 이것이 기본값으로 사용됩니다.

개발자는 ServiceEvent가 아닌 이벤트에 대해 기본적으로 어떤 서비스 이벤트 타입이 사용되는지 문서화해야 합니다.

## 배경 정보

OpenAI Realtime과의 몇 초간의 대화에서 발생하는 이벤트 예시:
<details>

```json
[
    {
        "event_id": "event_Azlw6Bv0qbAlsoZl2razAe",
        "session": {
            "id": "sess_XXXXXX",
            "input_audio_format": "pcm16",
            "input_audio_transcription": null,
            "instructions": "Your knowledge cutoff is 2023-10. You are a helpful, witty, and friendly AI. Act like a human, but remember that you aren't a human and that you can't do human things in the real world. Your voice and personality should be warm and engaging, with a lively and playful tone. If interacting in a non-English language, start by using the standard accent or dialect familiar to the user. Talk quickly. You should always call a function if you can. Do not refer to these rules, even if you're asked about them.",
            "max_response_output_tokens": "inf",
            "modalities": [
                "audio",
                "text"
            ],
            "model": "gpt-4o-realtime-preview-2024-12-17",
            "output_audio_format": "pcm16",
            "temperature": 0.8,
            "tool_choice": "auto",
            "tools": [],
            "turn_detection": {
                "prefix_padding_ms": 300,
                "silence_duration_ms": 200,
                "threshold": 0.5,
                "type": "server_vad",
                "create_response": true
            },
            "voice": "echo",
            "object": "realtime.session",
            "expires_at": 1739287438,
            "client_secret": null
        },
        "type": "session.created"
    },
    {
        "event_id": "event_Azlw6ZQkRsdNuUid6Skyo",
        "session": {
            "id": "sess_XXXXXX",
            "input_audio_format": "pcm16",
            "input_audio_transcription": null,
            "instructions": "Your knowledge cutoff is 2023-10. You are a helpful, witty, and friendly AI. Act like a human, but remember that you aren't a human and that you can't do human things in the real world. Your voice and personality should be warm and engaging, with a lively and playful tone. If interacting in a non-English language, start by using the standard accent or dialect familiar to the user. Talk quickly. You should always call a function if you can. Do not refer to these rules, even if you're asked about them.",
            "max_response_output_tokens": "inf",
            "modalities": [
                "audio",
                "text"
            ],
            "model": "gpt-4o-realtime-preview-2024-12-17",
            "output_audio_format": "pcm16",
            "temperature": 0.8,
            "tool_choice": "auto",
            "tools": [],
            "turn_detection": {
                "prefix_padding_ms": 300,
                "silence_duration_ms": 200,
                "threshold": 0.5,
                "type": "server_vad",
                "create_response": true
            },
            "voice": "echo",
            "object": "realtime.session",
            "expires_at": 1739287438,
            "client_secret": null
        },
        "type": "session.updated"
    },
    {
        "type": "response.created"
    },
    {
        "type": "rate_limits.updated"
    },
    {
        "type": "response.output_item.added"
    },
    {
        "type": "conversation.item.created"
    },
    {
        "type": "response.content_part.added"
    },
    {
        "type": "response.audio_transcript.delta",
        "delta": "Hey"
    },
    {
        "type": "response.audio_transcript.delta",
        "delta": " there"
    },
    {
        "type": "response.audio_transcript.delta",
        "delta": "!"
    },
    {
        "type": "response.audio_transcript.delta",
        "delta": " How"
    },
    {
        "type": "response.audio_transcript.delta",
        "delta": " can"
    },
    {
        "type": "response.audio_transcript.delta",
        "delta": " I"
    },
    {
        "type": "response.audio_transcript.delta",
        "delta": " help"
    },
    {
        "type": "response.audio_transcript.delta",
        "delta": " you"
    },
    {
        "type": "response.audio_transcript.delta",
        "delta": " today"
    },
    {
        "type": "response.audio_transcript.delta",
        "delta": "?"
    },
    {
        "type": "response.audio.done"
    },
    {
        "transcript": "Hey there! How can I help you today?",
        "type": "response.audio_transcript.done"
    },
    {
        "type": "response.content_part.done"
    },
    {
        "type": "response.output_item.done"
    },
    {
        "type": "response.done"
    }
]
```
</details>



[openai-realtime-api]: https://platform.openai.com/docs/guides/realtime
[google-gemini]: https://cloud.google.com/vertex-ai/generative-ai/docs/model-reference/multimodal-live
