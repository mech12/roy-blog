---
# 이것들은 선택적 요소입니다. 필요 없는 항목은 자유롭게 제거하세요.
status: accepted
contact: sergeymenshykh
date: 2025-05-13
deciders: markwallace, rbarreto, dmytrostruk, westey-m
consulted: 
informed:
---

## 맥락과 문제 설명

현재 Semantic Kernel(SK)은 소스에 관계없이 **모든** 함수를 AI 모델에 알립니다. 모든 등록된 플러그인의 함수이든 함수 선택 동작을 구성할 때 직접 제공된 함수이든 마찬가지입니다. 이 접근 방식은 함수가 많지 않고 AI 모델이 올바른 함수를 쉽게 선택할 수 있는 대부분의 시나리오에서 완벽하게 작동합니다.

그러나 사용 가능한 함수가 많은 경우, AI 모델이 적절한 함수를 선택하는 데 어려움을 겪어 혼란과 차선의 성능을 초래할 수 있습니다. 이로 인해 AI 모델이 현재 컨텍스트나 대화와 관련 없는 함수를 호출하여 전체 시나리오가 실패할 수 있습니다.

이 ADR은 SK 에이전트, 채팅 완성 서비스, M.E.AI 채팅 클라이언트와 같은 컴포넌트에 컨텍스트 기반 함수 선택 및 알림 메커니즘을 제공하기 위한 다양한 옵션을 검토합니다.

## 결정 동인
- 대화의 컨텍스트에 따라 함수를 동적으로 알릴 수 있어야 합니다.
- SK 및 M.E.AI AI 커넥터와 SK 에이전트에 원활하게 통합되어야 합니다.
- 복잡한 배선 없이 컨텍스트와 함수에 접근할 수 있어야 합니다.

## 범위 외
- RAG든 다른 것이든 특정 함수 선택 알고리즘의 구현.

## 옵션 1: 외부 벡터화 및 검색

