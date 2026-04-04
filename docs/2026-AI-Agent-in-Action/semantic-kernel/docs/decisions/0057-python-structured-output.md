---
# 이 항목들은 선택 사항입니다. 필요 없는 항목은 자유롭게 제거하세요.
status: { in-progress }
contact: { Evan Mattson }
date: { 2024-09-10 }
deciders: { Ben Thomas }
consulted: { Dmytro Struk }
informed:
  { Eduard van Valkenburg, Ben Thomas, Tao Chen, Dmytro Struk, Mark Wallace }
---

# Semantic Kernel Python에서 OpenAI의 구조화된 출력 지원

## 컨텍스트

지난해 OpenAI는 신뢰할 수 있는 AI 기반 애플리케이션을 구축하려는 개발자에게 필수적인 기능인 JSON 모드를 도입했습니다. JSON 모드가 유효한 JSON 출력 생성에서 모델 신뢰성을 향상시키는 데 도움이 되지만, 특정 스키마에 대한 엄격한 준수를 강제하지는 않습니다. 이 제한으로 인해 개발자들은 출력이 요구되는 형식을 준수하도록 보장하기 위해 커스텀 오픈소스 도구, 반복적 프롬프팅 및 재시도와 같은 우회 방법을 사용해야 했습니다.

이 문제를 해결하기 위해 OpenAI는 **구조화된 출력(Structured Outputs)** -- 모델 생성 출력이 개발자가 지정한 JSON 스키마에 정확히 일치하도록 보장하는 기능을 도입했습니다. 이 발전으로 개발자는 AI 출력이 미리 정의된 구조와 일치할 것이라는 보장을 제공하여 보다 견고한 애플리케이션을 구축할 수 있으며, 다운스트림 시스템과의 상호 운용성을 향상시킵니다.

최근 평가에서 구조화된 출력이 적용된 새 GPT-4o-2024-08-06 모델은 복잡한 JSON 스키마 준수에서 완벽한 100% 점수를 보였으며, 40% 미만 점수를 받은 GPT-4-0613과 비교됩니다. 구조화된 출력은 비정형 입력에서 신뢰할 수 있는 정형 데이터를 생성하는 프로세스를 간소화하며, 데이터 추출, 자동화된 워크플로우 및 함수 호출과 같은 다양한 AI 기반 애플리케이션의 핵심 요구 사항입니다.

---

## 문제 설명

OpenAI API를 사용하여 AI 기반 솔루션을 구축하는 개발자는 비정형 입력에서 정형 데이터를 추출할 때 종종 어려움에 직면합니다. 모델 출력이 미리 정의된 JSON 스키마를 준수하도록 보장하는 것은 신뢰할 수 있고 상호 운용 가능한 시스템을 만드는 데 매우 중요합니다. 그러나 JSON 모드를 사용하더라도 현재 모델은 스키마 적합성을 보장하지 않아, 재시도 및 커스텀 도구 형태의 비효율성, 오류 및 추가 개발 오버헤드를 초래합니다.

구조화된 출력의 도입으로 OpenAI 모델은 이제 개발자가 제공한 JSON 스키마를 엄격히 준수할 수 있습니다. 이 기능은 번거로운 우회 방법의 필요성을 제거하고 모델 출력의 일관성과 신뢰성을 보장하는 보다 간소화되고 효율적인 방법을 제공합니다. 구조화된 출력을 Semantic Kernel 오케스트레이션 SDK에 통합하면 개발자가 더 강력하고 스키마를 준수하는 애플리케이션을 만들고, 오류를 줄이고, 전반적인 생산성을 향상시킬 수 있습니다.

## 범위 밖

이 ADR은 `structured outputs`의 `response_format`에 초점을 맞추며 함수 호출 측면은 다루지 않습니다. 이에 대한 후속 ADR이 향후 작성될 예정입니다.

## 구조화된 출력 사용

### 응답 형식

OpenAI는 프롬프트 실행 설정 어트리뷰트에서 `response_format`을 설정하는 새로운 방법을 제공합니다:

```python
from pydantic import BaseModel

from openai import OpenAI


class Step(BaseModel):
    explanation: str
    output: str


class MathResponse(BaseModel):
    steps: list[Step]
    final_answer: str


client = AsyncOpenAI()

completion = await client.beta.chat.completions.parse(
    model="gpt-4o-2024-08-06",
    messages=[
        {"role": "system", "content": "You are a helpful math tutor."},
        {"role": "user", "content": "solve 8x + 31 = 2"},
    ],
    response_format=MathResponse, # 예를 들어, Pydantic 모델 타입이 직접 구성됨
)

message = completion.choices[0].message
if message.parsed:
    print(message.parsed.steps)
    print(message.parsed.final_answer)
else:
    print(message.refusal)
```

비-Pydantic 모델의 경우, SK는 `KernelParameterMetadata`의 `schema_data` 어트리뷰트를 사용해야 합니다. 이것은 SK 함수의 JSON 스키마를 나타냅니다:

