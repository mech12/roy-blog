---
# 이 항목들은 선택 사항입니다. 필요 없는 항목은 자유롭게 제거하세요.
status: accepted
contact: dmytrostruk
date: 2023-10-03
deciders: dmytrostruk
consulted: SergeyMenshykh, RogerBarreto, markwallace-microsoft
informed:
---

# Kernel 서비스 등록

## 배경 및 문제 상황

플러그인은 복잡한 시나리오를 지원하기 위해 의존성을 가질 수 있습니다. 예를 들어 `retrieve`, `recall`, `save`, `remove` 같은 함수를 지원하는 `TextMemoryPlugin`이 있습니다. 생성자는 다음과 같이 구현되어 있습니다:

```csharp
public TextMemoryPlugin(ISemanticTextMemory memory)
{
    this._memory = memory;
}
```

`TextMemoryPlugin`은 `ISemanticTextMemory` 인터페이스에 의존합니다. 마찬가지로 다른 플러그인에는 여러 의존성이 있을 수 있으며, 필요한 의존성을 수동 또는 자동으로 해결할 방법이 있어야 합니다.

현재 `ISemanticTextMemory`는 `IKernel` 인터페이스의 속성으로, 플러그인 초기화 시 `TextMemoryPlugin`에 `ISemanticTextMemory`를 주입할 수 있게 합니다:

```csharp
kernel.ImportFunctions(new TextMemoryPlugin(kernel.Memory));
```

Memory 관련 인터페이스뿐만 아니라 플러그인에서 사용될 수 있는 모든 종류의 서비스를 지원할 방법이 있어야 합니다 - `ISemanticTextMemory`, `IPromptTemplateEngine`, `IDelegatingHandlerFactory` 또는 기타 서비스.

## 검토된 옵션

### 솔루션 #1.1 (기본 제공)

사용자가 **수동** 접근 방식으로 모든 플러그인 초기화와 의존성 해결을 담당합니다.

```csharp
var memoryStore = new VolatileMemoryStore();
var embeddingGeneration = new OpenAITextEmbeddingGeneration(modelId, apiKey);
var semanticTextMemory = new SemanticTextMemory(memoryStore, embeddingGeneration);

var memoryPlugin = new TextMemoryPlugin(semanticTextMemory);

var kernel = Kernel.Builder.Build();

kernel.ImportFunctions(memoryPlugin);
```

참고: 이것은 서비스 의존성을 수동으로 해결하는 네이티브 .NET 접근 방식이며, 이 접근 방식은 항상 기본적으로 사용 가능해야 합니다. 의존성 해결을 개선하는 데 도움이 되는 다른 솔루션은 이 접근 방식 위에 추가할 수 있습니다.

### 솔루션 #1.2 (기본 제공)

사용자가 **의존성 주입** 접근 방식으로 모든 플러그인 초기화와 의존성 해결을 담당합니다.

```csharp
var serviceCollection = new ServiceCollection();

serviceCollection.AddTransient<IMemoryStore, VolatileMemoryStore>();
serviceCollection.AddTransient<ITextEmbeddingGeneration>(
    (serviceProvider) => new OpenAITextEmbeddingGeneration(modelId, apiKey));

serviceCollection.AddTransient<ISemanticTextMemory, SemanticTextMemory>();

var services = serviceCollection.BuildServiceProvider();

// 이론적으로 TextMemoryPlugin도 DI 컨테이너에 등록할 수 있습니다.
var memoryPlugin = new TextMemoryPlugin(services.GetService<ISemanticTextMemory>());

var kernel = Kernel.Builder.Build();

kernel.ImportFunctions(memoryPlugin);
```

참고: 솔루션 #1.1과 마찬가지로 이 방식도 기본적으로 지원되어야 합니다. 사용자는 항상 자신의 측에서 모든 의존성을 처리하고 필요한 플러그인만 Kernel에 제공할 수 있습니다.

### 솔루션 #2.1

솔루션 #1.1 및 솔루션 #1.2에 추가하여 의존성 해결 과정을 단순화하기 위한 Kernel 수준의 사용자 정의 서비스 컬렉션 및 서비스 프로바이더.

`IKernel` 인터페이스는 필요한 서비스를 가져오기 위한 최소한의 기능을 가진 자체 서비스 프로바이더 `KernelServiceProvider`를 갖습니다.

```csharp
public interface IKernelServiceProvider
{
    T? GetService<T>(string? name = null);
}

public interface IKernel
{
    IKernelServiceProvider Services { get; }
}
```

