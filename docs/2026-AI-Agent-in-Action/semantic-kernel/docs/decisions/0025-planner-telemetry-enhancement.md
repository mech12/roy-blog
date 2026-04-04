---
status: { accepted }
contact: { TaoChenOSU }
date: { 2023-11-21 }
deciders: alliscode, dmytrostruk, markwallace, SergeyMenshykh, stephentoub
consulted: {}
informed: {}
---

# 플래너 텔레메트리 강화

## 맥락 및 문제 설명

Semantic Kernel의 플래닝 기능을 사용하는 애플리케이션이 플래너와 계획의 성능을 지속적으로 모니터링하고 디버깅할 수 있다면 매우 유익할 것입니다.

## 시나리오

Contoso는 SK를 사용하여 AI 애플리케이션을 개발하는 회사입니다.

1. Contoso는 프롬프트 토큰, 완성 토큰, 총 토큰을 포함하여 특정 플래너의 토큰 사용량을 지속적으로 모니터링해야 합니다.
2. Contoso는 특정 플래너가 계획을 생성하는 데 걸리는 시간을 지속적으로 모니터링해야 합니다.
3. Contoso는 특정 플래너가 유효한 계획을 생성하는 성공률을 지속적으로 모니터링해야 합니다.
4. Contoso는 특정 계획 유형이 성공적으로 실행되는 성공률을 지속적으로 모니터링해야 합니다.
5. Contoso는 특정 플래너 실행의 토큰 사용량을 확인하고 싶습니다.
6. Contoso는 특정 플래너 실행에서 계획을 생성하는 데 걸린 시간을 확인하고 싶습니다.
7. Contoso는 계획의 단계를 확인하고 싶습니다.
8. Contoso는 각 계획 단계의 입력 및 출력을 확인하고 싶습니다.
9. Contoso는 플래너의 성능에 영향을 줄 수 있는 몇 가지 설정을 변경하려고 합니다. 변경 사항을 적용하기 전에 성능이 어떻게 영향을 받는지 알고 싶습니다.
10. Contoso는 더 저렴하고 빠른 새 모델로 업데이트하려고 합니다. 새 모델이 플래닝 작업에서 어떻게 수행되는지 알고 싶습니다.

## 범위 밖

1. Application Insights로 텔레메트리를 전송하는 방법에 대한 예시를 제공합니다. 다른 텔레메트리 서비스 옵션은 기술적으로 지원되지만, 이 ADR에서 설정하는 가능한 방법을 다루지 않습니다.
2. 이 ADR은 SK의 현재 계측(instrumentation) 설계를 수정하려는 것이 아닙니다.
3. 토큰 사용량을 반환하지 않는 서비스는 고려하지 않습니다.

## 결정 요인

