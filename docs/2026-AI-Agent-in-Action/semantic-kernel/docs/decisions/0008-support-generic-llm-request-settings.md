---
# 이 항목들은 선택 사항입니다. 필요 없는 항목은 자유롭게 제거하세요.
status: accepted
contact: markwallace-microsoft
date: 2023-9-15
deciders: shawncal
consulted: stephentoub, lemillermicrosoft, dmytrostruk
informed:
---

# 범용 LLM 요청 설정 지원을 위한 리팩토링

## 배경 및 문제 상황

Semantic Kernel 추상화 패키지에는 다음을 지원하는 데 사용되는 여러 클래스(`CompleteRequestSettings`, `ChatRequestSettings`, `PromptTemplateConfig.CompletionConfig`)가 포함되어 있습니다:

1. AI 서비스를 호출할 때 LLM 요청 설정을 전달
2. 시맨틱 함수와 연관된 `config.json`을 로드할 때 LLM 요청 설정의 역직렬화

이 클래스들의 문제점은 OpenAI 전용 속성만 포함한다는 것입니다. 개발자는 OpenAI 전용 요청 설정만 전달할 수 있으므로:

1. 효과가 없는 설정이 전달될 수 있습니다. 예: Huggingface에 `MaxTokens` 전달
2. OpenAI 속성과 겹치지 않는 설정을 보낼 수 없습니다. 예: Oobabooga는 `do_sample`, `typical_p` 등의 추가 매개변수를 지원합니다.

Oobabooga AI 서비스 구현자가 제기한 이슈 링크: <https://github.com/microsoft/semantic-kernel/issues/2735>

## 결정 동인

- Semantic Kernel 추상화는 AI 서비스에 종속적이지 않아야 합니다. 즉, OpenAI 전용 속성을 제거해야 합니다.
- 솔루션은 `config.json`에서 시맨틱 함수 구성(AI 요청 설정 포함)을 로드하는 것을 계속 지원해야 합니다.
- 개발자에게 좋은 경험을 제공해야 합니다. 예: 타입 안전성, 인텔리센스 등으로 프로그래밍할 수 있어야 합니다.
- AI 서비스 구현자에게 좋은 경험을 제공해야 합니다. 즉, 지원하는 서비스에 적합한 AI 요청 설정 추상화를 정의하는 방법이 명확해야 합니다.
- Semantic Kernel 구현 및 샘플 코드는 여러 AI 서비스와 함께 사용하려는 코드에서 OpenAI 전용 요청 설정을 지정하지 않아야 합니다.
- Semantic Kernel 구현 및 샘플 코드는 구현이 OpenAI 전용인 경우 이를 명확하게 해야 합니다.

## 검토된 옵션

- `dynamic`을 사용하여 요청 설정 전달
- `object`를 사용하여 요청 설정 전달
- 모든 구현이 확장해야 하는 AI 요청 설정 기본 클래스 정의

참고: 제네릭 사용은 Dmytro가 수행한 이전 조사에서 제외되었습니다.

## 결정 결과

**제안:** 모든 구현이 확장해야 하는 AI 요청 설정 기본 클래스를 정의합니다.

## 각 옵션의 장단점

### `dynamic`을 사용하여 요청 설정 전달

`IChatCompletion` 인터페이스는 다음과 같습니다:

```csharp
public interface IChatCompletion : IAIService
{
    ChatHistory CreateNewChat(string? instructions = null);

    Task<IReadOnlyList<IChatResult>> GetChatCompletionsAsync(
        ChatHistory chat,
        dynamic? requestSettings = null,
        CancellationToken cancellationToken = default);

    IAsyncEnumerable<IChatStreamingResult> GetStreamingChatCompletionsAsync(
        ChatHistory chat,
        dynamic? requestSettings = null,
        CancellationToken cancellationToken = default);
}
```

개발자가 시맨틱 함수의 요청 설정을 지정하는 옵션은 다음과 같습니다:

```csharp
// 옵션 1: 익명 타입 사용
await kernel.InvokeSemanticFunctionAsync("Hello AI, what can you do for me?", requestSettings: new { MaxTokens = 256, Temperature = 0.7 });

// 옵션 2: OpenAI 전용 클래스 사용
await kernel.InvokeSemanticFunctionAsync(prompt, requestSettings: new OpenAIRequestSettings() { MaxTokens = 256, Temperature = 0.7 });

// 옵션 3: JSON 페이로드에서 프롬프트 템플릿 구성 로드
string configPayload = @"{
    ""schema"": 1,
    ""description"": ""Say hello to an AI"",
    ""type"": ""completion"",
    ""completion"": {
        ""max_tokens"": 60,
        ""temperature"": 0.5,
        ""top_p"": 0.0,
        ""presence_penalty"": 0.0,
        ""frequency_penalty"": 0.0
    }
}";
var templateConfig = JsonSerializer.Deserialize<PromptTemplateConfig>(configPayload);
var func = kernel.CreateSemanticFunction(prompt, config: templateConfig!, "HelloAI");
await kernel.RunAsync(func);
```

PR: <https://github.com/microsoft/semantic-kernel/pull/2807>

- 좋은 점: SK 추상화에 OpenAI 전용 요청 설정에 대한 참조가 없음
- 중립적: 익명 타입을 사용할 수 있어 여러 AI 서비스에서 지원될 수 있는 속성을 전달할 수 있음. 예: `temperature` 또는 다른 AI 서비스의 속성 조합. 예: `max_tokens` (OpenAI)와 `max_new_tokens` (Oobabooga).
- 나쁜 점: 시맨틱 함수를 생성할 때 무엇을 전달해야 하는지 개발자에게 불분명함
- 나쁜 점: 채팅/텍스트 완성 서비스 구현자에게 무엇을 수용해야 하는지, 서비스 전용 속성을 추가하는 방법이 불분명함
- 나쁜 점: dynamic 인수가 해석되지 않은 코드 경로에 대해 컴파일러 타입 검사가 없어 코드 품질에 영향을 줌. 타입 문제는 `RuntimeBinderException`으로 나타나며 문제 해결이 어려울 수 있음. 반환 타입에 특별한 주의가 필요함. 예: `var` 대신 명시적 타입을 지정해야 `Microsoft.CSharp.RuntimeBinder.RuntimeBinderException : Cannot apply indexing with [] to an expression of type 'object'` 같은 오류를 방지할 수 있음

### `object`를 사용하여 요청 설정 전달

`IChatCompletion` 인터페이스는 다음과 같습니다:

```csharp
public interface IChatCompletion : IAIService
{
    ChatHistory CreateNewChat(string? instructions = null);

    Task<IReadOnlyList<IChatResult>> GetChatCompletionsAsync(
        ChatHistory chat,
        object? requestSettings = null,
        CancellationToken cancellationToken = default);

    IAsyncEnumerable<IChatStreamingResult> GetStreamingChatCompletionsAsync(
        ChatHistory chat,
        object? requestSettings = null,
        CancellationToken cancellationToken = default);
}
```

호출 패턴은 `dynamic`의 경우와 동일합니다. 즉, 익명 타입, AI 서비스 전용 클래스(예: `OpenAIRequestSettings`) 또는 JSON에서 로드합니다.

PR: <https://github.com/microsoft/semantic-kernel/pull/2819>

- 좋은 점: SK 추상화에 OpenAI 전용 요청 설정에 대한 참조가 없음
- 중립적: 익명 타입을 사용할 수 있어 여러 AI 서비스에서 지원될 수 있는 속성을 전달할 수 있음. 예: `temperature` 또는 다른 AI 서비스의 속성 조합. 예: `max_tokens` (OpenAI)와 `max_new_tokens` (Oobabooga).
- 나쁜 점: 시맨틱 함수를 생성할 때 무엇을 전달해야 하는지 개발자에게 불분명함
- 나쁜 점: 채팅/텍스트 완성 서비스 구현자에게 무엇을 수용해야 하는지, 서비스 전용 속성을 추가하는 방법이 불분명함
- 나쁜 점: 타입 검사와 명시적 캐스트를 수행하는 코드가 필요함. `dynamic`의 경우보다 상황이 약간 나음

### 모든 구현이 확장해야 하는 AI 요청 설정 기본 클래스 정의

`IChatCompletion` 인터페이스는 다음과 같습니다:

