---
# 선택적 요소입니다. 필요 없는 항목은 자유롭게 제거하세요.
status: accepted
contact: sergeymenshykh
date: 2024-04-17
deciders: markwallace, matthewbolanos, rbarreto, dmytrostruk
consulted: 
informed:
---

# 함수 호출 콘텐츠

## 배경 및 문제 설명

현재 SK에서 LLM 함수 호출은 OpenAI 커넥터에 의해서만 지원되며, 함수 호출 모델은 해당 커넥터에 특화되어 있습니다. 이 ARD 작성 시점에, 각각 고유한 함수 호출 모델을 가진 두 개의 새 커넥터가 추가되고 있습니다. 각 새 커넥터가 함수 호출을 위한 고유한 특정 모델 클래스를 도입하는 설계는 커넥터 개발 관점에서 잘 확장되지 않으며, SK 소비자 코드에서 커넥터의 다형적 사용을 허용하지 않습니다.

서비스에 구애받지 않는 함수 호출 모델 클래스가 유용한 또 다른 시나리오는 에이전트가 함수 호출을 서로 전달하는 것입니다. 이 상황에서 OpenAI Assistant API 커넥터/LLM을 사용하는 에이전트가 OpenAI 채팅 완성 API 위에 구축된 다른 에이전트에게 실행을 위한 함수 호출 콘텐츠/요청/모델을 전달할 수 있습니다.

이 ADR은 서비스에 구애받지 않는 함수 호출 모델 클래스의 상위 수준 세부 사항을 설명하며, 하위 수준 세부 사항은 구현 단계에 남겨둡니다. 또한, 이 ADR은 설계의 다양한 측면에 대해 식별된 옵션을 개략적으로 설명합니다.

요구 사항 - https://github.com/microsoft/semantic-kernel/issues/5153

## 결정 동인
1. 커넥터는 서비스에 구애받지 않는 함수 모델 클래스를 사용하여 LLM 함수 호출을 커넥터 호출자에게 전달해야 합니다.
2. 소비자는 서비스에 구애받지 않는 함수 모델 클래스를 사용하여 함수 결과를 커넥터에 다시 전달할 수 있어야 합니다.
3. 모든 기존 함수 호출 동작이 여전히 작동해야 합니다.
4. OpenAI 패키지나 다른 LLM 특정 패키지에 의존하지 않고 서비스에 구애받지 않는 함수 모델 클래스를 사용할 수 있어야 합니다.
5. 함수 호출 및 결과 클래스가 포함된 채팅 히스토리 객체를 직렬화하여 나중에 재수화할 수 있어야 합니다(그리고 잠재적으로 다른 AI 모델로 채팅 히스토리를 실행할 수 있어야 합니다).
6. 에이전트 간에 함수 호출을 전달할 수 있어야 합니다. 다중 에이전트 시나리오에서 한 에이전트가 다른 에이전트가 완료할 함수 호출을 생성할 수 있습니다.
7. 함수 호출을 시뮬레이션할 수 있어야 합니다. 개발자는 자신이 생성한 함수 호출이 포함된 채팅 메시지를 채팅 히스토리 객체에 추가한 다음 모든 LLM으로 실행할 수 있어야 합니다(OpenAI의 경우 함수 호출 ID 시뮬레이션이 필요할 수 있습니다).