- 프레임워크는 텔레메트리 서비스에 구애받지 않아야 합니다.
- SK에서 다음 메트릭이 출력되어야 합니다:
  - 프롬프트에 대한 입력 토큰 사용량 (프롬프트)
    - 설명: 프롬프트는 토큰을 소비하는 가장 작은 단위입니다 (`KernelFunctionFromPrompt`).
    - 차원: ComponentType, ComponentName, Service ID, Model ID
    - 유형: Histogram
    - 예시:
      | ComponentType | ComponentName | Service ID | Model ID | Value |
      |---|---|---|---|---|
      | Function | WritePoem | | GPT-3.5-Turbo | 40
      | Function | TellJoke | | GPT-4 | 50
      | Function | WriteAndTellJoke | | GPT-3.5-Turbo | 30
      | Planner | CreateHandlebarsPlan | | GPT-3.5-Turbo | 100
  - 프롬프트에 대한 출력 토큰 사용량 (완성)
    - 설명: 프롬프트는 토큰을 소비하는 가장 작은 단위입니다 (`KernelFunctionFromPrompt`).
    - 차원: ComponentType, ComponentName, Service ID, Model ID
    - 유형: Histogram
    - 예시:
      | ComponentType | ComponentName | Service ID | Model ID | Value |
      |---|---|---|---|---|
      | Function | WritePoem | | GPT-3.5-Turbo | 40
      | Function | TellJoke | | GPT-4 | 50
      | Function | WriteAndTellJoke | | GPT-3.5-Turbo | 30
      | Planner | CreateHandlebarsPlan | | GPT-3.5-Turbo | 100
  - 함수에 대한 집계된 실행 시간
    - 설명: 함수는 0개 이상의 프롬프트로 구성될 수 있습니다. 함수의 실행 시간은 함수의 `invoke` 호출 시작부터 끝까지의 기간입니다.
    - 차원: ComponentType, ComponentName, Service ID, Model ID
    - 유형: Histogram
    - 예시:
      | ComponentType | ComponentName | Value |
      |---|---|---|
      | Function | WritePoem | 1m
      | Function | TellJoke | 1m
      | Function | WriteAndTellJoke | 1.5m
      | Planner | CreateHandlebarsPlan | 2m
  - 플래너에 대한 성공/실패 횟수
    - 설명: 플래너 실행은 유효한 계획을 생성할 때 성공한 것으로 간주됩니다. 모델 응답이 원하는 형식의 계획으로 성공적으로 파싱되고 하나 이상의 단계를 포함할 때 계획은 유효합니다.
    - 차원: ComponentType, ComponentName, Service ID, Model ID
    - 유형: Counter
    - 예시:
      | ComponentType | ComponentName | Fail | Success
      |---|---|---|---|
      | Planner | CreateHandlebarsPlan | 5 | 95
      | Planner | CreateHSequentialPlan | 20 | 80
  - 계획에 대한 성공/실패 횟수
    - 설명: 계획 실행은 계획의 모든 단계가 성공적으로 실행될 때 성공한 것으로 간주됩니다.
    - 차원: ComponentType, ComponentName, Service ID, Model ID
    - 유형: Counter
    - 예시:
      | ComponentType | ComponentName | Fail | Success
      |---|---|---|---|
      | Plan | HandlebarsPlan | 5 | 95
      | Plan | SequentialPlan | 20 | 80

## 검토한 옵션

- 함수 훅
  - 함수가 호출되기 전이나 후에 실행될 로직을 함수에 주입합니다.
- 계측(Instrumentation)
  - 로깅
  - 메트릭
  - 트레이스

## 기타 고려 사항

SK는 현재 커넥터에서 토큰 사용량 메트릭을 추적하지만, 이러한 메트릭은 분류되지 않습니다. 따라서 개발자는 다른 작업에 대한 토큰 사용량을 결정할 수 없습니다. 이 문제를 해결하기 위해 다음 두 가지 접근 방식을 제안합니다:

- 상향식(Bottom-up): 커넥터에서 함수로 토큰 사용량 정보를 전파합니다.
- 하향식(Top-down): 함수 정보를 커넥터로 전파하여 함수 정보로 메트릭 항목에 태그를 지정할 수 있게 합니다.

다음과 같은 이유로 상향식 접근 방식을 구현하기로 결정했습니다:

1. SK는 이미 `ContentBase`를 통해 커넥터에서 토큰 사용량 정보를 전파하도록 구성되어 있습니다. 모델 정보와 같이 전파해야 할 항목 목록을 확장하기만 하면 됩니다.
2. 현재 SK에는 함수 정보를 커넥터 수준으로 전달하는 방법이 없습니다. 하향 정보 전파 수단으로 [baggage](https://opentelemetry.io/docs/concepts/signals/baggage/#:~:text=In%20OpenTelemetry%2C%20Baggage%20is%20contextual%20information%20that%E2%80%99s%20passed,available%20to%20any%20span%20created%20within%20that%20trace.)를 사용하는 것을 고려했지만, OpenTelemetry 팀의 전문가들이 보안 문제로 이 접근 방식을 권장하지 않았습니다.

상향식 접근 방식으로 메타데이터에서 토큰 사용량 정보를 검색해야 합니다:

```csharp
// 모든 서비스가 사용량 세부 정보를 지원하는 것은 아닙니다.
/// <summary>
/// 토큰 정보를 포함한 사용량 세부 정보를 캡처합니다.
/// </summary>
private void CaptureUsageDetails(string? modelId, IDictionary<string, object?>? metadata, ILogger logger)
{
  if (string.IsNullOrWhiteSpace(modelId))
  {
    logger.LogWarning("No model ID provided to capture usage details.");
    return;
  }

  if (metadata is null)
  {
    logger.LogWarning("No metadata provided to capture usage details.");
    return;
  }

  if (!metadata.TryGetValue("Usage", out object? usageObject) || usageObject is null)
  {
    logger.LogWarning("No usage details provided to capture usage details.");
    return;
  }

  var promptTokens = 0;
  var completionTokens = 0;
  try
  {
    var jsonObject = JsonElement.Parse(JsonSerializer.Serialize(usageObject));
    promptTokens = jsonObject.GetProperty("PromptTokens").GetInt32();
    completionTokens = jsonObject.GetProperty("CompletionTokens").GetInt32();
  }
  catch (Exception ex) when (ex is KeyNotFoundException)
  {
    logger.LogInformation("Usage details not found in model result.");
  }
  catch (Exception ex)
  {
    logger.LogError(ex, "Error while parsing usage details from model result.");
    throw;
  }

  logger.LogInformation(
    "Prompt tokens: {PromptTokens}. Completion tokens: {CompletionTokens}.",
    promptTokens, completionTokens);

  TagList tags = new() {
    { "semantic_kernel.function.name", this.Name },
    { "semantic_kernel.function.model_id", modelId }
  };

  s_invocationTokenUsagePrompt.Record(promptTokens, in tags);
  s_invocationTokenUsageCompletion.Record(completionTokens, in tags);
}
```

> 토큰 사용량을 반환하지 않는 서비스는 고려하지 않습니다. 현재 OpenAI 및 Azure OpenAI 서비스만 토큰 사용량 정보를 반환합니다.

## 결정 결과

1. 새로운 메트릭 이름:
   | Meter | Metrics |
   |---|---|
   |Microsoft.SemanticKernel.Planning| <ul><li>semantic_kernel.planning.invoke_plan.duration</li></ul> |
   |Microsoft.SemanticKernel| <ul><li>semantic_kernel.function.invocation.token_usage.prompt</li><li>semantic_kernel.function.invocation.token_usage.completion</li></ul> |
   > 참고: 모호함을 방지하기 위해 모든 기존 메트릭의 "sk" 접두사를 "semantic_kernel"로 교체합니다.
2. 계측(Instrumentation)

## 검증

예상되는 모든 텔레메트리 항목이 올바른 형식으로 존재하는지 확인하는 테스트를 추가할 수 있습니다.

## 옵션 설명

### 함수 훅

함수 훅은 개발자가 함수가 호출되기 전이나 후에 실행될 로직을 커널에 주입할 수 있게 합니다. 예시 사용 사례로는 함수가 호출되기 전에 함수 입력을 로깅하고, 함수가 반환된 후 결과를 로깅하는 것이 있습니다.
자세한 내용은 다음 ADR을 참조하세요:

1. [Kernel Hooks Phase 1](./0005-kernel-hooks-phase1.md)
2. [Kernel Hooks Phase 2](./0018-kernel-hooks-phase2.md)

함수 등록 시 모든 함수에 대한 중요 정보를 로깅하기 위해 기본 콜백을 주입할 수 있습니다.

장점:

1. 개발자에게 최대한의 노출과 유연성을 제공합니다. 즉, 앱 개발자가 더 많은 콜백을 추가하여 개별 함수에 대한 추가 정보를 매우 쉽게 로깅할 수 있습니다.

단점:

1. 메트릭을 생성하지 않으며 결과를 집계하기 위한 추가 작업이 필요합니다.
2. 로그에만 의존하면 트레이스 세부 정보를 제공하지 않습니다.
3. 로그는 더 자주 수정되어 불안정한 구현으로 이어지고 추가 유지 관리가 필요할 수 있습니다.
4. 훅은 제한된 함수 데이터에만 접근할 수 있습니다.

> 참고: SK에 이미 구현된 분산 추적으로, 개발자는 훅 내에서 사용자 정의 텔레메트리를 생성할 수 있으며, 텔레메트리 서비스가 구성되면 정보가 사용 가능한 한 전송됩니다. 그러나 훅 내에서 생성된 텔레메트리 항목은 함수의 범위 밖에 있으므로 부모-자식 관계로 함수와 상관되지 않습니다.

### 분산 추적

분산 추적은 분산 애플리케이션 내에서 장애와 성능 병목을 지역화할 수 있는 진단 기법입니다. .Net은 라이브러리에 분산 추적을 추가하기 위한 네이티브 지원을 가지고 있으며 .Net 라이브러리도 자동으로 분산 추적 정보를 생성하도록 계측되어 있습니다.

자세한 내용은 이 문서를 참조하세요: [.Net 분산 추적](https://learn.microsoft.com/en-us/dotnet/core/diagnostics/)

전체 장점:

1. 네이티브 .Net 지원.
2. SK에 분산 추적이 이미 구현되어 있습니다. 더 많은 텔레메트리만 추가하면 됩니다.
3. [OpenTelemetry](https://opentelemetry.io/docs/what-is-opentelemetry/)로 텔레메트리 서비스에 구애받지 않습니다.

전체 단점:

1. SK를 라이브러리로 사용하는 앱 개발자가 사용자 정의 트레이스와 메트릭을 추가하는 유연성이 적습니다.

#### 로깅

로그는 코드가 실행되는 동안 흥미로운 이벤트를 기록하는 데 사용됩니다.

```csharp
// 최적의 성능을 위해 LoggerMessage 속성 사용
this._logger.LogPlanCreationStarted();
this._logger.LogPlanCreated();
```

#### [메트릭](https://learn.microsoft.com/en-us/dotnet/core/diagnostics/metrics)

메트릭은 시간에 따른 측정값을 기록하는 데 사용됩니다.

```csharp
/// <summary>함수 관련 메트릭을 위한 <see cref="Meter"/>.</summary>
private static readonly Meter s_meter = new("Microsoft.SemanticKernel");

/// <summary>계획 실행 기간을 기록하기 위한 <see cref="Histogram{T}"/>.</summary>
private static readonly Histogram<double> s_planExecutionDuration =
  s_meter.CreateHistogram<double>(
    name: "semantic_kernel.planning.invoke_plan.duration",
    unit: "s",
    description: "Duration time of plan execution.");

TagList tags = new() { { "semantic_kernel.plan.name", planName } };

try
{
  ...
}
catch (Exception ex)
{
  // 측정값에 "error.type" 태그가 지정되면 실패입니다.
  tags.Add("error.type", ex.GetType().FullName);
}

s_planExecutionDuration.Record(duration.TotalSeconds, in tags);
```

#### [트레이스](https://learn.microsoft.com/en-us/dotnet/core/diagnostics/distributed-tracing)

Activity는 애플리케이션을 통한 의존성을 추적하고, 다른 컴포넌트에서 수행한 작업과 상관시키며, 트레이스라고 하는 Activity 트리를 형성하는 데 사용됩니다.

```csharp
ActivitySource s_activitySource = new("Microsoft.SemanticKernel");

// Activity 생성 및 시작
using var activity = s_activitySource.StartActivity(this.Name);

// 최적의 성능을 위해 LoggerMessage 속성 사용
logger.LoggerGoal(goal);
logger.LoggerPlan(plan);
```

> 참고: 트레이스 로그에는 민감한 데이터가 포함되며 프로덕션에서는 끄야 합니다: https://learn.microsoft.com/en-us/dotnet/core/extensions/logging?tabs=command-line#log-level

## 애플리케이션이 Application Insights로 텔레메트리를 전송하는 방법 예시

```csharp
using var traceProvider = Sdk.CreateTracerProviderBuilder()
  .AddSource("Microsoft.SemanticKernel*")
  .AddAzureMonitorTraceExporter(options => options.ConnectionString = connectionString)
  .Build();

using var meterProvider = Sdk.CreateMeterProviderBuilder()
  .AddMeter("Microsoft.SemanticKernel*")
  .AddAzureMonitorMetricExporter(options => options.ConnectionString = connectionString)
  .Build();

using var loggerFactory = LoggerFactory.Create(builder =>
{
  // 로깅 제공자로 OpenTelemetry 추가
  builder.AddOpenTelemetry(options =>
  {
    options.AddAzureMonitorLogExporter(options => options.ConnectionString = connectionString);
    // 로그 메시지 형식 지정. 기본값은 false입니다.
    options.IncludeFormattedMessage = true;
  });
  builder.SetMinimumLevel(MinLogLevel);
});
```

## 추가 정보

수행해야 할 추가 작업:

1. [텔레메트리 문서](../../dotnet/docs/TELEMETRY.md) 업데이트
