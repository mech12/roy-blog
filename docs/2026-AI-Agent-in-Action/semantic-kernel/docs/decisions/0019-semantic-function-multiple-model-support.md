---
# 이 항목들은 선택 사항입니다. 필요 없는 항목은 자유롭게 삭제하세요.
status: approved
contact: markwallace-microsoft
date: 2023-10-26
deciders: markwallace-microsoft, SergeyMenshykh, rogerbarreto
consulted: matthewbolanos, dmytrostruk
informed:
---

# 시맨틱 함수의 다중 모델 지원

## 맥락 및 문제 설명

개발자는 비용을 줄이기 위해 특정 프롬프트에는 GPT4를, 다른 프롬프트에는 GPT3.5를 사용하는 등 여러 모델을 동시에 사용할 수 있어야 합니다.

## 사용 사례

Semantic Kernel V1.0의 범위에는 AI 서비스 및 모델 요청 설정을 선택하는 기능이 포함됩니다:

1. 서비스 ID로 선택.
   - 서비스 ID는 등록된 AI 서비스를 고유하게 식별하며, 일반적으로 애플리케이션 범위에서 정의됩니다.
1. 개발자 정의 전략으로 선택.
   - _개발자 정의 전략_은 개발자가 로직을 제공하는 코드 우선 접근 방식입니다.
1. 모델 ID로 선택.
   - 모델 ID는 대규모 언어 모델을 고유하게 식별합니다. 여러 AI 서비스 제공자가 동일한 LLM을 지원할 수 있습니다.
1. 임의의 AI 서비스 속성으로 선택
   - 예를 들어, AI 서비스는 AI 제공자를 고유하게 식별하는 프로바이더 ID를 정의할 수 있습니다. 예: "Azure OpenAI", "OpenAI", "Hugging Face"

**이 ADR은 위 목록의 항목 1과 2에 초점을 맞춥니다. 항목 3과 4를 구현하려면 `AIService` 메타데이터를 저장하는 기능을 제공해야 합니다.**

## 결정 결과

이 ADR에 나열된 사용 사례 1과 2를 지원하고, AI 서비스 메타데이터 지원 추가를 위한 별도의 ADR을 작성합니다.

## 사용 사례 설명

**참고: 모든 코드는 의사 코드이며 최종 구현의 모습을 정확히 반영하지 않습니다.**

### 서비스 ID로 모델 요청 설정 선택

_Semantic Kernel을 사용하는 개발자로서, 시맨틱 함수에 대해 여러 요청 설정을 구성하고 각각을 서비스 ID와 연결하여, 다른 서비스가 시맨틱 함수를 실행할 때 올바른 요청 설정이 사용되도록 할 수 있습니다._

시맨틱 함수 템플릿 구성은 여러 모델 요청 설정을 구성할 수 있습니다. 이 경우 개발자는 시맨틱 함수를 실행하는 데 사용되는 서비스 ID에 따라 다른 설정을 구성합니다.
아래 예시에서 시맨틱 함수는 "AzureText"가 프롬프트에 구성된 모델 목록에서 첫 번째 서비스 ID이므로 `max_tokens=60`으로 "AzureText"를 사용하여 실행됩니다.