```json
{
  "type": "object",
  "properties": {
    "steps": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "explanation": {
            "type": "string"
          },
          "output": {
            "type": "string"
          }
        },
        "required": ["explanation", "output"],
        "additionalProperties": false
      }
    },
    "final_answer": {
      "type": "string"
    }
  },
  "required": ["steps", "final_answer"],
  "additionalProperties": false
}
```

필요한 `json_schema` `response_format`을 생성하기 위해:

```json
"response_format": {
    "type": "json_schema",
    "json_schema": {
        "name": "math_response",
        "strict": true,
        "schema": { // 위의 기존 SK `schema_data` 시작
            "type": "object",
            "properties": {
                "steps": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                    "explanation": {
                        "type": "string"
                    },
                    "output": {
                        "type": "string"
                    }
                    },
                    "required": ["explanation", "output"],
                    "additionalProperties": false
                }
                },
                "final_answer": {
                    "type": "string"
                }
            },
            "required": ["steps", "final_answer"],
            "additionalProperties": false
        } // 위의 기존 SK `schema_data` 끝
    }
}
```

#### 스트리밍 응답 형식 처리

새 `structured output` 응답 형식은 베타 단계이며, 스트리밍 채팅 완성 코드는 다음과 같이 처리되어야 합니다(현재 스트리밍 채팅 완성 호출과 다름):

```python
async with client.beta.chat.completions.stream(
    model='gpt-4o-mini',
    messages=messages,
    tools=[pydantic_function_tool(SomeClass)],
) as stream:
    async for event in stream:
        if event.type == 'content.delta':
            print(event.delta, flush=True, end='')
        elif event.type == 'content.done':
            content = event.content
        elif event.type == 'tool_calls.function.arguments.done':
            tool_calls.append({'name': event.name, 'parsed_arguments': event.parsed_arguments})

print(content)
```

채팅 완성을 관리하는 `OpenAIHandler` 클래스는 새로운 구조화된 출력 스트리밍 메서드를 처리해야 하며, 다음과 유사합니다:

```python
async def _initiate_chat_stream(self, settings: OpenAIChatPromptExecutionSettings):
    """채팅 스트림 요청을 시작하고 스트림을 반환합니다."""
    return self.client.beta.chat.completions.stream(
        model='gpt-4o-mini',
        messages=settings.messages,
        tools=[pydantic_function_tool(SomeClass)],
    )

async def _handle_chat_stream(self, stream):
    """채팅 스트림의 이벤트를 처리합니다."""
    async for event in stream:
        if event.type == 'content.delta':
            chunk_metadata = self._get_metadata_from_streaming_chat_response(event)
            yield [
                self._create_streaming_chat_message_content(event, event.delta, chunk_metadata)
            ]
        elif event.type == 'tool_calls.function.arguments.done':
            # 필요에 따라 도구 호출 결과 처리
            tool_calls.append({'name': event.name, 'parsed_arguments': event.parsed_arguments})

# 호출 메서드 예시:
async def _send_chat_stream_request(self, settings: OpenAIChatPromptExecutionSettings):
    """채팅 스트림 요청을 보내고 스트림을 처리합니다."""
    async with await self._initiate_chat_stream(settings) as stream:
        async for chunk in self._handle_chat_stream(stream):
            yield chunk
```

스트리밍 또는 비스트리밍 채팅 완성을 처리하는 메서드는 `response_format` 실행 설정에 기반합니다 -- Pydantic 모델 타입을 사용하는지 JSON 스키마를 사용하는지에 따라 다릅니다.

`response_format` 채팅 완성 메서드가 현재 채팅 완성 접근 방식과 다르므로, OpenAI가 졸업 시 `response_format` 메서드를 메인 라이브러리에 공식적으로 통합할 때까지 채팅 완성 처리를 위한 별도의 구현을 유지해야 합니다.

### 주의 사항

- `structured output` `response_format`은 현재 단일 객체 타입으로 제한됩니다. 사용자가 적절한 타입/수의 객체만 지정하도록 Pydantic 유효성 검사기를 사용합니다:

```python
@field_validator("response_format", mode="before")
    @classmethod
    def validate_response_format(cls, value):
        """response_format 파라미터를 유효성 검사합니다."""
        if not isinstance(value, dict) and not (isinstance(value, type) and issubclass(value, BaseModel)):
            raise ServiceInvalidExecutionSettingsError(
                "response_format must be a dictionary or a single Pydantic model class"
            )
        return value
```

- 어떤 OpenAI/AzureOpenAI 모델/API 버전이 `structured outputs`를 지원하는지 사용자와 개발자에게 알려주는 좋은(그리고 찾기 쉬운) 문서를 제공해야 합니다.

### 선택된 솔루션

- 응답 형식: 여기에는 단일 접근 방식이 있으므로, 기존 `OpenAIChatCompletionBase` 및 `OpenAIHandler` 코드를 사용하여 스트리밍 및 비스트리밍 채팅 완성을 모두 정의하는 깔끔한 구현을 통합해야 합니다.
