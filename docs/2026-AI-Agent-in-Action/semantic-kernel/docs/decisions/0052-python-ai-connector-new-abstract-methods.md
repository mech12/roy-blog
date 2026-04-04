---
# 이 항목들은 선택 사항입니다. 필요 없는 항목은 자유롭게 제거하세요.
status: { accepted }
contact: { Tao Chen }
date: { 2024-09-03 }
deciders: { Eduard van Valkenburg, Ben Thomas }
consulted: { Eduard van Valkenburg }
informed: { Eduard van Valkenburg, Ben Thomas }
---

# `ChatCompletionClientBase` 및 `TextCompletionClientBase`의 새 추상 메서드 (Semantic Kernel Python)

## 컨텍스트 및 문제 설명

`ChatCompletionClientBase` 클래스에는 현재 `get_chat_message_contents`와 `get_streaming_chat_message_contents`라는 두 개의 추상 메서드가 있습니다. 이 메서드들은 클라이언트가 다양한 모델과 상호작용하기 위한 표준화된 인터페이스를 제공합니다.

> 이 ADR에서는 `ChatCompletionClientBase`에 집중하지만 `TextCompletionClientBase`도 유사한 구조를 가질 것입니다.

많은 모델에 함수 호출이 도입됨에 따라, Semantic Kernel은 `auto function invocation`이라는 뛰어난 기능을 구현했습니다. 이 기능은 개발자가 모델이 요청한 함수를 수동으로 호출하는 부담에서 벗어나게 하여 개발 프로세스를 훨씬 더 매끄럽게 만듭니다.

자동 함수 호출은 `get_chat_message_contents` 또는 `get_streaming_chat_message_contents`에 대한 단일 호출이 모델에 대한 여러 호출을 초래할 수 있는 부작용을 야기할 수 있습니다. 그러나 이것은 모델에 대한 단일 호출만을 담당하는 또 다른 추상화 계층을 도입할 수 있는 훌륭한 기회를 제공합니다.

## 장점

- 구현을 단순화하기 위해 `get_chat_message_contents`와 `get_streaming_chat_message_contents`의 기본 구현을 포함할 수 있습니다.
- 개별 모델 호출을 추적하기 위한 공통 인터페이스를 도입할 수 있어, 시스템의 전반적인 모니터링과 관리를 개선할 수 있습니다.
- 이 추상화 계층을 도입함으로써 시스템에 새로운 AI 커넥터를 추가하는 것이 더 효율적이 됩니다.

## 세부 사항

### 두 개의 새 추상 메서드

> 수정: 자체 AI 커넥터를 구현한 기존 고객을 깨뜨리지 않기 위해, 이 두 메서드는 `@abstractmethod` 데코레이터로 장식되지 않고, 대신 내장 AI 커넥터에서 구현되지 않은 경우 예외를 발생시킵니다.

```python
async def _inner_get_chat_message_content(
    self,
    chat_history: ChatHistory,
    settings: PromptExecutionSettings
) -> list[ChatMessageContent]:
    raise NotImplementedError
```

```python
async def _inner_get_streaming_chat_message_content(
    self,
    chat_history: ChatHistory,
    settings: PromptExecutionSettings
) -> AsyncGenerator[list[StreamingChatMessageContent], Any]:
    raise NotImplementedError
```

### 커넥터가 함수 호출을 지원하는지 나타내는 `ChatCompletionClientBase`의 새 `ClassVar[bool]` 변수

이 클래스 변수는 파생 클래스에서 재정의되며, `get_chat_message_contents`와 `get_streaming_chat_message_contents`의 기본 구현에서 사용됩니다.

```python
class ChatCompletionClientBase(AIServiceClientBase, ABC):
    """채팅 완성 AI 서비스의 기본 클래스."""

    SUPPORTS_FUNCTION_CALLING: ClassVar[bool] = False
    ...
```

```python
class MockChatCompletionThatSupportsFunctionCalling(ChatCompletionClientBase):

    SUPPORTS_FUNCTION_CALLING: ClassVar[bool] = True

    @override
    async def get_chat_message_contents(
        self,
        chat_history: ChatHistory,
        settings: "PromptExecutionSettings",
        **kwargs: Any,
    ) -> list[ChatMessageContent]:
        if not self.SUPPORTS_FUNCTION_CALLING:
            return ...
        ...
```