```csharp
var kernel = Kernel.Builder
    .WithLoggerFactory(ConsoleLogger.LoggerFactory)
    .WithOpenAITextEmbeddingGenerationService(modelId, apiKey)
    .WithService<IMemoryStore, VolatileMemoryStore>(),
    .WithService<ISemanticTextMemory, SemanticTextMemory>()
    .Build();

var semanticTextMemory = kernel.Services.GetService<ISemanticTextMemory>();
var memoryPlugin = new TextMemoryPlugin(semanticTextMemory);

kernel.ImportFunctions(memoryPlugin);
```

장점:

- 특정 DI 컨테이너 라이브러리에 대한 의존성이 없습니다.
- 경량 구현.
- 플러그인에서 사용될 수 있는 서비스만 등록할 수 있는 가능성 (호스트 애플리케이션으로부터의 격리).
- 동일한 인터페이스를 **이름**으로 여러 번 등록할 수 있는 가능성.

단점:

- 이미 존재하는 라이브러리를 사용하는 대신 사용자 정의 DI 컨테이너에 대한 구현 및 유지보수.
- 플러그인을 임포트하려면 특정 서비스를 주입하기 위해 여전히 수동으로 초기화해야 합니다.

### 솔루션 #2.2

이 솔루션은 플러그인 인스턴스를 수동으로 초기화해야 하는 솔루션 #2.1의 마지막 단점을 처리하기 위한 개선입니다. 이를 위해 Kernel에 플러그인을 임포트하는 새로운 방법을 추가해야 합니다 - 객체 **인스턴스**가 아닌 객체 **타입**으로. 이 경우 Kernel이 `TextMemoryPlugin` 초기화를 담당하고 사용자 정의 서비스 컬렉션에서 모든 필요한 의존성을 주입합니다.

```csharp
// 이것 대신
var semanticTextMemory = kernel.Services.GetService<ISemanticTextMemory>();
var memoryPlugin = new TextMemoryPlugin(semanticTextMemory);

kernel.ImportFunctions(memoryPlugin);

// 이것을 사용
kernel.ImportFunctions<TextMemoryPlugin>();
```

### 솔루션 #3

Kernel에서 사용자 정의 서비스 컬렉션과 서비스 프로바이더 대신, 이미 존재하는 DI 라이브러리인 `Microsoft.Extensions.DependencyInjection`을 사용합니다.

```csharp
var serviceCollection = new ServiceCollection();

serviceCollection.AddTransient<IMemoryStore, VolatileMemoryStore>();
serviceCollection.AddTransient<ITextEmbeddingGeneration>(
    (serviceProvider) => new OpenAITextEmbeddingGeneration(modelId, apiKey));

serviceCollection.AddTransient<ISemanticTextMemory, SemanticTextMemory>();

var services = serviceCollection.BuildServiceProvider();

var kernel = Kernel.Builder
    .WithLoggerFactory(ConsoleLogger.LoggerFactory)
    .WithOpenAITextEmbeddingGenerationService(modelId, apiKey)
    .WithServices(services) // 호스트 애플리케이션에서 등록된 모든 서비스를 Kernel에 전달
    .Build();

// 플러그인 임포트 - 옵션 #1
var semanticTextMemory = kernel.Services.GetService<ISemanticTextMemory>();
var memoryPlugin = new TextMemoryPlugin(semanticTextMemory);

kernel.ImportFunctions(memoryPlugin);

// 플러그인 임포트 - 옵션 #2
kernel.ImportFunctions<TextMemoryPlugin>();
```

장점:

- 의존성 해결을 위한 구현이 필요 없음 - 이미 존재하는 .NET 라이브러리를 사용하면 됩니다.
- 이미 존재하는 애플리케이션에서 등록된 모든 서비스를 한 번에 주입하여 플러그인 의존성으로 사용할 수 있는 가능성.

단점:

- Semantic Kernel 패키지에 대한 추가 의존성 - `Microsoft.Extensions.DependencyInjection`.
- 특정 서비스 목록을 포함할 수 없는 가능성 (호스트 애플리케이션으로부터의 격리 부족).
- `Microsoft.Extensions.DependencyInjection` 버전 불일치 및 런타임 오류 가능성 (예: 사용자가 `Microsoft.Extensions.DependencyInjection` `--version 2.0`을 사용하는데 Semantic Kernel은 `--version 6.0`을 사용하는 경우)

## 결정 결과

현재로서는 Kernel을 단일 책임 단위로 유지하기 위해 솔루션 #1.1과 솔루션 #1.2만 지원합니다. 플러그인 의존성은 플러그인 인스턴스를 Kernel에 전달하기 전에 해결되어야 합니다.