## 1. 서비스에 구애받지 않는 함수 호출 모델 클래스
현재 SK는 커넥터 특정 콘텐츠 클래스를 사용하여 함수를 호출하려는 LLM의 의도를 SK 커넥터 호출자에게 전달합니다:
```csharp
IChatCompletionService chatCompletionService = kernel.GetRequiredService<IChatCompletionService>();

ChatHistory chatHistory = new ChatHistory();
chatHistory.AddUserMessage("Given the current time of day and weather, what is the likely color of the sky in Boston?");

// OpenAIChatMessageContent 클래스는 OpenAI 커넥터에 특화됨 - OpenAIChatCompletionService, AzureOpenAIChatCompletionService.
OpenAIChatMessageContent result = (OpenAIChatMessageContent)await chatCompletionService.GetChatMessageContentAsync(chatHistory, settings, kernel);

// ChatCompletionsFunctionToolCall은 OpenAI에 특화된 Azure.AI.OpenAI 패키지에 속함.
List<ChatCompletionsFunctionToolCall> toolCalls = result.ToolCalls.OfType<ChatCompletionsFunctionToolCall>().ToList();

chatHistory.Add(result);
foreach (ChatCompletionsFunctionToolCall toolCall in toolCalls)
{
    string content = kernel.Plugins.TryGetFunctionAndArguments(toolCall, out KernelFunction? function, out KernelArguments? arguments) ?
        JsonSerializer.Serialize((await function.InvokeAsync(kernel, arguments)).GetValue<object>()) :
        "Unable to find function. Please try again!";

    chatHistory.Add(new ChatMessageContent(
        AuthorRole.Tool,
        content,
        metadata: new Dictionary<string, object?>(1) { { OpenAIChatMessageContent.ToolIdProperty, toolCall.Id } }));
}
```

`OpenAIChatMessageContent`와 `ChatCompletionsFunctionToolCall` 클래스 모두 OpenAI에 특화되어 있으며 OpenAI가 아닌 커넥터에서는 사용할 수 없습니다. 또한, LLM 벤더 특정 클래스를 사용하면 커넥터 호출자의 코드가 복잡해지고 커넥터를 다형적으로 작업하는 것이 불가능해집니다 - `IChatCompletionService` 인터페이스를 통해 커넥터를 참조하면서 구현을 교환할 수 있는 능력.

이러한 문제를 해결하기 위해, 서비스에 구애받지 않는 방식으로 함수를 호출하려는 LLM의 의도를 호출자에게 전달하고 함수 호출 결과를 LLM에 다시 반환할 수 있는 메커니즘이 필요합니다. 또한, 이 메커니즘은 LLM이 함수 호출을 요청하면서 단일 응답에서 다른 콘텐츠 유형도 반환하는 잠재적 멀티모달 사례를 지원할 수 있을 만큼 확장 가능해야 합니다.

SK 채팅 완성 모델 클래스가 이미 `ChatMessageContent.Items` 컬렉션을 통해 멀티모달 시나리오를 지원한다는 점을 고려하면, 이 컬렉션은 함수 호출 시나리오에도 활용할 수 있습니다. 커넥터는 LLM 함수 호출을 서비스에 구애받지 않는 함수 콘텐츠 모델 클래스에 매핑하고 items 컬렉션에 추가해야 합니다. 한편, 커넥터 호출자는 함수를 실행하고 items 컬렉션을 통해 실행 결과를 다시 전달합니다.

서비스에 구애받지 않는 함수 콘텐츠 모델 클래스에 대한 몇 가지 옵션이 아래에서 검토됩니다.

### 옵션 1.1 - 함수 호출(요청)과 함수 결과 모두를 나타내는 FunctionCallContent
이 옵션은 함수 호출과 함수 결과 모두를 전달하기 위한 하나의 서비스에 구애받지 않는 모델 클래스 `FunctionCallContent`를 갖는 것을 가정합니다:
```csharp
class FunctionCallContent : KernelContent
{
    public string? Id {get; private set;}
    public string? PluginName {get; private set;}
    public string FunctionName {get; private set;}
    public KernelArguments? Arguments {get; private set; }
    public object?/FunctionResult/string? Result {get; private set;} // 속성의 유형은 아래에서 설명합니다.
    
    public string GetFullyQualifiedName(string functionNameSeparator = "-") {...}

    public Task<FunctionResult> InvokeAsync(Kernel kernel, CancellationToken cancellationToken = default)
    {
        // 1. kernel.Plugins 컬렉션에서 플러그인/함수를 검색합니다.
        // 2. Arguments를 역직렬화하여 KernelArguments를 생성합니다.
        // 3. 함수를 호출합니다.
    }
}
```

