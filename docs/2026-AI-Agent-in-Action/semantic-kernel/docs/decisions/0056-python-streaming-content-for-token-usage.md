---
# 이 항목들은 선택 사항입니다. 필요 없는 항목은 자유롭게 제거하세요.
status: { accepted }
contact: { Tao Chen }
date: { 2024-09-18 }
deciders: { Tao Chen }
consulted: { Eduard van Valkenburg, Evan Mattson }
informed: { Eduard van Valkenburg, Evan Mattson, Ben Thomas }
---

# 토큰 사용량 정보를 위한 스트리밍 콘텐츠 (Semantic Kernel Python)

## 컨텍스트 및 문제 설명

현재 Semantic Kernel의 `StreamingChatMessageContent`(`StreamingContentMixin`에서 상속)는 선택 인덱스(choice index)를 지정해야 합니다. 이는 **OpenAI의 스트리밍 채팅 완성** API에서 토큰 사용량 정보가 choices 필드가 비어 있는 마지막 청크에서 반환되기 때문에 제한을 만들어, 해당 청크의 선택 인덱스를 알 수 없게 합니다. 자세한 내용은 [OpenAI API 문서](https://platform.openai.com/docs/api-reference/chat/create)의 `stream_options` 필드를 참조하세요.

> 마지막 청크에서 반환되는 토큰 사용량 정보는 지정된 선택 수에 관계없이 채팅 완성 요청의 **전체** 토큰 사용량입니다. 즉, 여러 선택이 요청된 경우에도 스트리밍 응답에서 토큰 사용량 정보를 포함하는 청크는 하나뿐입니다.

`StreamingChatMessageContent`의 현재 데이터 구조:

```Python
# semantic_kernel/content/streaming_chat_message_content.py
class StreamingChatMessageContent(ChatMessageContent, StreamingContentMixin):

# semantic_kernel/content/chat_message_content.py
class ChatMessageContent(KernelContent):
    content_type: Literal[ContentTypes.CHAT_MESSAGE_CONTENT] = Field(CHAT_MESSAGE_CONTENT_TAG, init=False)  # type: ignore
    tag: ClassVar[str] = CHAT_MESSAGE_CONTENT_TAG
    role: AuthorRole
    name: str | None = None
    items: list[Annotated[ITEM_TYPES, Field(..., discriminator=DISCRIMINATOR_FIELD)]] = Field(default_factory=list)
    encoding: str | None = None
    finish_reason: FinishReason | None = None

# semantic_kernel/content/streaming_content_mixin.py
class StreamingContentMixin(KernelBaseModel, ABC):
    choice_index: int

# semantic_kernel/content/kernel_content.py
class KernelContent(KernelBaseModel, ABC):
    inner_content: Any | None = None
    ai_model_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
```

## 제안 1

비스트리밍 응답에서 토큰 사용량은 하나 이상의 선택과 함께 모델의 응답 일부로 반환됩니다. 그런 다음 선택을 개별 `ChatMessageContent`로 파싱하며, 토큰 사용량이 개별 선택이 아닌 전체 응답에 대한 것임에도 불구하고 각각에 토큰 사용량 정보를 포함합니다.

동일한 전략을 고려하면, 스트리밍 응답의 모든 선택은 `choice_index`에 의해 최종적으로 결합될 때 토큰 사용량 정보를 포함해야 합니다. 요청된 선택 수를 알고 있으므로 다음 단계를 수행할 수 있습니다:

1. 마지막 청크를 요청된 각 선택에 대해 복제하여 메타데이터에 토큰 사용량 정보가 포함된 `StreamingChatMessageContent` 목록을 생성합니다.
2. 0부터 시작하여 각 복제된 청크에 선택 인덱스를 할당합니다.
3. 복제된 청크를 목록으로 클라이언트에 스트리밍합니다.

### 추가 고려 사항

현재 두 `StreamingChatMessageContent`가 "더해질" 때 메타데이터가 병합되지 않습니다. 청크가 결합될 때 메타데이터가 올바르게 병합되도록 해야 합니다. 충돌하는 메타데이터 키가 있을 때 두 번째 청크의 메타데이터가 첫 번째 청크의 메타데이터를 덮어씁니다:

```Python
class StreamingChatMessageContent(ChatMessageContent, StreamingContentMixin):
    ...

    def __add__(self, other: "StreamingChatMessageContent") -> "StreamingChatMessageContent":
        ...

        return StreamingChatMessageContent(
            ...,
            metadata=self.metadata | other.metadata,
            ...
        )

    ...
```

### 위험 사항

이 제안과 관련된 호환성 깨짐 변경 및 알려진 위험은 없습니다.

## 제안 2

`StreamingContentMixin` 클래스에서 선택 인덱스를 선택적으로 허용합니다. 이를 통해 토큰 사용량 정보가 마지막 청크에서 반환될 때 선택 인덱스가 `None`이 될 수 있습니다. 마지막 청크에서 선택 인덱스가 `None`으로 설정되며, 클라이언트가 토큰 사용량 정보를 적절히 처리할 수 있습니다.

```Python
# semantic_kernel/content/streaming_content_mixin.py
class StreamingContentMixin(KernelBaseModel, ABC):
    choice_index: int | None
```

이것은 제안 1에 비해 더 간단한 솔루션이며, OpenAI API가 반환하는 것과 더 일치합니다. 즉, 토큰 사용량이 특정 선택과 연관되지 않습니다.

### 위험 사항

`choice_index` 필드가 현재 필수이므로 이것은 잠재적인 호환성 깨짐 변경입니다. 이 접근 방식은 또한 선택 인덱스가 `None`일 때 다르게 처리해야 하므로 스트리밍 콘텐츠 결합을 더 복잡하게 만듭니다.

## 제안 3

`ChatMessageContent`와 `StreamingChatMessageContent`를 단일 클래스 `ChatMessageContent`로 병합하고, `StreamingChatMessageContent`를 사용 중단으로 표시합니다. `StreamingChatMessageContent` 클래스는 향후 릴리스에서 제거됩니다. 그런 다음 토큰 사용량 정보를 처리하기 위해 [제안 1](#제안-1) 또는 [제안 2](#제안-2)를 `ChatMessageContent` 클래스에 적용합니다.

이 접근 방식은 스트리밍 채팅 메시지를 위한 별도의 클래스가 필요 없어 코드베이스를 단순화합니다. `ChatMessageContent` 클래스가 스트리밍 및 비스트리밍 채팅 메시지를 모두 처리할 수 있게 됩니다.

```Python
# semantic_kernel/content/streaming_chat_message_content.py
@deprecated("StreamingChatMessageContent is deprecated. Use ChatMessageContent instead.")
class StreamingChatMessageContent(ChatMessageContent):
    pass

# semantic_kernel/content/chat_message_content.py
class ChatMessageContent(KernelContent):
    ...
    # ChatMessageContent 클래스에 choice_index 필드를 추가하고 선택적으로 만듬
    choice_index: int | None

    # 두 ChatMessageContent 인스턴스가 더해질 때 메타데이터를 병합하는 __add__ 메서드 추가. 이것은 현재 `StreamingContentMixin` 클래스의 추상 메서드임.
    def __add__(self, other: "ChatMessageContent") -> "ChatMessageContent":
        ...

        return ChatMessageContent(
            ...,
            choice_index=self.choice_index,
            ...
        )

    # ChatMessageContent 인스턴스의 바이트 표현을 반환하는 __bytes__ 메서드 추가. 이것은 현재 `StreamingContentMixin` 클래스의 추상 메서드임.
    def __bytes__(self) -> bytes:
        ...
```

### 위험 사항

스트리밍 및 비스트리밍 채팅 메시지에 대한 반환 데이터 구조를 통합하고 있으므로, 특히 `StreamingChatMessageContent` 클래스의 사용 중단을 모르는 개발자에게는 초기에 혼란을 줄 수 있습니다. 또는 SK .Net에서 시작한 개발자에게도 마찬가지입니다. Python으로 시작했지만 나중에 프로덕션을 위해 .Net으로 이동하는 개발자에게는 더 가파른 학습 곡선을 만들 수도 있습니다. 이 접근 방식은 또한 반환 데이터 타입이 다르므로 AI 커넥터에 호환성 깨짐 변경을 도입합니다.

> 이 제안에 대해 `StreamingTextContent`와 `TextContent`도 유사한 방식으로 업데이트해야 합니다.

## 제안 4

[제안 3](#제안-3)과 유사하게, `ChatMessageContent`와 `StreamingChatMessageContent`를 단일 클래스 `ChatMessageContent`로 병합하고, `StreamingChatMessageContent`를 사용 중단으로 표시합니다. 또한 두 `ChatMessageContent` 인스턴스의 결합을 처리하기 위해 `ChatMessageContentConcatenationMixin`이라는 새 mixin을 도입합니다. 그런 다음 토큰 사용량 정보를 처리하기 위해 [제안 1](#제안-1) 또는 [제안 2](#제안-2)를 `ChatMessageContent` 클래스에 적용합니다.

```Python
# semantic_kernel/content/streaming_chat_message_content.py
@deprecated("StreamingChatMessageContent is deprecated. Use ChatMessageContent instead.")
class StreamingChatMessageContent(ChatMessageContent):
    pass

# semantic_kernel/content/chat_message_content.py
class ChatMessageContent(KernelContent, ChatMessageContentConcatenationMixin):
    ...
    # ChatMessageContent 클래스에 choice_index 필드를 추가하고 선택적으로 만듬
    choice_index: int | None

    # ChatMessageContent 인스턴스의 바이트 표현을 반환하는 __bytes__ 메서드 추가. 이것은 현재 `StreamingContentMixin` 클래스의 추상 메서드임.
    def __bytes__(self) -> bytes:
        ...

class ChatMessageContentConcatenationMixin(KernelBaseModel, ABC):
    def __add__(self, other: "ChatMessageContent") -> "ChatMessageContent":
        ...
```

이 접근 방식은 `ChatMessageContent` 클래스의 관심사와 결합 로직을 두 개의 별도 클래스로 분리합니다. 이를 통해 코드베이스를 깨끗하고 유지 보수 가능하게 유지할 수 있습니다.

### 위험 사항

[제안 3](#제안-3)과 동일합니다.

## 결정 결과

고객과 기존 코드베이스에 대한 영향을 최소화하기 위해, OpenAI 스트리밍 응답에서 토큰 사용량 정보를 처리하기 위해 [제안 1](#제안-1)을 선택합니다. 이 제안은 하위 호환성이 있으며 비스트리밍 응답의 현재 데이터 구조와 일치합니다. 또한 두 `StreamingChatMessageContent` 인스턴스가 결합될 때 메타데이터가 올바르게 병합되도록 합니다. 이 접근 방식은 또한 토큰 사용량 정보가 스트리밍 응답의 모든 선택에 연관되도록 합니다.

[제안 3](#제안-3)과 [제안 4](#제안-4)는 여전히 유효하지만, 대부분의 서비스가 스트리밍 및 비스트리밍 응답에 대해 여전히 다른 타입의 객체를 반환하므로 현 시점에서는 시기상조일 수 있습니다. 향후 리팩토링 노력을 위해 이를 염두에 둘 것입니다.
