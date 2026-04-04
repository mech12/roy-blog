---
# 선택적 요소입니다. 필요 없는 항목은 자유롭게 제거하세요.
status: accepted
date: 2023-11-8
contact: alliscode
deciders: markwallace, mabolan
consulted: SergeyMenshykh
informed:
---

# SKFunction 및 플래너에 더 많은 타입 정보 제공

## 배경 및 문제 설명

현재 Semantic Kernel은 SKFunction의 매개변수에 대해 소량의 정보만 유지하며, SKFunction의 출력에 대한 정보는 전혀 없습니다. 이는 플러그인 함수의 입출력 스키마를 적절히 설명할 수 없기 때문에 플래너의 효과에 큰 부정적 영향을 미칩니다.

플래너는 사용 가능한 플러그인에 대한 설명에 의존하며, 이를 Functions Manual이라고 합니다. 이것은 LLM에 제공되는 사용 설명서로, LLM에게 사용 가능한 함수와 그 사용 방법을 설명하는 것입니다. Sequential 플래너의 현재 Functions Manual 예시는 다음과 같습니다:

```
DatePluginSimpleComplex.GetDate1:
  description: Gets the date with the current date offset by the specified number of days.
  inputs:
    - numDays: The number of days to offset the date by from today. Positive for future, negative for past.

WeatherPluginSimpleComplex.GetWeatherForecast1:
  description: Gets the weather forecast for the specified date and the current location, and time.
  inputs:
    - date: The date for the forecast
```

이 Functions Manual은 LLM에 사용 가능한 두 가지 플러그인 함수를 설명합니다. 하나는 일수 오프셋이 적용된 현재 날짜를 가져오고, 다른 하나는 주어진 날짜의 날씨 예보를 가져옵니다. 고객이 이러한 플러그인 함수로 플래너가 답변할 수 있기를 원하는 간단한 질문은 "내일 날씨 예보는 무엇인가요?"입니다. 이 질문에 답하기 위한 계획을 만들고 실행하려면 첫 번째 함수를 호출한 다음 그 결과를 두 번째 함수의 매개변수로 전달해야 합니다. 의사 코드로 작성하면 계획은 다음과 같습니다:

```csharp
var dateResponse = DatePluginSimpleComplex.GetDate1(1);
var forecastResponse = WeatherPluginSimpleComplex.GetWeatherForecast1(dateResponse);
return forecastResponse;
```

이것은 합리적인 계획으로 보이며, 실제로 Sequential 플래너가 만들어낼 것과 비슷합니다. 첫 번째 함수의 알 수 없는 반환 유형이 두 번째 함수의 알 수 없는 매개변수 유형과 일치하는 한 작동할 수도 있습니다. 그러나 LLM에 제공하는 Functions Manual은 이러한 유형이 일치하는지 알기 위해 필요한 정보를 지정하지 않습니다.

누락된 유형 정보를 제공하는 한 가지 방법은 Json Schema를 사용하는 것입니다. 이는 OpenAPI 스펙이 입출력에 대한 유형 정보를 제공하는 것과 동일한 방법이며, 로컬 및 원격 플러그인에 대한 일관된 솔루션을 제공합니다. Json Schema를 활용하면 Functions Manual은 다음과 같이 될 수 있습니다:

```json
[
  {
    "name": "DatePluginSimpleComplex.GetDate1",
    "description": "Gets the date with the current date offset by the specified number of days.",
    "parameters": {
      "type": "object",
      "required": ["numDays"],
      "properties": {
        "numDays": {
          "type": "integer",
          "description": "The number of days to offset the date by from today. Positive for future, negative for past."
        }
      }
    },
    "responses": {
      "200": {
        "description": "Successful response.",
        "content": {
          "application/json": {
            "schema": {
              "type": "object",
              "properties": { "date": { "type": "string" } },
              "description": "The date."
            }
          }
        }
      }
    }
  },
  {
    "name": "WeatherPluginSimpleComplex.GetWeatherForecast1",
    "description": "Gets the weather forecast for the specified date and the current location, and time.",
    "parameters": {
      "type": "object",
      "required": ["date"],
      "properties": {
        "date": { "type": "string", "description": "The date for the forecast" }
      }
    },
    "responses": {
      "200": {
        "description": "Successful response.",
        "content": {
          "application/json": {
            "schema": {
              "type": "object",
              "properties": { "degreesFahrenheit": { "type": "integer" } },
              "description": "The forecasted temperature in Fahrenheit."
            }
          }
        }
      }
    }
  }
]
```

이 Functions Manual은 LLM이 접근할 수 있는 함수의 입출력에 대해 훨씬 더 많은 정보를 제공합니다. 첫 번째 함수의 출력이 두 번째 함수에 필요한 정보를 포함하는 복잡한 객체임을 알 수 있습니다. 이는 사용되는 토큰 양의 증가를 수반하지만, 유형 정보에서 파생되는 기능 향상이 이 비용을 상쇄합니다. 이 정보가 있으면 LLM이 출력에서 값을 추출하고 입력에 전달하는 방법에 대한 이해를 포함하는 계획을 생성할 것으로 기대할 수 있습니다. 테스트에서 사용한 효과적인 방법 중 하나는 LLM에게 적절한 출력에 대한 Json Path로 입력을 지정하도록 요청하는 것입니다. 의사 코드로 표시한 동등한 계획은 다음과 같습니다:

