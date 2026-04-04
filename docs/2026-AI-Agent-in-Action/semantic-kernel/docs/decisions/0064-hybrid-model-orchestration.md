---
status: accepted
contact: sergeymenshykh
date: 2025-02-05
deciders: dmytrostruk, markwallace, rbarreto, sergeymenshykh, westey-m,
---

# 하이브리드 모델 오케스트레이션

## 맥락과 문제 설명
끊임없이 등장하고 개선되는 로컬 및 클라우드 기반 모델과 로컬 디바이스의 NPU에서 실행되는 로컬 AI 모델 활용에 대한 수요 증가를 고려하면,
AI 기반 애플리케이션은 최상의 AI 사용자 경험을 달성하기 위해 로컬 및 클라우드 모델 모두를 추론에 효과적이고 원활하게 활용할 수 있어야 합니다.

## 결정 동인

1. 모델 오케스트레이션 레이어는 간단하고 확장 가능해야 합니다.
2. 모델 오케스트레이션 레이어의 클라이언트 코드는 기저의 복잡성을 인식하거나 처리할 필요가 없어야 합니다.
3. 모델 오케스트레이션 레이어는 당면한 작업에 가장 적합한 모델을 선택하기 위한 다양한 전략을 허용해야 합니다.

## 검토한 구현 옵션

다음 옵션들은 모델 오케스트레이션 레이어를 구현하는 몇 가지 방법을 검토합니다.

### 옵션 1: 오케스트레이션 전략별 IChatClient 구현

이 옵션은 모델 오케스트레이션 레이어를 구현하는 간단하고 직관적인 접근 방식을 제시합니다. 각 전략은 IChatClient 인터페이스의 별도 구현으로 만들어집니다.

예를 들어, 첫 번째로 설정된 채팅 클라이언트를 추론에 사용하고 AI 모델이 사용 불가능한 경우 다음 클라이언트로 대체하는 폴백 전략은 다음과 같이 구현할 수 있습니다:
```csharp
public sealed class FallbackChatClient : IChatClient
{
    private readonly IChatClient[] _clients;

    public FallbackChatClient(params IChatClient[] clients)
    {
        this._clients = clients;
    }

    public Task<Microsoft.Extensions.AI.ChatCompletion> CompleteAsync(IList<ChatMessage> chatMessages, ChatOptions? options = null, CancellationToken cancellationToken = default)
    {
        foreach (var client in this._clients)
        {
            try
            {
                return client.CompleteAsync(chatMessages, options, cancellationToken);
            }
            catch (HttpRequestException ex)
            {
                if (ex.StatusCode >= 500)
                {
                    // 다음 클라이언트를 시도합니다
                    continue;
                }

                throw;
            }
        }
    }

    public IAsyncEnumerable<StreamingChatCompletionUpdate> CompleteStreamingAsync(IList<ChatMessage> chatMessages, ChatOptions? options = null, CancellationToken cancellationToken = default)
    {
        ...
    }

    public void Dispose() { /*클라이언트를 여기서 dispose할 수 없습니다. 상위 스택에서 사용될 수 있기 때문입니다*/ }

    public ChatClientMetadata Metadata => new ChatClientMetadata();

    public object? GetService(Type serviceType, object? serviceKey = null) => null;
}
```

지연시간 기반 또는 토큰 기반 전략과 같은 다른 오케스트레이션 전략도 유사한 방식으로 구현할 수 있습니다: IChatClient 인터페이스를 구현하는 클래스와 해당 채팅 클라이언트 선택 전략.

장점:
- 새로운 추상화가 필요하지 않습니다.
- 간단하고 직관적인 구현입니다.
- 대부분의 사용 사례에 충분할 수 있습니다.

### 옵션 2: 오케스트레이션 전략별 채팅 완성 핸들러를 가진 HybridChatClient 클래스

이 옵션은 IChatClient 인터페이스를 구현하고 선택 루틴을 추상 ChatCompletionHandler 클래스로 표현되는 제공된 핸들러에 위임하는 HybridChatClient 클래스를 도입합니다:
```csharp
public sealed class HybridChatClient : IChatClient
{
    private readonly IChatClient[] _chatClients;
    private readonly ChatCompletionHandler _handler;
    private readonly Kernel? _kernel;

    public HybridChatClient(IChatClient[] chatClients, ChatCompletionHandler handler, Kernel? kernel = null)
    {
        this._chatClients = chatClients;
        this._handler = handler;
        this._kernel = kernel;
    }

    public Task<Extensions.AI.ChatCompletion> CompleteAsync(IList<ChatMessage> chatMessages, ChatOptions? options = null, CancellationToken cancellationToken = default)
    {
        return this._handler.CompleteAsync(
            new ChatCompletionHandlerContext
            {
                ChatMessages = chatMessages,
                Options = options,
                ChatClients = this._chatClients.ToDictionary(c => c, c => (CompletionContext?)null),
                Kernel = this._kernel,
            }, cancellationToken);
    }

    public IAsyncEnumerable<StreamingChatCompletionUpdate> CompleteStreamingAsync(IList<ChatMessage> chatMessages, ChatOptions? options = null, CancellationToken cancellationToken = default)
    {
        ...
    }

    ...
}

public abstract class ChatCompletionHandler
{
    public abstract Task<Extensions.AI.ChatCompletion> CompleteAsync(ChatCompletionHandlerContext context, CancellationToken cancellationToken = default);

    public abstract IAsyncEnumerable<StreamingChatCompletionUpdate> CompleteStreamingAsync(ChatCompletionHandlerContext context, CancellationToken cancellationToken = default);
}
```

