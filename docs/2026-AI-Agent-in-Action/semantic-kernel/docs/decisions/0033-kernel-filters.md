---
# 선택적 요소입니다. 필요 없는 항목은 자유롭게 제거하세요.
status: accepted
contact: dmytrostruk
date: 2023-01-23
deciders: sergeymenshykh, markwallace, rbarreto, stephentoub, dmytrostruk
---

# 커널 필터

## 배경 및 문제 설명

현재 함수 실행 중 이벤트를 가로채는 방식은 커널 이벤트와 이벤트 핸들러를 사용하여 예상대로 작동합니다. 예시:

```csharp
ILogger logger = loggerFactory.CreateLogger("MyLogger");

var kernel = Kernel.CreateBuilder()
    .AddOpenAIChatCompletion(
        modelId: TestConfiguration.OpenAI.ChatModelId,
        apiKey: TestConfiguration.OpenAI.ApiKey)
    .Build();

void MyInvokingHandler(object? sender, FunctionInvokingEventArgs e)
{
    logger.LogInformation("Invoking: {FunctionName}", e.Function.Name)
}

void MyInvokedHandler(object? sender, FunctionInvokedEventArgs e)
{
    if (e.Result.Metadata is not null && e.Result.Metadata.ContainsKey("Usage"))
    {
        logger.LogInformation("Token usage: {TokenUsage}", e.Result.Metadata?["Usage"]?.AsJson());
    }
}

kernel.FunctionInvoking += MyInvokingHandler;
kernel.FunctionInvoked += MyInvokedHandler;

var result = await kernel.InvokePromptAsync("How many days until Christmas? Explain your thinking.")
```

이 접근 방식에는 몇 가지 문제가 있습니다:

1. 이벤트 핸들러는 의존성 주입을 지원하지 않습니다. 핸들러가 특정 서비스가 사용 가능한 동일한 스코프에서 정의되지 않는 한, 애플리케이션에 등록된 특정 서비스에 접근하기 어렵습니다. 이 접근 방식은 핸들러가 솔루션에서 정의될 수 있는 위치에 일부 제한을 줍니다. (예: 개발자가 핸들러에서 `ILoggerFactory`를 사용하려면, 핸들러는 `ILoggerFactory` 인스턴스가 사용 가능한 곳에서 정의되어야 합니다).
2. 애플리케이션 런타임의 어떤 특정 시점에 핸들러가 커널에 연결되어야 하는지가 명확하지 않습니다. 또한, 어떤 시점에 핸들러를 분리해야 하는지도 명확하지 않습니다.
3. .NET에서의 이벤트 및 이벤트 핸들러 메커니즘은 이전에 이벤트를 다루지 않은 .NET 개발자에게 익숙하지 않을 수 있습니다.

<!-- 선택적 요소입니다. 자유롭게 제거하세요. -->

## 결정 동인

1. 핸들러에 대한 의존성 주입이 지원되어 애플리케이션 내 등록된 서비스에 쉽게 접근할 수 있어야 합니다.
2. 핸들러가 Startup.cs든 별도 파일이든 솔루션 내 어디에서 정의되든 제한이 없어야 합니다.
3. 애플리케이션 런타임의 특정 시점에 핸들러를 등록하고 제거하는 명확한 방법이 있어야 합니다.
4. 커널에서 이벤트를 수신하고 처리하는 메커니즘이 .NET 생태계에서 쉽고 일반적이어야 합니다.
5. 새로운 접근 방식은 커널 이벤트에서 사용 가능한 동일한 기능을 지원해야 합니다 - 함수 실행 취소, 커널 인수 변경, AI에 보내기 전 렌더링된 프롬프트 변경 등.

## 결정 결과

커널 필터 도입 - ASP.NET의 액션 필터와 유사한 방식으로 커널에서 이벤트를 수신하는 접근 방식.

Semantic Kernel 전반에 걸쳐 두 가지 새로운 추상화가 사용되며, 개발자는 자신의 요구를 충족하는 방식으로 이러한 추상화를 구현해야 합니다.

함수 관련 이벤트의 경우: `IFunctionFilter`

```csharp
public interface IFunctionFilter
{
    void OnFunctionInvoking(FunctionInvokingContext context);

    void OnFunctionInvoked(FunctionInvokedContext context);
}
```

프롬프트 관련 이벤트의 경우: `IPromptFilter`

```csharp
public interface IPromptFilter
{
    void OnPromptRendering(PromptRenderingContext context);

    void OnPromptRendered(PromptRenderedContext context);
}
```

새로운 접근 방식은 개발자가 별도의 클래스에서 필터를 정의하고 커널 이벤트를 올바르게 처리하기 위해 필요한 서비스를 쉽게 주입할 수 있게 합니다:

MyFunctionFilter.cs - 위에 제시된 이벤트 핸들러와 동일한 로직을 가진 필터:

```csharp
public sealed class MyFunctionFilter : IFunctionFilter
{
    private readonly ILogger _logger;

    public MyFunctionFilter(ILoggerFactory loggerFactory)
    {
        this._logger = loggerFactory.CreateLogger("MyLogger");
    }

    public void OnFunctionInvoking(FunctionInvokingContext context)
    {
        this._logger.LogInformation("Invoking {FunctionName}", context.Function.Name);
    }

    public void OnFunctionInvoked(FunctionInvokedContext context)
    {
        var metadata = context.Result.Metadata;

        if (metadata is not null && metadata.ContainsKey("Usage"))
        {
            this._logger.LogInformation("Token usage: {TokenUsage}", metadata["Usage"]?.AsJson());
        }
    }
}
```

새 필터가 정의되면, 의존성 주입(사전 구성)을 사용하거나 커널 초기화 후(사후 구성)에 필터를 추가하여 커널에서 사용하도록 쉽게 구성할 수 있습니다:

```csharp
IKernelBuilder kernelBuilder = Kernel.CreateBuilder();
kernelBuilder.AddOpenAIChatCompletion(
        modelId: TestConfiguration.OpenAI.ChatModelId,
        apiKey: TestConfiguration.OpenAI.ApiKey);

// DI를 사용하여 필터 추가 (사전 구성)
kernelBuilder.Services.AddSingleton<IFunctionFilter, MyFunctionFilter>();

Kernel kernel = kernelBuilder.Build();

// 커널 초기화 후 필터 추가 (사후 구성)
// kernel.FunctionFilters.Add(new MyAwesomeFilter());

var result = await kernel.InvokePromptAsync("How many days until Christmas? Explain your thinking.");
```

등록 순서대로 트리거되는 여러 필터를 구성하는 것도 가능합니다:

```csharp
kernelBuilder.Services.AddSingleton<IFunctionFilter, Filter1>();
kernelBuilder.Services.AddSingleton<IFunctionFilter, Filter2>();
kernelBuilder.Services.AddSingleton<IFunctionFilter, Filter3>();
```

그리고 런타임에 필터 실행 순서를 변경하거나 필요한 경우 특정 필터를 제거하는 것도 가능합니다:

```csharp
kernel.FunctionFilters.Insert(0, new InitialFilter());
kernel.FunctionFilters.RemoveAt(1);
```
