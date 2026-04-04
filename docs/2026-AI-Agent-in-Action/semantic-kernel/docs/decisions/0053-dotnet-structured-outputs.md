---
# 이 항목들은 선택 사항입니다. 필요 없는 항목은 자유롭게 제거하세요.
status: proposed
contact: dmytrostruk
date: 2024-09-10
deciders: sergeymenshykh, markwallace, rbarreto, westey-m, dmytrostruk, ben.thomas, evan.mattson, crickman
---

# .NET 버전 Semantic Kernel의 구조화된 출력(Structured Outputs) 구현

## 컨텍스트 및 문제 설명

[구조화된 출력](https://platform.openai.com/docs/guides/structured-outputs)은 OpenAI API의 기능으로, 제공된 JSON 스키마를 기반으로 모델이 항상 응답을 생성하도록 보장합니다. 이를 통해 모델 응답에 대한 더 많은 제어가 가능하고, 모델 환각을 방지하며, 응답 형식에 대해 구체적으로 지정할 필요 없이 더 간단한 프롬프트를 작성할 수 있습니다. 이 ADR은 .NET 버전 Semantic Kernel에서 이 기능을 활성화하는 여러 옵션을 설명합니다.

.NET 및 Python OpenAI SDK에서 구현된 방법의 예시:

.NET OpenAI SDK:
```csharp
ChatCompletionOptions options = new()
{
    ResponseFormat = ChatResponseFormat.CreateJsonSchemaFormat(
        name: "math_reasoning",
        jsonSchema: BinaryData.FromString("""
            {
                "type": "object",
                "properties": {
                "steps": {
                    "type": "array",
                    "items": {
                    "type": "object",
                    "properties": {
                        "explanation": { "type": "string" },
                        "output": { "type": "string" }
                    },
                    "required": ["explanation", "output"],
                    "additionalProperties": false
                    }
                },
                "final_answer": { "type": "string" }
                },
                "required": ["steps", "final_answer"],
                "additionalProperties": false
            }
            """),
    strictSchemaEnabled: true)
};

ChatCompletion chatCompletion = await client.CompleteChatAsync(
    ["How can I solve 8x + 7 = -23?"],
    options);

using JsonDocument structuredJson = JsonDocument.Parse(chatCompletion.ToString());

Console.WriteLine($"Final answer: {structuredJson.RootElement.GetProperty("final_answer").GetString()}");
Console.WriteLine("Reasoning steps:");
```

Python OpenAI SDK:

```python
class CalendarEvent(BaseModel):
    name: str
    date: str
    participants: list[str]

completion = client.beta.chat.completions.parse(
    model="gpt-4o-2024-08-06",
    messages=[
        {"role": "system", "content": "Extract the event information."},
        {"role": "user", "content": "Alice and Bob are going to a science fair on Friday."},
    ],
    response_format=CalendarEvent,
)

event = completion.choices[0].message.parsed
```

## 고려된 옵션

**참고**: 이 ADR에 제시된 모든 옵션은 상호 배타적이지 않으며 동시에 구현하고 지원할 수 있습니다.

### 옵션 #1: ResponseFormat 속성에 OpenAI.Chat.ChatResponseFormat 객체 사용 (.NET OpenAI SDK와 유사)

이 접근 방식은 사용자가 JSON 스키마가 포함된 `OpenAI.Chat.ChatResponseFormat` 객체를 구성하여 `OpenAIPromptExecutionSettings.ResponseFormat` 속성에 제공하면, Semantic Kernel이 이를 .NET OpenAI SDK에 그대로 전달하는 것을 의미합니다.

사용 예시:

```csharp
// Kernel 초기화
Kernel kernel = Kernel.CreateBuilder()
    .AddOpenAIChatCompletion(
        modelId: "gpt-4o-2024-08-06",
        apiKey: TestConfiguration.OpenAI.ApiKey)
    .Build();

// 문자열에서 원하는 응답 타입의 JSON 스키마 생성.
ChatResponseFormat chatResponseFormat = ChatResponseFormat.CreateJsonSchemaFormat(
    name: "math_reasoning",
    jsonSchema: BinaryData.FromString("""
        {
            "type": "object",
            "properties": {
                "Steps": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "Explanation": { "type": "string" },
                            "Output": { "type": "string" }
                        },
                    "required": ["Explanation", "Output"],
                    "additionalProperties": false
                    }
                },
                "FinalAnswer": { "type": "string" }
            },
            "required": ["Steps", "FinalAnswer"],
            "additionalProperties": false
        }
        """),
    strictSchemaEnabled: true);

// OpenAIPromptExecutionSettings.ResponseFormat 속성에 ChatResponseFormat 전달.
var executionSettings = new OpenAIPromptExecutionSettings
{
    ResponseFormat = chatResponseFormat
};

// 문자열 결과 가져오기.
var result = await kernel.InvokePromptAsync("How can I solve 8x + 7 = -23?", new(executionSettings));

Console.WriteLine(result.ToString());

// 출력:

// {
//    "Steps":[
//       {
//          "Explanation":"Start with the equation: (8x + 7 = -23). The goal is to isolate (x) on one side of the equation. To begin, we need to remove the constant term from the left side of the equation.",
//          "Output":"8x + 7 = -23"
//       },
//       {
//          "Explanation":"Subtract 7 from both sides of the equation to eliminate the constant from the left side.",
//          "Output":"8x + 7 - 7 = -23 - 7"
//       },
//       {
//          "Explanation":"Simplify both sides: The +7 and -7 on the left will cancel out, while on the right side, -23 - 7 equals -30.",
//          "Output":"8x = -30"
//       },
//       {
//          "Explanation":"Now, solve for (x) by dividing both sides of the equation by 8. This will isolate (x).",
//          "Output":"8x / 8 = -30 / 8"
//       },
//       {
//          "Explanation":"Simplify the right side of the equation by performing the division: -30 divided by 8 equals -3.75.",
//          "Output":"x = -3.75"
//       }
//    ],
//    "FinalAnswer":"x = -3.75"
// }
```

장점:
- 이 접근 방식은 `ChatResponseFormat` 객체를 .NET OpenAI SDK에 그대로 전달하는 로직이 이미 있으므로, 추가 변경 없이 Semantic Kernel에서 이미 지원됩니다.
- .NET OpenAI SDK와 일관적.

단점:
- 타입 안전성 없음. 응답 타입에 대한 정보를 사용자가 수동으로 구성해야 요청을 수행할 수 있습니다. 각 응답 속성에 접근하려면 응답도 수동으로 처리해야 합니다. C# 타입을 정의하고 응답에 JSON 역직렬화를 사용할 수 있지만, 요청용 JSON 스키마는 여전히 별도로 정의되므로 타입에 대한 정보가 2곳에 저장되며 타입에 대한 모든 수정은 2곳에서 처리해야 합니다.
- Python 버전과 일관적이지 않음. Python에서는 응답 타입이 클래스로 정의되고 단순 할당으로 `response_format` 속성에 전달됩니다.

### 옵션 #2: ResponseFormat 속성에 C# 타입 사용 (Python OpenAI SDK와 유사)

이 접근 방식은 `OpenAI.Chat.ChatResponseFormat` 객체와 JSON 스키마가 Semantic Kernel에 의해 구성되며, 사용자는 C# 타입만 정의하여 `OpenAIPromptExecutionSettings.ResponseFormat` 속성에 할당하면 됩니다.

사용 예시:

```csharp
// 원하는 응답 모델 정의
private sealed class MathReasoning
{
    public List<MathReasoningStep> Steps { get; set; }

    public string FinalAnswer { get; set; }
}

private sealed class MathReasoningStep
{
    public string Explanation { get; set; }

    public string Output { get; set; }
}

// Kernel 초기화
Kernel kernel = Kernel.CreateBuilder()
    .AddOpenAIChatCompletion(
        modelId: "gpt-4o-2024-08-06",
        apiKey: TestConfiguration.OpenAI.ApiKey)
    .Build();

// OpenAIPromptExecutionSettings.ResponseFormat 속성에 원하는 응답 타입 전달.
var executionSettings = new OpenAIPromptExecutionSettings
{
    ResponseFormat = typeof(MathReasoning)
};

// 문자열 결과 가져오기.
var result = await kernel.InvokePromptAsync("How can I solve 8x + 7 = -23?", new(executionSettings));

// 문자열을 원하는 응답 타입으로 역직렬화.
var mathReasoning = JsonSerializer.Deserialize<MathReasoning>(result.ToString())!;

OutputResult(mathReasoning);

// 출력:

// Step #1
// Explanation: Start with the given equation.
// Output: 8x + 7 = -23

// Step #2
// Explanation: To isolate the term containing x, subtract 7 from both sides of the equation.
// Output: 8x + 7 - 7 = -23 - 7

// Step #3
// Explanation: To solve for x, divide both sides of the equation by 8, which is the coefficient of x.
// Output: (8x)/8 = (-30)/8

// Step #4
// Explanation: This simplifies to x = -3.75, as dividing -30 by 8 gives -3.75.
// Output: x = -3.75

// Final answer: x = -3.75
```

장점:
- 타입 안전성. JSON 스키마를 Semantic Kernel이 처리하므로 사용자가 수동으로 정의할 필요가 없어, C# 타입 정의에만 집중할 수 있습니다. C# 타입의 속성을 추가하거나 제거하여 원하는 응답 형식을 변경할 수 있습니다. 특정 속성에 대한 더 상세한 정보를 제공하기 위해 `Description` 어트리뷰트가 지원됩니다.
- Python OpenAI SDK와 일관적.
- Semantic Kernel 코드베이스에 이미 C# 타입에서 JSON 스키마를 빌드하는 로직이 있으므로 최소한의 코드 변경이 필요합니다.

단점:
- 원하는 타입을 `ResponseFormat = typeof(MathReasoning)` 또는 `ResponseFormat = object.GetType()` 할당으로 제공해야 하며, C# 제네릭을 사용하여 개선할 수 있습니다.
- Kernel에서 반환되는 응답이 여전히 `string`이므로, 사용자가 원하는 타입으로 수동 역직렬화해야 합니다.

### 옵션 #3: C# 제네릭 사용

이 접근 방식은 옵션 #2와 유사하지만, `ResponseFormat = typeof(MathReasoning)` 또는 `ResponseFormat = object.GetType()` 할당 대신 C# 제네릭을 사용할 수 있습니다.

사용 예시:

```csharp
// 원하는 응답 모델 정의
private sealed class MathReasoning
{
    public List<MathReasoningStep> Steps { get; set; }

    public string FinalAnswer { get; set; }
}

private sealed class MathReasoningStep
{
    public string Explanation { get; set; }

    public string Output { get; set; }
}

// Kernel 초기화
Kernel kernel = Kernel.CreateBuilder()
    .AddOpenAIChatCompletion(
        modelId: "gpt-4o-2024-08-06",
        apiKey: TestConfiguration.OpenAI.ApiKey)
    .Build();

// MathReasoning 결과 가져오기.
var result = await kernel.InvokePromptAsync<MathReasoning>("How can I solve 8x + 7 = -23?");

OutputResult(mathReasoning);
```

장점:
- 간단한 사용법, `PromptExecutionSettings` 정의 및 이후 문자열 응답 역직렬화가 필요 없음.

단점:
- 옵션 #1 및 옵션 #2에 비해 구현 복잡성:
    1. 채팅 완성 서비스는 문자열을 반환하므로, 문자열 대신 타입을 반환하기 위한 역직렬화 로직을 어딘가에 추가해야 합니다. 잠재적 위치: `FunctionResult`, 이미 `GetValue<T>` 제네릭 메서드를 포함하고 있지만 역직렬화 로직이 없으므로 추가하고 테스트해야 합니다.
    2. `IChatCompletionService`와 그 메서드는 제네릭이 아니지만, 응답 타입에 대한 정보는 여전히 OpenAI 커넥터에 전달되어야 합니다. 한 가지 방법은 제네릭 버전의 `IChatCompletionService`를 추가하는 것이며, 이는 많은 추가 코드 변경을 도입할 수 있습니다. 다른 방법은 `PromptExecutionSettings` 객체를 통해 타입 정보를 전달하는 것입니다. `IChatCompletionService`가 `OpenAIPromptExecutionSettings`가 아닌 `PromptExecutionSettings`를 사용한다는 점을 고려하면, 특정 커넥터에 결합하지 않고 응답 형식에 대한 정보를 전달할 수 있도록 `ResponseFormat` 속성을 기본 실행 설정 클래스로 이동해야 합니다. 반면에 `ResponseFormat` 파라미터가 다른 AI 커넥터에 유용할지는 불명확합니다.
    3. 역직렬화를 위해 모든 응답 콘텐츠를 먼저 집계해야 하므로 스트리밍 시나리오는 지원되지 않습니다. Semantic Kernel이 집계를 수행하면 스트리밍 기능이 상실됩니다.

## 범위 밖

함수 호출 기능은 이 ADR의 범위 밖입니다. 구조화된 출력 기능은 이미 현재 함수 호출 구현에서 함수와 인수에 대한 정보가 포함된 JSON 스키마를 제공하여 부분적으로 사용되고 있기 때문입니다. 이 프로세스에 추가해야 할 유일한 나머지 파라미터는 구조화된 출력을 함수 호출에서 활성화하기 위해 `true`로 설정해야 하는 `strict` 속성입니다. 이 파라미터는 `PromptExecutionSettings` 타입을 통해 노출될 수 있습니다.

함수 호출 프로세스에 대해 `strict` 속성을 `true`로 설정하면, 모델이 존재하지 않는 추가 파라미터나 함수를 생성하지 않아야 하므로 환각 문제를 해결할 수 있습니다. 반면에 함수 호출에 구조화된 출력을 활성화하면 스키마가 먼저 처리되므로 첫 번째 요청 시 추가 지연이 발생하여 성능에 영향을 줄 수 있으며, 이는 이 속성이 잘 문서화되어야 함을 의미합니다.

자세한 정보: [구조화된 출력을 사용한 함수 호출](https://platform.openai.com/docs/guides/function-calling/function-calling-with-structured-outputs).

## 결정 결과

1. 옵션 #1과 옵션 #2를 지원하고, 옵션 #3은 별도로 처리하기 위한 작업을 생성합니다.
2. 함수 호출에서의 구조화된 출력을 위한 작업을 생성하고 별도로 처리합니다.