**장점**:
- 함수 호출과 함수 결과 모두를 나타내는 하나의 모델 클래스.

**단점**:
- 커넥터가 콘텐츠가 함수 호출인지 함수 결과인지를 채팅 히스토리에서 부모 `ChatMessageContent`의 역할을 분석하여 결정해야 합니다. 유형 자체가 목적을 전달하지 않기 때문입니다.
  * 함수 결과를 커넥터에 전달하기 위한 특정 역할(AuthorRole.Tool?)을 가진 채팅 메시지를 정의하는 프로토콜이 필요하므로 이것이 단점이 아닐 수 있습니다. 자세한 내용은 이 ADR에서 아래에서 논의됩니다.

### 옵션 1.2 - 함수 호출을 나타내는 FunctionCallContent와 함수 결과를 나타내는 FunctionResultContent
이 옵션은 두 개의 모델 클래스를 제안합니다 - 커넥터 호출자에게 함수 호출을 전달하기 위한 `FunctionCallContent`:
```csharp
class FunctionCallContent : KernelContent
{
    public string? Id {get;}
    public string? PluginName {get;}
    public string FunctionName {get;}
    public KernelArguments? Arguments {get;}
    public Exception? Exception {get; init;}

    public Task<FunctionResultContent> InvokeAsync(Kernel kernel,CancellationToken cancellationToken = default)
    {
        // 1. kernel.Plugins 컬렉션에서 플러그인/함수를 검색합니다.
        // 2. Arguments를 역직렬화하여 KernelArguments를 생성합니다.
        // 3. 함수를 호출합니다.
    }

    public static IEnumerable<FunctionCallContent> GetFunctionCalls(ChatMessageContent messageContent)
    {
        // <see cref="ChatMessageContent.Items"/> 컬렉션을 통해 제공된 함수 호출 목록을 반환합니다.
    }
}
```

그리고 - 함수 결과를 커넥터에 다시 전달하기 위한 `FunctionResultContent`:
```csharp
class FunctionResultContent : KernelContent
{
    public string? Id {get; private set;}
    public string? PluginName {get; private set;}
    public string? FunctionName {get; private set;}

    public object?/FunctionResult/string? Result {get; set;}

    public ChatMessageContent ToChatMessage()
    {
        // <see cref="ChatMessageContent"/>를 생성하고 현재 클래스 인스턴스를 <see cref="ChatMessageContent.Items"/> 컬렉션에 추가합니다.
    }
}
```

**장점**:
- 이전 옵션에 비해 명시적인 모델로, 부모 `ChatMessageContent` 메시지의 역할에 관계없이 호출자가 콘텐츠의 의도를 명확하게 선언할 수 있습니다.
  * 위 옵션의 단점과 유사하게, 함수 결과를 커넥터에 전달하기 위한 채팅 메시지의 역할을 정의하는 프로토콜이 필요하므로 이것이 장점이 아닐 수 있습니다.

**단점**:
- 하나의 추가 콘텐츠 클래스.