```csharp
// 여러 LLM으로 Kernel 구성
IKernel kernel = new KernelBuilder()
    .WithLoggerFactory(ConsoleLogger.LoggerFactory)
    .WithAzureTextCompletionService(deploymentName: aoai.DeploymentName,
        endpoint: aoai.Endpoint, serviceId: "AzureText", apiKey: aoai.ApiKey)
    .WithAzureChatCompletionService(deploymentName: aoai.ChatDeploymentName,
        endpoint: aoai.Endpoint, serviceId: "AzureChat", apiKey: aoai.ApiKey)
    .WithOpenAITextCompletionService(modelId: oai.ModelId,
        serviceId: "OpenAIText", apiKey: oai.ApiKey, setAsDefault: true)
    .WithOpenAIChatCompletionService(modelId: oai.ChatModelId,
        serviceId: "OpenAIChat", apiKey: oai.ApiKey, setAsDefault: true)
    .Build();

// 여러 LLM 요청 설정으로 시맨틱 함수 구성
var modelSettings = new List<AIRequestSettings>
{
    new OpenAIRequestSettings() { ServiceId = "AzureText", MaxTokens = 60 },
    new OpenAIRequestSettings() { ServiceId = "AzureChat", MaxTokens = 120 },
    new OpenAIRequestSettings() { ServiceId = "OpenAIText", MaxTokens = 180 },
    new OpenAIRequestSettings() { ServiceId = "OpenAIChat", MaxTokens = 240 }
};
var prompt = "Hello AI, what can you do for me?";
var promptTemplateConfig = new PromptTemplateConfig() { ModelSettings = modelSettings };
var func = kernel.CreateSemanticFunction(prompt, config: promptTemplateConfig, "HelloAI");

// 시맨틱 함수가 AzureText를 사용하여 max_tokens=60으로 실행됩니다
result = await kernel.RunAsync(func);
```

이것은 시맨틱 함수를 호출할 때 사용할 AI 서비스와 요청 설정을 선택하는 전략으로 `IAIServiceSelector` 인터페이스를 사용하여 작동합니다.
인터페이스는 다음과 같이 정의됩니다:

```csharp
public interface IAIServiceSelector
{
    (T?, AIRequestSettings?) SelectAIService<T>(
                            string renderedPrompt,
                            IAIServiceProvider serviceProvider,
                            IReadOnlyList<AIRequestSettings>? modelSettings) where T : IAIService;
}
```

기본 `OrderedIAIServiceSelector` 구현이 제공되며, 시맨틱 함수에 정의된 모델 요청 설정의 순서에 따라 AI 서비스를 선택합니다.

- 구현은 해당 서비스 ID를 가진 서비스가 존재하는지 확인하고, 존재하면 해당 서비스와 관련 모델 요청 설정이 사용됩니다.
- 모델 요청 설정이 정의되지 않으면 기본 텍스트 완성 서비스가 사용됩니다.
- 서비스 ID를 정의하지 않거나 비워두면 기본 요청 설정을 지정할 수 있으며, 첫 번째 기본값이 사용됩니다.
- 기본값이 지정되지 않고 지정된 서비스 중 사용 가능한 것이 없으면 작업이 실패합니다.

### 개발자 정의 전략으로 AI 서비스 및 모델 요청 설정 선택

_Semantic Kernel을 사용하는 개발자로서, 함수를 실행하는 데 사용되는 AI 서비스와 요청 설정을 선택하는 구현을 제공하여, 시맨틱 함수 실행에 사용되는 AI 서비스와 설정을 동적으로 제어할 수 있습니다._

이 경우 개발자는 서비스 ID에 따라 다른 설정을 구성하고, 시맨틱 함수가 실행될 때 어떤 AI 서비스를 사용할지 결정하는 AI 서비스 선택기를 제공합니다.
아래 예시에서 시맨틱 함수는 `MyAIServiceSelector`가 반환하는 AI 서비스와 AI 요청 설정으로 실행됩니다. 예를 들어, 렌더링된 프롬프트의 토큰 수를 계산하고 이를 기반으로 사용할 서비스를 결정하는 AI 서비스 선택기를 만들 수 있습니다.

