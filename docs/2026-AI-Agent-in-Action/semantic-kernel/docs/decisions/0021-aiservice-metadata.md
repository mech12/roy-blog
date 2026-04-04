---
# 이 항목들은 선택 사항입니다. 필요 없는 항목은 자유롭게 삭제하세요.
status: {proposed}
date: {2023-11-10}
deciders: SergeyMenshykh, markwallace, rbarreto, dmytrostruk
consulted: 
informed: 
---
# AI 서비스 메타데이터 추가

## 맥락 및 문제 설명

개발자는 시맨틱 함수나 계획을 실행하는 데 사용될 `IAIService`에 대한 더 많은 정보를 알 수 있어야 합니다.
이 정보가 필요한 이유의 몇 가지 예시:

1. SK 개발자로서, 구성된 모델 ID를 기반으로 사용할 OpenAI 서비스를 선택할 수 있는 `IAIServiceSelector`를 작성하여, 실행하는 프롬프트에 따라 최적의(가장 저렴할 수 있는) 모델을 선택할 수 있습니다.
2. SK 개발자로서, 프롬프트가 LLM에 전송되기 전에 프롬프트의 토큰 크기를 계산하는 사전 호출 훅을 작성하여, 사용할 최적의 `IAIService`를 결정할 수 있습니다. 프롬프트의 토큰 크기를 계산하는 데 사용하는 라이브러리에는 모델 ID가 필요합니다.

`IAIService`의 현재 구현은 비어 있습니다.

```csharp
public interface IAIService
{
}
```

`T IKernel.GetService<T>(string? name = null) where T : IAIService;`를 사용하여 `IAIService` 인스턴스를 검색할 수 있습니다. 즉, 서비스 유형과 이름(서비스 ID라고도 함)으로 검색합니다.
`IAIService`의 구체적인 인스턴스는 서비스 제공자에 따라 다른 속성을 가질 수 있습니다. 예를 들어, Azure OpenAI에는 배포 이름이 있고 OpenAI 서비스에는 모델 ID가 있습니다.

다음 코드 스니펫을 고려하세요:

```csharp
IKernel kernel = new KernelBuilder()
    .WithLoggerFactory(ConsoleLogger.LoggerFactory)
    .WithAzureChatCompletionService(
        deploymentName: chatDeploymentName,
        endpoint: endpoint,
        serviceId: "AzureOpenAIChat",
        apiKey: apiKey)
    .WithOpenAIChatCompletionService(
        modelId: openAIModelId,
        serviceId: "OpenAIChat",
        apiKey: openAIApiKey)
    .Build();

var service = kernel.GetService<IChatCompletion>("OpenAIChat");
```

Azure OpenAI의 경우 배포 이름으로 서비스를 생성합니다. 이것은 AI 모델을 배포한 사람이 지정한 임의의 이름입니다. 예를 들어 `eastus-gpt-4` 또는 `foo-bar`일 수 있습니다.
OpenAI의 경우 모델 ID로 서비스를 생성합니다. 이것은 배포된 OpenAI 모델 중 하나와 일치해야 합니다.

OpenAI를 사용하는 프롬프트 작성자의 관점에서, 일반적으로 모델을 기반으로 프롬프트를 튜닝합니다. 따라서 프롬프트가 실행될 때 모델 ID를 사용하여 서비스를 검색할 수 있어야 합니다. 위 코드 스니펫에서 볼 수 있듯이 `IKernel`은 ID로만 `IAService` 인스턴스 검색을 지원합니다. 또한 `IChatCompletion`은 제네릭 인터페이스이므로 특정 커넥터 인스턴스에 대한 정보를 제공하는 속성이 포함되어 있지 않습니다.

## 결정 요인

* `IAIService` 인스턴스에 대한 일반 메타데이터를 저장하는 메커니즘이 필요합니다.
  * 관련 메타데이터를 저장하는 것은 구체적인 `IAIService` 인스턴스의 책임입니다. 예: OpenAI 및 HuggingFace AI 서비스의 모델 ID.
* 사용 가능한 `IAIService` 인스턴스를 반복할 수 있어야 합니다.

## 검토한 옵션

* 옵션 #1
  * `IAIService`를 확장하여 다음 속성을 포함합니다:
    * `string? ModelId { get; }` - 모델 ID를 반환합니다. 적절한 값으로 채우는 것은 각 `IAIService` 구현의 책임입니다.
    * `IReadOnlyDictionary<string, object> Attributes { get; }` - 읽기 전용 딕셔너리로 속성을 반환합니다. 적절한 메타데이터로 채우는 것은 각 `IAIService` 구현의 책임입니다.
  * `INamedServiceProvider`를 확장하여 이 메서드를 포함합니다: `ICollection<T> GetServices<T>() where T : TService;`
  * `OpenAIKernelBuilderExtensions`를 확장하여 특정 모델을 대상으로 할 수 있는 경우 `WithAzureXXX` 메서드에 `modelId` 속성을 포함합니다.