### 커넥터 호출자 코드 예시:
```csharp
// GetChatMessageContentAsync 메서드는 하나의 선택만 반환합니다. 그러나 여러 선택을 반환할 수 있는 GetChatMessageContentsAsync 메서드가 있습니다.
ChatMessageContent messageContent = await completionService.GetChatMessageContentAsync(chatHistory, settings, kernel);
chatHistory.Add(messageContent); // 함수 호출이 포함된 원본 채팅 메시지 콘텐츠를 채팅 히스토리에 추가

IEnumerable<FunctionCallContent> functionCalls = FunctionCallContent.GetFunctionCalls(messageContent); // 함수 호출 목록 가져오기.
// 대안: IEnumerable<FunctionCallContent> functionCalls = messageContent.Items.OfType<FunctionCallContent>();

// 요청된 함수 호출을 반복하며 호출합니다.
foreach (FunctionCallContent functionCall in functionCalls)
{
    FunctionResultContent? result = null;

    try
    {
        result = await functionCall.InvokeAsync(kernel); // `Kernel.Plugins` 컬렉션에서 함수 호출을 해결하고 호출합니다.
    }
    catch(Exception ex)
    {
        chatHistory.Add(new FunctionResultContent(functionCall, ex).ToChatMessage());
        // 또는
        //string message = "LLM이 추론할 수 있는 오류 세부 사항.";
        //chatHistory.Add(new FunctionResultContent(functionCall, message).ToChatMessageContent());
        
        continue;
    }
    
    chatHistory.Add(result.ToChatMessage());
    // 또는 chatHistory.Add(new ChatMessageContent(AuthorRole.Tool, new ChatMessageContentItemCollection() { result }));
}

// 함수 호출과 함수 결과가 포함된 채팅 히스토리를 LLM에 보내 최종 응답을 받습니다
messageContent = await completionService.GetChatMessageContentAsync(chatHistory, settings, kernel);
```

이 설계는 호출자가 각 함수 결과 콘텐츠에 대해 채팅 메시지 인스턴스를 생성할 것을 요구하지 않습니다. 대신, 단일 채팅 메시지 인스턴스를 통해 여러 함수 결과 콘텐츠 인스턴스를 커넥터에 보낼 수 있습니다:
```csharp
ChatMessageContent messageContent = await completionService.GetChatMessageContentAsync(chatHistory, settings, kernel);
chatHistory.Add(messageContent); // 함수 호출이 포함된 원본 채팅 메시지 콘텐츠를 채팅 히스토리에 추가.

IEnumerable<FunctionCallContent> functionCalls = FunctionCallContent.GetFunctionCalls(messageContent); // 함수 호출 목록 가져오기.

ChatMessageContentItemCollection items = new ChatMessageContentItemCollection();

// 요청된 함수 호출을 반복하며 호출합니다
foreach (FunctionCallContent functionCall in functionCalls)
{
    FunctionResultContent result = await functionCall.InvokeAsync(kernel);

    items.Add(result);
}

chatHistory.Add(new ChatMessageContent(AuthorRole.Tool, items);

// 함수 호출과 함수 결과가 포함된 채팅 히스토리를 LLM에 보내 최종 응답을 받습니다
messageContent = await completionService.GetChatMessageContentAsync(chatHistory, settings, kernel);
```

### 결정 결과
명시적 특성으로 인해 옵션 1.2가 선택되었습니다.

## 2. 채팅 완성 커넥터를 위한 함수 호출 프로토콜
서로 다른 채팅 완성 커넥터는 커넥터 특정 역할을 가진 메시지를 통해 호출자에게 함수 호출을 전달하고 함수 결과를 다시 받을 수 있습니다. 예를 들어, `{Azure}OpenAIChatCompletionService` 커넥터는 `Assistant` 역할의 메시지를 사용하여 커넥터 호출자에게 함수 호출을 전달하고, 호출자가 `Tool` 역할의 메시지를 통해 함수 결과를 반환할 것을 기대합니다.

커넥터가 반환하는 함수 호출 메시지의 역할은 호출자에게 중요하지 않습니다. 응답 메시지의 역할에 관계없이 `GetFunctionCalls` 메서드를 호출하여 함수 목록을 쉽게 얻을 수 있기 때문입니다.

```csharp
ChatMessageContent messageContent = await completionService.GetChatMessageContentAsync(chatHistory, settings, kernel);

IEnumerable<FunctionCallContent> functionCalls = FunctionCallContent.GetFunctionCalls(); // messageContent에 함수 호출이 포함되어 있으면 역할에 관계없이 함수 호출 목록을 반환합니다.
```