```csharp
public interface IChatCompletion : IAIService
{
    ChatHistory CreateNewChat(string? instructions = null);

    Task<IReadOnlyList<IChatResult>> GetChatCompletionsAsync(
        ChatHistory chat,
        AIRequestSettings? requestSettings = null,
        CancellationToken cancellationToken = default);

    IAsyncEnumerable<IChatStreamingResult> GetStreamingChatCompletionsAsync(
        ChatHistory chat,
        AIRequestSettings? requestSettings = null,
        CancellationToken cancellationToken = default);
}
```

`AIRequestSettings`는 다음과 같이 정의됩니다:

```csharp
public class AIRequestSettings
{
    /// <summary>
    /// 서비스 식별자.
    /// </summary>
    [JsonPropertyName("service_id")]
    [JsonPropertyOrder(1)]
    public string? ServiceId { get; set; } = null;

    /// <summary>
    /// 추가 속성
    /// </summary>
    [JsonExtensionData]
    public Dictionary<string, object>? ExtensionData { get; set; }
}
```

개발자가 시맨틱 함수의 요청 설정을 지정하는 옵션은 다음과 같습니다:

```csharp
// 옵션 1: 시맨틱 함수를 호출하고 OpenAI 전용 인스턴스를 전달
var result = await kernel.InvokeSemanticFunctionAsync(prompt, requestSettings: new OpenAIRequestSettings() { MaxTokens = 256, Temperature = 0.7 });
Console.WriteLine(result.Result);

// 옵션 2: JSON 페이로드에서 프롬프트 템플릿 구성 로드
string configPayload = @"{
    ""schema"": 1,
    ""description"": ""Say hello to an AI"",
    ""type"": ""completion"",
    ""completion"": {
        ""max_tokens"": 60,
        ""temperature"": 0.5,
        ""top_p"": 0.0,
        ""presence_penalty"": 0.0,
        ""frequency_penalty"": 0.0
        }
}";
var templateConfig = JsonSerializer.Deserialize<PromptTemplateConfig>(configPayload);
var func = kernel.CreateSemanticFunction(prompt, config: templateConfig!, "HelloAI");

await kernel.RunAsync(func);
```

다음 패턴도 사용할 수 있습니다:

```csharp
this._summarizeConversationFunction = kernel.CreateSemanticFunction(
    SemanticFunctionConstants.SummarizeConversationDefinition,
    skillName: nameof(ConversationSummarySkill),
    description: "Given a section of a conversation, summarize conversation.",
    requestSettings: new AIRequestSettings()
    {
        ExtensionData = new Dictionary<string, object>()
        {
            { "Temperature", 0.1 },
            { "TopP", 0.5 },
            { "MaxTokens", MaxTokens }
        }
    });

```

이 패턴의 주의점은, `AIRequestSettings`의 보다 구체적인 구현이 기본 `AIRequestSettings`에서 인스턴스를 하이드레이션하기 위해 JSON 직렬화/역직렬화를 사용한다고 가정할 때, 모든 속성이 기본 JsonConverter에서 지원되는 경우에만 작동한다는 것입니다. 예를 들어:

- `Uri` 속성을 포함하는 `MyAIRequestSettings`가 있다면. `MyAIRequestSettings` 구현은 설정을 올바르게 직렬화/역직렬화하기 위해 URI 변환기를 로드합니다.
- `MyAIRequestSettings`의 설정이 기본 JsonConverter에 의존하는 AI 서비스로 전송되면 `NotSupportedException` 예외가 발생합니다.

PR: <https://github.com/microsoft/semantic-kernel/pull/2829>

- 좋은 점: SK 추상화에 OpenAI 전용 요청 설정에 대한 참조가 없음
- 좋은 점: 시맨틱 함수를 생성할 때 무엇을 전달해야 하는지 개발자에게 명확하며, 어떤 서비스 전용 요청 설정 구현이 존재하는지 쉽게 발견할 수 있음
- 좋은 점: 채팅/텍스트 완성 서비스 구현자에게 무엇을 수용해야 하는지, 기본 추상화를 확장하여 서비스 전용 속성을 추가하는 방법이 명확함
- 중립적: `ExtensionData`를 사용할 수 있어 여러 AI 서비스에서 지원될 수 있는 속성을 전달할 수 있음. 예: `temperature` 또는 다른 AI 서비스의 속성 조합. 예: `max_tokens` (OpenAI)와 `max_new_tokens` (Oobabooga).