* 옵션 #2
  * `IAIService`를 확장하여 다음 메서드를 포함합니다:
    * `T? GetAttributes<T>() where T : AIServiceAttributes;` - `AIServiceAttributes`의 인스턴스를 반환합니다. 자체 서비스 속성 클래스를 정의하고 적절한 값으로 채우는 것은 각 `IAIService` 구현의 책임입니다.
  * `INamedServiceProvider`를 확장하여 이 메서드를 포함합니다: `ICollection<T> GetServices<T>() where T : TService;`
  * `OpenAIKernelBuilderExtensions`를 확장하여 특정 모델을 대상으로 할 수 있는 경우 `WithAzureXXX` 메서드에 `modelId` 속성을 포함합니다.
* 옵션 #3
* 옵션 #2
  * `IAIService`를 확장하여 다음 속성을 포함합니다:
    * `public IReadOnlyDictionary<string, object> Attributes => this.InternalAttributes;` - 읽기 전용 딕셔너리를 반환합니다. 자체 서비스 속성 클래스를 정의하고 적절한 값으로 채우는 것은 각 `IAIService` 구현의 책임입니다.
    * `ModelId`
    * `Endpoint`
    * `ApiVersion`
  * `INamedServiceProvider`를 확장하여 이 메서드를 포함합니다: `ICollection<T> GetServices<T>() where T : TService;`
  * `OpenAIKernelBuilderExtensions`를 확장하여 특정 모델을 대상으로 할 수 있는 경우 `WithAzureXXX` 메서드에 `modelId` 속성을 포함합니다.

이러한 옵션은 다음과 같이 사용됩니다:

SK 개발자로서, 모델 ID를 기반으로 AI 서비스를 선택하는 사용자 정의 `IAIServiceSelector`를 작성하여 사용되는 LLM을 제한하고 싶습니다.
아래 샘플에서 서비스 선택기 구현은 GPT3 모델인 첫 번째 서비스를 찾습니다.

### 옵션 1

``` csharp
public class Gpt3xAIServiceSelector : IAIServiceSelector
{
    public (T?, AIRequestSettings?) SelectAIService<T>(string renderedPrompt, IAIServiceProvider serviceProvider, IReadOnlyList<AIRequestSettings>? modelSettings) where T : IAIService
    {
        var services = serviceProvider.GetServices<T>();
        foreach (var service in services)
        {
            if (!string.IsNullOrEmpty(service.ModelId) && service.ModelId.StartsWith("gpt-3", StringComparison.OrdinalIgnoreCase))
            {
                Console.WriteLine($"Selected model: {service.ModelId}");
                return (service, new OpenAIRequestSettings());
            }
        }

        throw new SKException("Unable to find AI service for GPT 3.x.");
    }
}
```

## 옵션 2

``` csharp
public class Gpt3xAIServiceSelector : IAIServiceSelector
{
    public (T?, AIRequestSettings?) SelectAIService<T>(string renderedPrompt, IAIServiceProvider serviceProvider, IReadOnlyList<AIRequestSettings>? modelSettings) where T : IAIService
    {
        var services = serviceProvider.GetServices<T>();
        foreach (var service in services)
        {
            var serviceModelId = service.GetAttributes<AIServiceAttributes>()?.ModelId;
            if (!string.IsNullOrEmpty(serviceModelId) && serviceModelId.StartsWith("gpt-3", StringComparison.OrdinalIgnoreCase))
            {
                Console.WriteLine($"Selected model: {serviceModelId}");
                return (service, new OpenAIRequestSettings());
            }
        }

        throw new SKException("Unable to find AI service for GPT 3.x.");
    }
}
```

## 옵션 3

```csharp
public (T?, AIRequestSettings?) SelectAIService<T>(string renderedPrompt, IAIServiceProvider serviceProvider, IReadOnlyList<AIRequestSettings>? modelSettings) where T : IAIService
{
    var services = serviceProvider.GetServices<T>();
    foreach (var service in services)
    {
        var serviceModelId = service.GetModelId();
        var serviceOrganization = service.GetAttribute(OpenAIServiceAttributes.OrganizationKey);
        var serviceDeploymentName = service.GetAttribute(AzureOpenAIServiceAttributes.DeploymentNameKey);
        if (!string.IsNullOrEmpty(serviceModelId) && serviceModelId.StartsWith("gpt-3", StringComparison.OrdinalIgnoreCase))
        {
            Console.WriteLine($"Selected model: {serviceModelId}");
            return (service, new OpenAIRequestSettings());
        }
    }

    throw new SKException("Unable to find AI service for GPT 3.x.");
}
```

## 결정 결과

선택한 옵션: 옵션 1, 구현이 간단하고 모든 가능한 속성을 쉽게 반복할 수 있기 때문입니다.