그러나 커넥터에 함수 결과를 다시 보내기 위한 하나의 커넥터에 구애받지 않는 역할만 있는 것이 커넥터의 다형적 사용에 중요합니다. 이렇게 하면 호출자가 다음과 같은 코드를 작성할 수 있습니다:

 ```csharp
 ...
IEnumerable<FunctionCallContent> functionCalls = FunctionCallContent.GetFunctionCalls();

foreach (FunctionCallContent functionCall in functionCalls)
{
    FunctionResultContent result = await functionCall.InvokeAsync(kernel);

    chatHistory.Add(result.ToChatMessage());
}
...
```

그리고 다음과 같은 코드를 피할 수 있습니다:

```csharp
IChatCompletionService chatCompletionService = new();
...
IEnumerable<FunctionCallContent> functionCalls = FunctionCallContent.GetFunctionCalls();

foreach (FunctionCallContent functionCall in functionCalls)
{
    FunctionResultContent result = await functionCall.InvokeAsync(kernel);

    // 단일 커넥터에 구애받지 않는 역할 대신 커넥터 특정 역할을 사용하면 커넥터의 다형적 사용이 방지되고 호출자가 if/else 블록을 작성해야 합니다.
    if(chatCompletionService is OpenAIChatCompletionService || chatCompletionService is AzureOpenAIChatCompletionService)
    {
        chatHistory.Add(new ChatMessageContent(AuthorRole.Tool, new ChatMessageContentItemCollection() { result });
    }
    else if(chatCompletionService is AnotherCompletionService)
    {
        chatHistory.Add(new ChatMessageContent(AuthorRole.Function, new ChatMessageContentItemCollection() { result });
    }
    else if(chatCompletionService is SomeOtherCompletionService)
    {
        chatHistory.Add(new ChatMessageContent(AuthorRole.ServiceSpecificRole, new ChatMessageContentItemCollection() { result });
    }
}
...
```

### 결정 결과
잘 알려져 있고, 개념적으로 함수 결과뿐만 아니라 SK가 향후 지원해야 할 다른 도구도 나타낼 수 있는 `AuthorRole.Tool` 역할로 결정되었습니다.

## 3. FunctionResultContent.Result 속성의 유형:
`FunctionResultContent.Result` 속성에 사용할 수 있는 몇 가지 데이터 유형이 있습니다. 문제의 데이터 유형은 다음 시나리오를 허용해야 합니다:
- 함수 결과 콘텐츠가 포함된 채팅 히스토리를 직렬화하고 나중에 필요할 때 재수화할 수 있도록 직렬화/역직렬화가 가능해야 합니다.
- 원래 예외를 보내거나 문제를 설명하는 문자열을 LLM에 보내 함수 실행 실패를 전달할 수 있어야 합니다.

지금까지 세 가지 잠재적 데이터 유형이 식별되었습니다: object, string, FunctionResult.

### 옵션 3.1 - object
```csharp
class FunctionResultContent : KernelContent
{
    // 다른 멤버는 생략
    public object? Result {get; set;}
}
```

이 옵션은 JsonSerializer에서 기본적으로 지원하지 않는 유형으로 표현된 함수 결과가 포함된 채팅 히스토리의 {역}직렬화를 위해 JSON 컨버터/리졸버를 사용해야 할 수 있습니다.

**장점**:
- 직렬화는 커넥터에 의해 수행되지만, 필요한 경우 호출자도 수행할 수 있습니다.
- 호출자는 필요한 경우 함수 결과와 함께 추가 데이터를 제공할 수 있습니다.
- 호출자는 함수 실행 실패를 전달하는 방법을 제어할 수 있습니다: Exception 클래스의 인스턴스를 전달하거나 LLM에 문제에 대한 문자열 설명을 제공합니다.

**단점**:


### 옵션 3.2 - string (현재 구현)
```csharp
class FunctionResultContent : KernelContent
{
    // 다른 멤버는 생략
    public string? Result {get; set;}
}
```
**장점**:
- 채팅 히스토리 {역}직렬화에 컨버터가 필요 없습니다.
- 호출자는 필요한 경우 함수 결과와 함께 추가 데이터를 제공할 수 있습니다.
- 호출자는 함수 실행 실패를 전달하는 방법을 제어할 수 있습니다: 직렬화된 예외, 메시지 또는 LLM에 문제에 대한 문자열 설명을 제공합니다.

**단점**:
- 직렬화가 호출자에 의해 수행됩니다. 채팅 완성 서비스의 다형적 사용에 문제가 될 수 있습니다.

### 옵션 3.3 - FunctionResult
```csharp
class FunctionResultContent : KernelContent
{
    // 다른 멤버는 생략
    public FunctionResult? Result {get;set;}

    public Exception? Exception {get;set}
    또는 
    public object? Error { get; set; } // Exception 클래스의 인스턴스 또는 문제를 설명하는 문자열을 포함할 수 있습니다.
}
```
**장점**:
- FunctionResult SK 도메인 클래스 사용.

**단점**:
- 추가 Exception/Error 속성 없이는 커넥터/LLM에 예외를 전달할 수 없습니다.
- `FunctionResult`는 현재 {역}직렬화가 불가능합니다:
  * `FunctionResult.ValueType` 속성은 `Type` 유형을 가지며, 이는 위험하다고 간주되어 JsonSerializer에서 기본적으로 직렬화할 수 없습니다.
  * `KernelReturnParameterMetadata.ParameterType` 및 `KernelParameterMetadata.ParameterType` 속성도 `Type` 유형으로 동일하게 적용됩니다.
  * `FunctionResult.Function` 속성은 역직렬화할 수 없으며 [JsonIgnore] 특성으로 표시해야 합니다.
    * 역직렬화를 위해 새 생성자 ctr(object? value = null, IReadOnlyDictionary<string, object?>? metadata = null)을 추가해야 합니다.
    * `FunctionResult.Function` 속성은 nullable이어야 합니다. 필터가 `Function` 속성을 노출하는 `FunctionFilterContext` 클래스를 사용하므로 함수 필터 사용자에게 브레이킹 변경이 될 수 있습니다.

### 옵션 3.4 - FunctionResult: KernelContent
참고: 이 옵션은 이 ADR의 두 번째 검토 라운드에서 제안되었습니다.

이 옵션은 `FunctionResult` 클래스를 `KernelContent` 클래스의 파생 클래스로 만드는 것을 제안합니다:
```csharp
public class FunctionResult : KernelContent
{
    ....
}
```
따라서 함수 결과 콘텐츠를 나타내기 위한 별도의 `FunctionResultContent` 클래스 대신, `FunctionResult` 클래스가 `KernelContent` 클래스를 상속하여 콘텐츠 자체가 됩니다. 결과적으로 `KernelFunction.InvokeAsync` 메서드가 반환하는 함수 결과를 `ChatMessageContent.Items` 컬렉션에 직접 추가할 수 있습니다:
```csharp
foreach (FunctionCallContent functionCall in functionCalls)
{
    FunctionResult result = await functionCall.InvokeAsync(kernel);

    chatHistory.Add(new ChatMessageContent(AuthorRole.Tool, new ChatMessageContentItemCollection { result }));
    // 대신
    chatHistory.Add(new ChatMessageContent(AuthorRole.Tool, new ChatMessageContentItemCollection { new FunctionResultContent(functionCall, result) }));
    
    // 물론, 추가 인스턴스/확장 메서드로 구문을 단순화할 수 있습니다
    chatHistory.AddFunctionResultMessage(result); // ChatHistory 클래스의 새 AddFunctionResultMessage 확장 메서드 사용
}
```