```csharp
var dateResponse = DatePluginSimpleComplex.GetDate1(1);
var forecastResponse = WeatherPluginSimpleComplex.GetWeatherForecast1(dateResponse.date);
return forecastResponse.degreesFahrenheit;
```

## 제안

위의 Json Schema 기반 예시와 같은 완전한 Functions Manual을 생성할 수 있으려면, SKFunction과 관련 Function View가 매개변수 유형 및 반환 유형에 대한 더 많은 정보를 유지해야 합니다. Function View는 현재 다음과 같은 정의를 가지고 있습니다:

```csharp
public sealed record FunctionView(
    string Name,
    string PluginName,
    string Description = "",
    IReadOnlyList<ParameterView>? Parameters = null)
{
    /// <summary>
    /// 함수 매개변수 목록
    /// </summary>
    public IReadOnlyList<ParameterView> Parameters { get; init; } = Parameters ?? Array.Empty<ParameterView>();
}
```

함수 매개변수는 의미적 설명을 포함하고 더 많은 유형 정보를 추가할 수 있는 `ParameterView` 객체 컬렉션으로 설명됩니다. 그러나 함수 출력의 유형 정보와 의미적 설명을 넣을 기존 위치가 없습니다. 이를 해결하기 위해 `FunctionView`에 `ReturnParameterView`라는 새 속성을 추가합니다:

```csharp
public sealed record FunctionView(
    string Name,
    string PluginName,
    string Description = "",
    IReadOnlyList<ParameterView>? Parameters = null,
    ReturnParameterView? ReturnParameter = null)
{
    /// <summary>
    /// 함수 매개변수 목록
    /// </summary>
    public IReadOnlyList<ParameterView> Parameters { get; init; } = Parameters ?? Array.Empty<ParameterView>();

    /// <summary>
    /// 함수 출력
    /// </summary>
    public ReturnParameterView ReturnParameter { get; init; } = ReturnParameter ?? new ReturnParameterView();
}
```

`ParameterView` 객체는 현재 매개변수 유형에 대한 일부 정보를 포함하는 `ParameterViewType` 속성을 가지고 있지만, JSON 유형([string, number, boolean, null, object, array])으로 제한되며 객체의 구조를 설명할 방법이 없습니다. 필요한 추가 유형 정보를 추가하기 위해 네이티브 `System.Type` 속성을 추가할 수 있습니다. 이는 SKFunction을 임포트할 때 매개변수 Type이 항상 접근 가능하므로 로컬 함수에 잘 작동합니다. LLM 응답에서 네이티브 유형을 하이드레이션하는 데도 필요합니다. 그러나 원격 플러그인의 경우 객체의 네이티브 유형은 알 수 없으며 존재하지 않을 수도 있으므로 `System.Type`은 도움이 되지 않습니다. 이 경우 OpenAPI 명세에서 유형 정보를 추출하고 이전에 알 수 없던 스키마를 허용하는 속성에 저장해야 합니다. 이 속성 유형의 옵션에는 JsonSchema.Net 또는 NJsonSchema와 같은 OSS 라이브러리의 `JsonSchema`, System.Text.Json의 `JsonDocument`, 또는 Json 직렬화된 스키마를 포함하는 `string`이 있습니다.

| 유형                      | 장점                                                         | 단점                                                       |
| ------------------------- | ------------------------------------------------------------ | ---------------------------------------------------------- |
| JsonSchema.Net.JsonSchema | 인기가 높고 업데이트가 빈번하며, System.Net 위에 구축됨 | SK 코어에 OSS 의존성을 가져옴                       |
| NJsonShema.JsonSchema     | 매우 인기가 높고, 빈번한 업데이트, 장기 프로젝트            | Json.Net (Newtonsoft) 위에 구축됨                      |
| JsonDocument              | 네이티브 C# 유형, 빠르고 유연함                            | Json Schema가 아닌 스키마를 위한 Json DOM 컨테이너 |
| String                    | 네이티브 C# 유형                                               | Json Schema도 Json DOM도 아님, 매우 빈약한 유형 힌트      |

코어 추상화 프로젝트에서 타사 라이브러리에 대한 의존성을 피하기 위해, 원격 플러그인 로드 시 생성되는 Json Schema를 보관하는 데 `JsonDocument` 유형을 사용합니다. 이러한 스키마를 생성하거나 추출하는 데 필요한 라이브러리는 이를 필요로 하는 패키지, 즉 Functions.OpenAPI, Planners.Core, Connectors.AI.OpenAI에 포함될 수 있습니다. `NativeType` 속성은 네이티브 함수를 로드할 때 채워지며, 필요할 때 Json Schema를 생성하고 플래너 및 시맨틱 함수에서 LLM 응답으로부터 네이티브 유형을 하이드레이션하는 데 사용됩니다.

```csharp
public sealed record ParameterView(
    string Name,
    string? Description = null,
    string? DefaultValue = null,
    ParameterViewType? Type = null,
    bool? IsRequired = null,
    Type? NativeType = null,
    JsonDocument? Schema = null);
```