HybridChatClient 클래스는 채팅 클라이언트 목록, 채팅 메시지, 옵션, Kernel 인스턴스를 포함하는 ChatCompletionHandlerContext 클래스를 통해 핸들러에 필요한 모든 정보를 전달합니다.
```csharp
public class ChatCompletionHandlerContext
{
    public IDictionary<IChatClient, CompletionContext?> ChatClients { get; init; }

    public IList<ChatMessage> ChatMessages { get; init; }

    public ChatOptions? Options { get; init; }

    public Kernel? Kernel { get; init; }
}
```

이전 옵션에서 보여준 폴백 전략은 다음과 같은 핸들러로 구현할 수 있습니다:
```csharp
public class FallbackChatCompletionHandler : ChatCompletionHandler
{
    public override async Task<Extensions.AI.ChatCompletion> CompleteAsync(ChatCompletionHandlerContext context, CancellationToken cancellationToken = default)
    {
        for (int i = 0; i < context.ChatClients.Count; i++)
        {
            var chatClient = context.ChatClients.ElementAt(i).Key;

            try
            {
                return client.CompleteAsync(chatMessages, options, cancellationToken);
            }
            catch (HttpRequestException ex)
            {
                if (ex.StatusCode >= 500)
                {
                    // 다음 클라이언트를 시도합니다
                    continue;
                }

                throw;
            }
        }

        throw new InvalidOperationException("No client provided for chat completion.");
    }

    public override async IAsyncEnumerable<StreamingChatCompletionUpdate> CompleteStreamingAsync(ChatCompletionHandlerContext context, CancellationToken cancellationToken = default)
    {
        ...
    }
}
```

호출자 코드는 다음과 같습니다:
```csharp
IChatClient onnxChatClient = new OnnxChatClient(...);

IChatClient openAIChatClient = new OpenAIChatClient(...);

// 첫 번째 클라이언트를 시도하고 실패하면 다음 클라이언트로 대체합니다
FallbackChatCompletionHandler handler = new FallbackChatCompletionHandler(...);

IChatClient hybridChatClient = new HybridChatClient([onnxChatClient, openAIChatClient], handler);

...

var result = await hybridChatClient.CompleteAsync("Do I need an umbrella?", ...);
```

핸들러는 체이닝하여 더 복잡한 시나리오를 만들 수 있으며, 핸들러가 일부 전처리를 수행한 다음 확장된 채팅 클라이언트 목록과 함께 다른 핸들러에 호출을 위임합니다.

예를 들어, 첫 번째 핸들러는 클라우드 모델이 민감한 데이터에 대한 접근을 요청했음을 식별하고 이를 처리하기 위해 로컬 모델에 호출 처리를 위임합니다.

```csharp
IChatClient onnxChatClient = new OnnxChatClient(...);

IChatClient llamaChatClient = new LlamaChatClient(...);

IChatClient openAIChatClient = new OpenAIChatClient(...);

// 첫 번째 클라이언트를 시도하고 실패하면 다음 클라이언트로 대체합니다
FallbackChatCompletionHandler fallbackHandler = new FallbackChatCompletionHandler(...);
  
// 요청에 민감한 데이터가 포함되어 있는지 확인하고, 민감한 데이터를 처리할 수 있는 클라이언트를 식별하여 다음 핸들러에 호출 처리를 위임합니다.
SensitiveDataHandler sensitiveDataHandler = new SensitiveDataHandler(fallbackHandler);

IChatClient hybridChatClient = new HybridChatClient(new[] { onnxChatClient, llamaChatClient, openAIChatClient }, sensitiveDataHandler);
  
var result = await hybridChatClient.CompleteAsync("Do I need an umbrella?", ...);
```

복잡한 오케스트레이션 시나리오의 예:

| 첫 번째 핸들러 | 두 번째 핸들러 | 시나리오 설명 |
|---------------------------------------|--------------------------------|---------------------------------------------------------------------------|
| InputTokenThresholdEvaluationHandler  | FastestChatCompletionHandler   | 프롬프트의 입력 토큰 크기와 각 모델의 최소/최대 토큰 용량을 기반으로 모델을 식별한 다음, 가장 빠른 모델의 응답을 반환합니다. |
| InputTokenThresholdEvaluationHandler  | RelevancyChatCompletionHandler | 프롬프트의 입력 토큰 크기와 각 모델의 최소/최대 토큰 용량을 기반으로 모델을 식별한 다음, 가장 관련성 높은 응답을 반환합니다. |
| InputTokenThresholdEvaluationHandler  | FallbackChatCompletionHandler  | 프롬프트의 입력 토큰 크기와 각 모델의 최소/최대 토큰 용량을 기반으로 모델을 식별한 다음, 첫 번째 사용 가능한 모델의 응답을 반환합니다. |
| SensitiveDataRoutingHandler           | FastestChatCompletionHandler   | 데이터 민감도를 기반으로 모델을 식별한 다음, 가장 빠른 모델의 응답을 반환합니다. |
| SensitiveDataRoutingHandler           | RelevancyChatCompletionHandler | 데이터 민감도를 기반으로 모델을 식별한 다음, 가장 관련성 높은 응답을 반환합니다. |
| SensitiveDataRoutingHandler           | FallbackChatCompletionHandler  | 데이터 민감도를 기반으로 모델을 식별한 다음, 첫 번째 사용 가능한 모델의 응답을 반환합니다. |

장점:
- 동일한 핸들러를 재사용하여 다양한 복합 오케스트레이션 전략을 만들 수 있습니다.

단점:
- 이전 옵션보다 더 많은 새로운 추상화와 컴포넌트가 필요합니다: 컨텍스트 클래스와 다음 핸들러 처리를 위한 코드.

<br/>

이 옵션을 보여주는 POC는 [여기](https://github.com/microsoft/semantic-kernel/pull/10412)에서 찾을 수 있습니다.

### 옵션 3: 기존 IAIServiceSelector 인터페이스 구현

Semantic Kernel에는 AI 서비스의 동적 선택을 가능하게 하는 메커니즘이 있습니다:

```csharp
public interface IAIServiceSelector
{
    bool TrySelectAIService<T>(
        Kernel kernel,
        KernelFunction function,
        KernelArguments arguments,
        [NotNullWhen(true)] out T? service,
        out PromptExecutionSettings? serviceSettings) where T : class, IAIService;
}
```

그러나 이 메커니즘은 항상 사용 가능하지 않을 수 있는 특정 컨텍스트(커널, 함수, 인수)를 필요로 합니다.
또한 Microsoft.Extensions.AI에서 IChatClient 인터페이스를 구현하는 것과 같은 모든 AI 서비스와 호환되지 않을 수 있는 IAIService 인터페이스의 구현에서만 작동합니다.

또한 이 메커니즘은 AI 서비스의 가용성, 지연시간 등을 결정하기 위해 먼저 프롬프팅해야 하는 오케스트레이션 시나리오에서는 사용할 수 없습니다.
예를 들어, AI 서비스의 가용성을 확인하려면, 셀렉터는 채팅 메시지와 옵션을 서비스에 보내야 합니다. 서비스가 사용 가능하면 완성을 반환하거나, 사용 불가능하면 다른 서비스로 대체해야 합니다. TrySelectAIService 메서드가 채팅 메시지 목록이나 옵션을 받지 않으므로, 이 메서드를 사용하여 채팅 메시지를 보내는 것은 불가능합니다. 가능하더라도, 셀렉터가 완성 자체를 반환하지 않기 때문에 소비자 코드는 완성을 얻기 위해 선택된 서비스에 동일한 채팅 메시지를 다시 보내야 합니다. 또한 TrySelectAIService 메서드는 동기식이므로, 일반적으로 권장되지 않는 동기 코드를 사용하지 않고는 채팅 메시지를 보내기 어렵습니다.

위의 내용을 살펴보면, IAIServiceSelector 인터페이스는 다른 목적을 위해 설계되었기 때문에 AI 서비스의 하이브리드 오케스트레이션에 적합하지 않다는 것이 분명합니다: 완성 및 스트리밍 완성 메서드의 결과를 고려하지 않고 SK 컨텍스트와 서비스 메타데이터를 기반으로 AI 서비스의 인스턴스를 동기적으로 선택하기 위한 것입니다.

장점:
- AI 서비스 선택을 위한 기존 메커니즘을 재사용합니다.

단점:
- 모든 AI 서비스에 적합하지 않습니다.
- 모든 시나리오에서 사용 가능하지 않을 수 있는 컨텍스트가 필요합니다.
- 소비자 코드가 단순히 IChatClient 인터페이스를 사용하는 대신 IAIServiceSelector 인터페이스를 인식해야 합니다.
- 동기 메서드입니다.

## 결정 결과

선택한 옵션: 옵션 1, 새로운 추상화가 필요하지 않으며 단순성과 직관성이 대부분의 사용 사례에 충분하기 때문입니다.
더 복잡한 오케스트레이션 시나리오가 필요한 경우 향후 옵션 2를 고려할 수 있습니다.