질문:
- 함수 결과와 함께 원본 `FunctionCallContent`를 커넥터에 어떻게 전달할 것인가. 현재로서는 필요한지 여부가 명확하지 않습니다. 현재 근거는 일부 모델이 함수 결과와 함께 인수와 같은 원본 함수 호출의 속성을 LLM에 다시 전달할 것을 기대할 수 있다는 것입니다. 원본 함수 호출은 필요한 경우 커넥터가 채팅 히스토리에서 찾을 수 있다는 주장이 있습니다. 그러나 토큰 절약, 환각 감소 등을 위해 채팅 히스토리가 잘릴 수 있으므로 항상 가능하지 않을 수 있다는 반론이 있습니다.
- 커넥터에 함수 ID를 어떻게 전달할 것인가?
- 커넥터에 예외를 어떻게 전달할 것인가? `KernelFunction.InvokeAsync` 메서드에 의해 항상 할당될 `Exception` 속성을 `FunctionResult` 클래스에 추가하는 것이 제안되었습니다. 그러나 이 변경은 계약이 충족되면 함수를 실행하고 계약이 충족되지 않으면 예외를 던져야 하는 C# 함수 호출 시맨틱을 깨뜨립니다.
- `FunctionResult`가 `KernelContent` 클래스를 상속하여 비스트리밍 콘텐츠가 되면, 나중에 필요할 때 `StreamingKernelContent` 클래스가 나타내는 스트리밍 콘텐츠 기능을 `FunctionResult`가 어떻게 나타낼 수 있는가? C#은 다중 상속을 지원하지 않습니다.

**장점**
- `FunctionResult` 클래스가 (비스트리밍) 콘텐츠 자체가 되어 콘텐츠가 기대되는 모든 곳에 전달할 수 있습니다.
- 추가 `FunctionResultContent` 클래스가 필요 없습니다.
  
**단점**
- `FunctionResult`와 `KernelContent` 클래스 간의 불필요한 결합이 각각이 독립적으로 발전하는 것을 방해하는 제한 요소가 될 수 있습니다.
- `FunctionResult.Function` 속성을 직렬화 가능하도록 nullable로 변경하거나, 함수 인스턴스 자체 없이 함수 스키마를 {역}직렬화하기 위해 커스텀 직렬화를 적용해야 합니다.
- LLM이 요구하는 함수 ID를 나타내기 위해 `FunctionResult` 클래스에 `Id` 속성을 추가해야 합니다.

### 결정 결과
원래는 다른 두 옵션에 비해 가장 유연한 옵션 3.1로 결정되었습니다. 커넥터가 함수 스키마를 가져와야 하는 경우, 커넥터에서 사용 가능한 kernel.Plugins 컬렉션에서 쉽게 얻을 수 있습니다. 함수 결과 메타데이터는 `KernelContent.Metadata` 속성을 통해 커넥터에 전달할 수 있습니다.
그러나 이 ADR의 두 번째 검토 라운드에서 옵션 3.4가 탐색을 위해 제안되었습니다. 최종적으로, 옵션 3.4의 프로토타이핑 후 단점으로 인해 옵션 3.1로 돌아가기로 결정되었습니다.

## 4. 시뮬레이션된 함수
모델의 훈련으로 인해 LLM이 프롬프트에 제공된 데이터를 무시하는 경우가 있습니다. 그러나 모델은 함수 결과를 통해 동일한 데이터가 제공되면 해당 데이터로 작업할 수 있습니다.

시뮬레이션된 함수를 모델링하는 몇 가지 방법이 있습니다:

### 옵션 4.1 - SemanticFunction으로서의 시뮬레이션된 함수
```csharp
...

ChatMessageContent messageContent = await completionService.GetChatMessageContentAsync(chatHistory, settings, kernel);

// 시뮬레이션된 함수 호출
FunctionCallContent simulatedFunctionCall = new FunctionCallContent(name: "weather-alert", id: "call_123");
messageContent.Items.Add(simulatedFunctionCall); // 커넥터 응답 메시지에 시뮬레이션된 함수 호출 추가

chatHistory.Add(messageContent);

// SK 함수 생성 및 호출
KernelFunction simulatedFunction = KernelFunctionFactory.CreateFromMethod(() => "A Tornado Watch has been issued, with potential for severe ..... Stay informed and follow safety instructions from authorities.");
FunctionResult simulatedFunctionResult = await simulatedFunction.InvokeAsync(kernel);

chatHistory.Add(new ChatMessageContent(AuthorRole.Tool, new ChatMessageContentItemCollection() { new FunctionResultContent(simulatedFunctionCall, simulatedFunctionResult) }));

messageContent = await completionService.GetChatMessageContentAsync(chatHistory, settings, kernel);

...
```
**장점**:
- 호출자가 시뮬레이션된 함수를 호출할 때 SK 함수 필터/훅이 트리거될 수 있습니다.
 
**단점**:
- 다른 옵션만큼 가볍지 않습니다.

### 옵션 4.2 - 시뮬레이션된 함수로서의 object
```csharp
...

ChatMessageContent messageContent = await completionService.GetChatMessageContentAsync(chatHistory, settings, kernel);

// 시뮬레이션된 함수
FunctionCallContent simulatedFunctionCall = new FunctionCallContent(name: "weather-alert", id: "call_123");
messageContent.Items.Add(simulatedFunctionCall);

chatHistory.Add(messageContent);

// 시뮬레이션된 결과 생성
string simulatedFunctionResult = "A Tornado Watch has been issued, with potential for severe ..... Stay informed and follow safety instructions from authorities."

//또는

WeatherAlert simulatedFunctionResult = new WeatherAlert { Id = "34SD7RTYE4", Text = "A Tornado Watch has been issued, with potential for severe ..... Stay informed and follow safety instructions from authorities." };

chatHistory.Add(new ChatMessageContent(AuthorRole.Tool, new ChatMessageContentItemCollection() { new FunctionResultContent(simulatedFunctionCall, simulatedFunctionResult) }));

messageContent = await completionService.GetChatMessageContentAsync(chatHistory, settings, kernel);

...
```
**장점**:
- SK 함수 생성 및 실행이 필요 없으므로 이전 옵션에 비해 더 가벼운 옵션.

**단점**:
- 호출자가 시뮬레이션된 함수를 호출할 때 SK 함수 필터/훅이 트리거될 수 없습니다.

### 결정 결과
제공된 옵션들은 상호 배타적이지 않으며, 시나리오에 따라 각각 사용할 수 있습니다.

## 5. 스트리밍
커넥터의 스트리밍 API를 위한 서비스에 구애받지 않는 함수 호출 모델의 설계는 위에서 설명한 비스트리밍 설계와 유사해야 합니다.

스트리밍 API는 비스트리밍 API와 콘텐츠가 한꺼번에가 아닌 청크로 반환된다는 점에서 다릅니다. 예를 들어, OpenAI 커넥터는 현재 두 개의 청크로 함수 호출을 반환합니다: 함수 ID와 이름은 첫 번째 청크에, 함수 인수는 후속 청크에서 전송됩니다. 또한, LLM은 동일한 응답에서 둘 이상의 함수에 대한 함수 호출을 스트리밍할 수 있습니다. 예를 들어, 커넥터가 스트리밍하는 첫 번째 청크에는 첫 번째 함수의 ID와 이름이, 다음 청크에는 두 번째 함수의 ID와 이름이 포함될 수 있습니다.

이는 스트리밍 특성을 더 자연스럽게 수용하기 위해 스트리밍 API의 함수 호출 모델 설계에서 약간의 편차가 필요합니다. 상당한 편차가 있는 경우, 세부 사항을 설명하는 별도의 ADR이 작성됩니다.