```csharp
// 여러 LLM으로 Kernel 구성
IKernel kernel = new KernelBuilder()
    .WithLoggerFactory(ConsoleLogger.LoggerFactory)
    .WithAzureTextCompletionService(deploymentName: aoai.DeploymentName,
        endpoint: aoai.Endpoint, serviceId: "AzureText", apiKey: aoai.ApiKey)
    .WithAzureChatCompletionService(deploymentName: aoai.ChatDeploymentName,
        endpoint: aoai.Endpoint, serviceId: "AzureChat", apiKey: aoai.ApiKey)
    .WithOpenAITextCompletionService(modelId: oai.ModelId,
        serviceId: "OpenAIText", apiKey: oai.ApiKey, setAsDefault: true)
    .WithOpenAIChatCompletionService(modelId: oai.ChatModelId,
        serviceId: "OpenAIChat", apiKey: oai.ApiKey, setAsDefault: true)
    .WithAIServiceSelector(new MyAIServiceSelector())
    .Build();

// 여러 LLM 요청 설정으로 시맨틱 함수 구성
var modelSettings = new List<AIRequestSettings>
{
    new OpenAIRequestSettings() { ServiceId = "AzureText", MaxTokens = 60 },
    new OpenAIRequestSettings() { ServiceId = "AzureChat", MaxTokens = 120 },
    new OpenAIRequestSettings() { ServiceId = "OpenAIText", MaxTokens = 180 },
    new OpenAIRequestSettings() { ServiceId = "OpenAIChat", MaxTokens = 240 }
};
var prompt = "Hello AI, what can you do for me?";
var promptTemplateConfig = new PromptTemplateConfig() { ModelSettings = modelSettings };
var func = kernel.CreateSemanticFunction(prompt, config: promptTemplateConfig, "HelloAI");

// 시맨틱 함수가 동적으로 결정된 AI 서비스와 AI 요청 설정으로 실행됩니다
result = await kernel.RunAsync(func, funcVariables);
```

## 추가 정보

### 서비스 ID로 AI 서비스 선택

다음 사용 사례가 지원됩니다. 개발자는 여러 명명된 AI 서비스로 `Kernel` 인스턴스를 생성할 수 있습니다. 시맨틱 함수를 호출할 때 서비스 ID(및 선택적으로 사용할 요청 설정)를 지정할 수 있습니다. 명명된 AI 서비스가 프롬프트를 실행하는 데 사용됩니다.

```csharp
var aoai = TestConfiguration.AzureOpenAI;
var oai = TestConfiguration.OpenAI;

// 여러 LLM으로 Kernel 구성
IKernel kernel = Kernel.Builder
    .WithLoggerFactory(ConsoleLogger.LoggerFactory)
    .WithAzureTextCompletionService(deploymentName: aoai.DeploymentName,
        endpoint: aoai.Endpoint, serviceId: "AzureText", apiKey: aoai.ApiKey)
    .WithAzureChatCompletionService(deploymentName: aoai.ChatDeploymentName,
        endpoint: aoai.Endpoint, serviceId: "AzureChat", apiKey: aoai.ApiKey)
    .WithOpenAITextCompletionService(modelId: oai.ModelId,
        serviceId: "OpenAIText", apiKey: oai.ApiKey)
    .WithOpenAIChatCompletionService(modelId: oai.ChatModelId,
        serviceId: "OpenAIChat", apiKey: oai.ApiKey)
    .Build();

// 시맨틱 함수를 호출하고 사용할 서비스와 요청 설정을 지정
result = await kernel.InvokeSemanticFunctionAsync(prompt,
    requestSettings: new OpenAIRequestSettings()
        { ServiceId = "AzureText", MaxTokens = 60 });

result = await kernel.InvokeSemanticFunctionAsync(prompt,
    requestSettings: new OpenAIRequestSettings()
        { ServiceId = "AzureChat", MaxTokens = 120 });

result = await kernel.InvokeSemanticFunctionAsync(prompt,
    requestSettings: new OpenAIRequestSettings()
        { ServiceId = "OpenAIText", MaxTokens = 180 });

result = await kernel.InvokeSemanticFunctionAsync(prompt,
    requestSettings: new OpenAIRequestSettings()
        { ServiceId = "OpenAIChat", MaxTokens = 240 });
```