이 옵션은 다음 샘플에서 시연됩니다: [PluginSelectionWithFilters.UsingVectorSearchWithChatCompletionAsync](https://github.com/microsoft/semantic-kernel/blob/6eff772c6034992a9db6e10ac12dd445a19d81a8/dotnet/samples/Concepts/Optimization/PluginSelectionWithFilters.cs#L104C23-L104C63)
`PluginStore` 클래스를 사용하여 커널 함수를 벡터화하고 `FunctionProvider`를 사용하여 프롬프트와 관련된 함수를 찾습니다:

````csharp
// 서비스 등록
IKernelBuilder builder = Kernel.CreateBuilder();
builder.Services.AddInMemoryVectorStore();
builder.Services.AddSingleton<IFunctionProvider, FunctionProvider>();
builder.Services.AddSingleton<IPluginStore, PluginStore>();

// 플러그인 등록
Kernel kernel = builder.Build();
kernel.ImportPluginFromType<TimePlugin>();
kernel.ImportPluginFromType<WeatherPlugin>();

// 커널의 모든 함수를 벡터화
IPluginStore pluginStore = kernel.GetRequiredService<IPluginStore>();
await pluginStore.SaveAsync(collectionName: "functions", kernel.Plugins);

const string Prompt = "Provide latest headlines";

// 프롬프트와 관련된 함수를 찾기 위해 RAG 수행
IFunctionProvider functionProvider = kernel.GetRequiredService<IFunctionProvider>();
KernelFunction[] relevantFunctions = await functionProvider.GetRelevantFunctionsAsync(collectionName: "functions", Prompt, kernel.Plugins, numberOfFunctions: 1);

// 관련 함수를 AI 모델에 알리도록 설정
executionSettings.FunctionChoiceBehavior = FunctionChoiceBehavior.Auto(relevantFunctions);

// 채팅 완성 수행
var chatHistory = new ChatHistory();
chatHistory.AddUserMessage(Prompt);

var chatCompletionService = kernel.GetRequiredService<IChatCompletionService>();
var result = await chatCompletionService.GetChatMessageContentAsync(chatHistory, executionSettings, kernel);

Console.WriteLine(result);
````

AI 모델 요청별이 아닌 작업별로 호출됩니다; AI 모델이 함수 호출을 수행하는 경우 한 번의 작업 호출이 여러 AI 모델 요청을 초래할 수 있습니다.

장점:
- SK 채팅 완성 서비스, SK 에이전트, M.E.AI 채팅 클라이언트를 포함한 모든 AI 컴포넌트에서 사용할 수 있습니다.

단점:
- 솔루션의 모든 부분(함수의 벡터화, 함수 검색, 함수 알림)을 함께 통합하는 것이 복잡합니다.
- 프롬프트 템플릿에 구성된 함수 선택 동작을 지원하지 않습니다.

## 옵션 1A: 함수 호출 필터

이 옵션은 다음 샘플에서 시연됩니다: [PluginSelectionWithFilters.UsingVectorSearchWithKernelAsync](https://github.com/microsoft/semantic-kernel/blob/6eff772c6034992a9db6e10ac12dd445a19d81a8/dotnet/samples/Concepts/Optimization/PluginSelectionWithFilters.cs#L30C23-L30C55).
벡터화 부분은 옵션 1과 동일하며, `InvokePromptAsync` 함수에 대한 호출을 가로채어 프롬프트와 관련된 함수를 식별하고 실행 설정을 통해 AI 모델에 알리도록 설정하는 함수 호출 필터로 함수 선택 부분이 약간 다릅니다:

````csharp
// 서비스 등록
IKernelBuilder builder = Kernel.CreateBuilder();
builder.Services.AddInMemoryVectorStore();
builder.Services.AddSingleton<IFunctionProvider, FunctionProvider>();
builder.Services.AddSingleton<IPluginStore, PluginStore>();

// 플러그인 등록
Kernel kernel = builder.Build();
kernel.ImportPluginFromType<TimePlugin>();
kernel.ImportPluginFromType<WeatherPlugin>();

// 커널의 모든 함수를 벡터화
IPluginStore pluginStore = kernel.GetRequiredService<IPluginStore>();
await pluginStore.SaveAsync(collectionName: "functions", kernel.Plugins);

// 함수 호출 필터 등록
IFunctionProvider functionProvider = kernel.GetRequiredService<IFunctionProvider>();
kernel.FunctionInvocationFilters.Add(new PluginSelectionFilter(functionProvider: functionProvider, collectionName: "functions"));

// 채팅 완성 수행
KernelArguments kernelArguments = new(executionSettings) { ["Request"] = "Provide latest headlines" };
await kernel.InvokePromptAsync("{{$Request}}", kernelArguments);

// 함수 호출 필터
class PluginSelectionFilter(IFunctionProvider functionProvider, string collectionName)
{
    public async Task OnFunctionInvocationAsync(FunctionInvocationContext context, Func<FunctionInvocationContext, Task> next)
    {
        string request = context.Arguments["Request"];

        if (context.Function.Name.Contains(nameof(KernelExtensions.InvokePromptAsync)) && !string.IsNullOrWhiteSpace(request))
        {
            var functions = await functionProvider.GetRelevantFunctionsAsync(collectionName, request, plugins, numberOfFunctions);

            context.Arguments.ExecutionSettings.FunctionChoiceBehavior = FunctionChoiceBehavior.Auto(functions);
        }

        await next(context);
    }
}
````

AI 모델 요청별이 아닌 작업별로 호출됩니다; AI 모델이 함수 호출을 수행하는 경우 한 번의 작업 호출이 여러 AI 모델 요청을 초래할 수 있습니다.

장점:

단점:
- `InvokePromptAsync` 함수의 사용에 의존하므로, `kernel.InvokePromptAsync` 함수가 사용되는 경우를 제외한 모든 시나리오에서 사용할 수 없습니다.
- 프롬프트 템플릿에 구성된 함수 선택 동작을 지원하지 않습니다.
 
## 옵션 2: M.E.AI ChatClient 데코레이터

이 옵션은 `M.E.AI.IChatClient` 인터페이스의 구현(예: `ContextFunctionSelectorChatClient` 클래스)을 가정하며, `GetResponseAsync` 또는 `GetResponseStreamAsync` 메서드의 `ChatOptions` 매개변수에서 사용 가능한 모든 함수를 벡터화합니다. 그런 다음 이러한 메서드에 전달된 채팅 메시지 목록으로 표현되는 컨텍스트와 관련된 함수를 검색합니다:

````csharp
public class ContextFunctionSelectorChatClient : DelegatingChatClient
{
    protected ContextFunctionSelectorChatClient(IChatClient innerClient) : base(innerClient)
    {
    }

    public override async Task<ChatResponse> GetResponseAsync(IEnumerable<ChatMessage> messages, ChatOptions? options = null)
    {
        ChatOptions? targetOptions = options;
        if (options?.Tools?.Any() ?? false)
        {
            targetOptions = options.Clone();

            AITool[] functionsToAdvertise = await this.GetRelevantFunctions(options, messages).ConfigureAwait(false);

            targetOptions.Tools = functionsToAdvertise;
        }

        return await base.GetResponseAsync(messages, targetOptions, ct).ConfigureAwait(false);
    }

    private async Task<AITool[]> GetRelevantFunctions(ChatOptions options, IEnumerable<ChatMessage> messages)
    {
        // 1. `options.Tool` 컬렉션의 모든 함수를 벡터화합니다(아직 벡터화되지 않은 경우).
        // 2. `messages` 컬렉션으로 표현되는 컨텍스트를 벡터화합니다.
        // 3. 벡터화된 컨텍스트를 사용하여 가장 관련성 높은 함수를 검색하고 반환합니다.
    }

    public override IAsyncEnumerable<ChatResponseUpdate> GetStreamingResponseAsync(IEnumerable<ChatMessage> messages, ChatOptions? options = null)
    {
        // GetResponseAsync와 유사하지만 스트리밍용
    }
}

// M.E.AI 채팅 클라이언트에서의 사용
ChatClient chatClient = new("model", "api-key");

IChatClient client = chatClient.AsIChatClient()
    .AsBuilder()
    .UseFunctionInvocation()
    .UseContextFunctionSelector()
    .Build();

// SK 채팅 완성 서비스에서의 사용
IChatCompletionService chatCompletionService = new OpenAIChatCompletionService("<model-id>", "<api-key>");

IChatClient client = chatCompletionService.AsChatClient()
    .AsBuilder()
    .UseContextFunctionSelector()
    .Build();
````

데코레이터는 AI 모델 요청별이 아닌 작업별로 호출됩니다; AI 모델이 함수 호출을 수행하는 경우 한 번의 작업 호출이 여러 AI 모델 요청을 초래할 수 있습니다.

장점:
- SK 채팅 완성 서비스 및 M.E.AI 채팅 클라이언트와 원활하게 작동합니다.
- M.E.AI가 채택한 초기화 패턴에 맞춘 간편한 배선.
- 새로운 추상화가 필요하지 않습니다.
- 새로운 함수 셀렉터를 쉽게 추가하고 체이닝할 수 있습니다.

단점:
- 채팅 완성 에이전트에서만 작동하며, 채팅 완성 서비스를 사용하지 않는 SK 에이전트에서는 작동하지 않습니다.
- 프롬프트 템플릿에 구성된 함수 선택 동작을 지원하지 않습니다.

## 옵션 3: 함수 알림 필터

이 옵션은 대화의 컨텍스트에 따라 AI 모델에 알릴 함수를 선택하는 데 사용되는 새로운 필터 타입을 가정합니다:

````csharp
// 플러그인 등록
Kernel kernel = new Kernel();
kernel.ImportPluginFromType<TimePlugin>();
kernel.ImportPluginFromType<WeatherPlugin>();

// 함수 알림 필터 등록
kernel.FunctionAdvertisementFilters.Add(new ContextFunctionSelectorFilter());

// 채팅 완성 수행
await kernel.InvokePromptAsync("Provide latest headlines");

// 함수 호출 필터
class ContextFunctionSelectorFilter()
{
    public async Task OnFunctionsAdvertisementAsync(FunctionAdvertisementContext context, Func<FunctionAdvertisementContext, Task> next);
    {
        // 1. `context.Functions` 컬렉션의 모든 함수를 벡터화합니다(아직 벡터화되지 않은 경우).
        // 2. `context.ChatHistory` 컬렉션으로 표현되는 컨텍스트를 벡터화합니다.
        // 3. 벡터화된 컨텍스트를 사용하여 가장 관련성 높은 함수를 검색하고 `context.Functions` 속성에 할당합니다.
    }
}
````

필터는 작업별 및 AI 모델 요청별로 호출될 수 있습니다; AI 모델이 함수 호출을 수행하는 경우 한 번의 작업 호출이 여러 AI 모델 요청을 초래할 수 있습니다.

장점:
- SK 사용자에게 익숙한 개념입니다.
- 채팅 완성 서비스와 함께 작동합니다.
- 컨텍스트를 필터에 제공할 수 있는 경우, 채팅 완성 및 비채팅 완성 **SK** 에이전트 모두에서 작동합니다.

단점:
- 새로운 추상화가 필요합니다.
- Kernel의 공개 API 표면을 확장해야 합니다.
- SK 에이전트, 채팅 완성 서비스, M.E.AI 채팅 클라이언트 어댑터 등 모든 AI 컴포넌트가 필터를 호출하도록 업데이트되어야 합니다.

## 옵션 4: FunctionChoiceBehavior 콜백

이 옵션은 기존 `AutoFunctionChoiceBehavior`, `RequiredFunctionChoiceBehavior`, `NoneFunctionChoiceBehavior` 클래스를 함수 셀렉터를 매개변수로 받는 새로운 생성자로 확장하여 컨텍스트에 따라 AI 모델에 알릴 함수를 선택하는 데 사용합니다.

````csharp
// 서비스 등록
IKernelBuilder builder = Kernel.CreateBuilder();
builder.Services.AddInMemoryVectorStore();
builder.Services.AddSingleton<IFunctionProvider, FunctionProvider>();
builder.Services.AddSingleton<IPluginStore, PluginStore>();

// 플러그인 등록
Kernel kernel = builder.Build();
kernel.ImportPluginFromType<TimePlugin>();
kernel.ImportPluginFromType<WeatherPlugin>();

// 관련 함수를 AI 모델에 알리도록 설정
executionSettings.FunctionChoiceBehavior = FunctionChoiceBehavior.Auto(FunctionSelector);

// 채팅 완성 수행
var chatHistory = new ChatHistory();
chatHistory.AddUserMessage("Provide latest headlines");

var chatCompletionService = kernel.GetRequiredService<IChatCompletionService>();
var result = await chatCompletionService.GetChatMessageContentAsync(chatHistory, executionSettings, kernel);

Console.WriteLine(result);

async Task<IList<KernelFunction>> FunctionSelector(FunctionChoiceBehaviorConfigurationContext context)
{
    // `context.Functions` 컬렉션의 모든 함수를 벡터화
    IPluginStore pluginStore = context.Kernel.GetRequiredService<IPluginStore>();
    await pluginStore.SaveAsync(collectionName: "functions", context.Kernel.Plugins);

    // 벡터화된 컨텍스트를 사용하여 가장 관련성 높은 함수를 검색
    IFunctionProvider functionProvider = kernel.GetRequiredService<IFunctionProvider>();
    IList<KernelFunction> relevantFunctions = await functionProvider.GetRelevantFunctionsAsync(collectionName: "functions", context.ChatHistory, kernel.Plugins, numberOfFunctions: 1);

    return relevantFunctions;
}
````

필터는 작업별 및 AI 모델 요청별로 호출될 수 있습니다; AI 모델이 함수 호출을 수행하는 경우 한 번의 작업 호출이 여러 AI 모델 요청을 초래할 수 있습니다.

장점:

단점:
- 프롬프트 템플릿에 구성된 함수 선택 동작을 지원하지 않습니다.
- `FunctionChoiceBehavior`를 사용하는 컴포넌트에서만 사용할 수 있습니다: SK 채팅 완성 서비스 및 채팅 완성 에이전트.

## 옵션 적용 가능성

이 표는 위에서 설명한 옵션들이 Semantic Kernel 및 M.E.AI의 다양한 컴포넌트에 대한 적용 가능성을 요약합니다:

| 옵션 | 범위 | OpenAI & AzureAI 에이전트 | Bedrock 에이전트 | 채팅 완성 에이전트 | SK 채팅 완성 서비스 | M.E.AI 채팅 클라이언트 |
|----------------------------------------|-----------|-------------------------|-----------------------|-----------------------|----------------------------|----------------------|
| **1.** 외부 벡터화 및 검색 | 작업 | Yes<sup>1,2</sup> | Yes<sup>1,3</sup> | Yes<sup>1,2or4</sup> | Yes<sup>1,2or4</sup> | Yes<sup>1</sup> |
| **1A.** 함수 호출 필터 | 작업 | No<sup>5</sup> | No<sup>5</sup> | No<sup>5</sup> | No<sup>5</sup> | No |
| **2.** M.E.AI ChatClient 데코레이터 | 작업 | No | No | Yes<sup>6</sup> | Yes<sup>6</sup> | Yes |
| **3.** 함수 알림 필터 | 작업 & 요청 | Yes | No<sup>3</sup> | Yes | Yes | Yes<sup>7</sup> |
| **4.** FunctionChoiceBehavior 콜백 | 작업 & 요청 | No<sup>8,9</sup> | No<sup>8</sup> | Yes | Yes | Yes<sup>7</sup> |

<sup>1</sup> 함수 벡터화, 함수 검색, 함수 알림, 에이전트/채팅 완성 서비스 호출의 수동 오케스트레이션이 필요합니다.
이 솔루션은 현재 사용 가능하지만 모든 컴포넌트를 함께 통합하기 위한 복잡한 배선이 필요합니다.

<sup>2</sup> 에이전트 또는 채팅 완성 서비스의 각 호출에 관련 함수를 제공하려면, 먼저 커널에 등록된 모든 플러그인을 제거해야 합니다.
그런 다음 각 호출에 대해 `kernel.Plugins.AddFromFunctions("dynamicPlugin", [relevantFunctions])`를 사용하여 관련 함수가 포함된 새 플러그인을 커널에 등록해야 합니다.
또는 플러그인을 제거하는 대신 새 커널을 생성할 수 있지만, 에이전트의 새 인스턴스도 생성해야 합니다.
관련 함수가 더 이상 원래 플러그인의 일부가 아니고 새 플러그인으로 재패키징되므로, 함수 이름 충돌 및 원래 플러그인이 제공하는 추가 컨텍스트의 손실과 같은 문제가 발생할 수 있습니다.

<sup>3</sup> 각 에이전트 호출에 관련 함수를 제공하려면, 에이전트가 에이전트 초기화 시에만 사용되는 `AgentDefinition.Tools` 컬렉션에 정의된 함수를 사용하므로 호출별로 에이전트의 새 인스턴스를 생성해야 합니다.

<sup>4</sup> 에이전트 또는 채팅 완성 서비스의 각 호출에 관련 함수를 제공하려면, 오케스트레이션 기능이 `*FunctionChoiceBehavior` 클래스의 새 인스턴스의 `functions` 매개변수를 통해 함수를 제공하고 해당 인스턴스를 `executionSettings.FunctionChoiceBehavior` 속성에 할당해야 합니다: `executionSettings.FunctionChoiceBehavior = new AutoFunctionChoiceBehavior(functions)`.

<sup>5</sup> 함수 호출 필터를 사용하여 함수 선택 및 알림을 수행합니다. 필터는 `kernel.InvokePromptAsync` 함수의 호출에 의해 트리거된 경우에만 관련 함수를 검색하고 실행 설정을 통해 AI 모델에 알리도록 설정합니다. 다른 함수 호출에 의해 트리거되면 아무것도 하지 않으므로, `kernel.InvokePromptAsync` 함수가 사용되는 경우를 제외한 모든 경우에서 사용할 수 없습니다.

<sup>6</sup> M.E.AI 채팅 클라이언트는 `ChatClientChatCompletionService` SK 어댑터를 사용하여 `IChatCompletionService` 인터페이스에 적응해야 합니다.

<sup>7</sup> M.E.AI 채팅 클라이언트는 데코레이터(SK에서 사용 가능)로 데코레이트되어야 하며, 데코레이터가 관련 함수를 가져오기 위해 함수 알림 필터/함수 선택 동작에 접근할 수 있어야 합니다.

<sup>8</sup> OpenAI, AzureAI, Bedrock 에이전트 중 어느 것도 함수 알림에 함수 선택 동작을 사용하지 않습니다. 자동 함수 선택 동작 이외의 다른 함수 선택 동작을 지원하지 않으므로 어떤 에이전트를 확장하여 함수 선택 동작을 사용하게 하는 것은 의미가 없습니다.

<sup>9</sup> OpenAI 또는 AzureAI 에이전트를 확장하여 제공된 함수 선택 동작에서 관련 함수를 가져오면 개발 경험이 혼란스러워집니다.
현재 함수는 에이전트 정의, 에이전트 생성자, 커널의 세 곳에서 에이전트에 제공될 수 있습니다. 네 번째 소스를 추가하면 더 혼란스러워집니다.

참고:
- 서버 측에서 스레드를 유지하는 에이전트의 경우, 먼저 서버에서 전체 스레드를 로드하지 않으면 전체 컨텍스트를 가져오는 것이 불가능합니다.
이는 효율적이지 않으며 에이전트에서 지원되지 않을 수 있습니다. 그러나 에이전트 호출 중 전달된 메시지는 충분할 수 있으며 함수 선택을 위한 컨텍스트로 사용할 수 있습니다.

## 에이전트 메모리와의 통합

에이전트의 메모리 모델은 다음 클래스로 표현됩니다:

````csharp
public sealed class AIContextPart
{
    public string? Instructions { get; set; }
    public List<AIFunction> AIFunctions { get; set; } = new();
}

public abstract class AIContextBehavior
{
    public virtual Task OnThreadCreatedAsync(string? threadId, CancellationToken ct) {...}
    public virtual Task OnNewMessageAsync(string? threadId, ChatMessage newMessage, CancellationToken ct) {...}
    public virtual Task OnThreadDeleteAsync(string? threadId, CancellationToken ct) {...}
    public abstract Task<AIContextPart> OnModelInvokeAsync(ICollection<ChatMessage> newMessages, CancellationToken ct);
    public virtual Task OnSuspendAsync(string? threadId, CancellationToken ct) {...}
    public virtual Task OnResumeAsync(string? threadId, CancellationToken ct) {...}
}

public sealed class AIContextBehaviorsManager
{
    public AIContextBehaviorsManager(IEnumerable<AIContextBehavior> aiContextBehaviors) {...}
    public void Add(AIContextBehavior aiContextBehavior) {...}
    public void AddFromServiceProvider(IServiceProvider serviceProvider) {...}
    public async Task OnThreadCreatedAsync(string? threadId, CancellationToken ct) {...}
    public async Task OnThreadDeleteAsync(string threadId, CancellationToken ct) {...}
    public async Task OnNewMessageAsync(string? threadId, ChatMessage newMessage, CancellationToken ct) {...}
    public async Task<AIContextPart> OnModelInvokeAsync(ICollection<ChatMessage> newMessages, CancellationToken ct) {...}
    public async Task OnSuspendAsync(string? threadId, CancellationToken ct) {...}
    public async Task OnResumeAsync(string? threadId, CancellationToken ct) {...}
}
````

모델 사용법을 보여주는 예시:

````csharp
// 커널을 생성하고 플러그인을 등록합니다
Kernel kernel = this.CreateKernelWithChatCompletion();
kernel.Plugins.AddFromType<FinancePlugin>();

// Mem0Behavior 생성
Mem0Behavior mem0Behavior = new(...);
await mem0Behavior.ClearStoredMemoriesAsync();

// 채팅 완성 에이전트 생성
ChatCompletionAgent agent = new(kernel, ...);

// 에이전트 스레드를 생성하고 Mem0Behavior를 추가합니다
ChatHistoryAgentThread agentThread = new();    
agentThread.AIContextBehaviors.Add(mem0Behavior);

// 에이전트에 프롬프트
string userMessage = "Please retrieve my company report";
ChatMessageContent message = await agent.InvokeAsync(userMessage, agentThread).FirstAsync();
````

비에이전트 시나리오(예: 채팅 완성 서비스 또는 채팅 클라이언트)에서 함수 목록을 좁히기 위해 기존 AI 컨텍스트 동작을 재사용해야 하는 경우가 있을 수 있습니다.
이러한 경우, AI 컨텍스트 동작을 위에서 설명한 옵션 중 하나에 필요한 모델에 적응시키거나, 바람직하게는 벡터화 및 시맨틱 검색을 위한 동일한 컴포넌트를 사용하여 AI 컨텍스트 동작과 위에서 설명한 옵션 중 하나에 필요한 모델을 모두 구현할 수 있습니다.

## 결정 결과
ADR 검토 회의에서 에이전트의 함수에 대해 RAG를 수행하는 AIContextBehavior를 구현하여 에이전트에 대한 컨텍스트 기반 함수 선택을 우선적으로 처리하기로 결정되었습니다.
이후 요청 시, 옵션 2: M.E.AI ChatClient 데코레이터를 사용하여 채팅 완성 서비스 및 M.E.AI 채팅 클라이언트로 동일한 기능을 확장할 수 있습니다.
