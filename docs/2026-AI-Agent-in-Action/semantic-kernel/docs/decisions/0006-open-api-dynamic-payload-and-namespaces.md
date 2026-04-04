---
status: superseded by [ADR-0062](0062-open-api-payload.md)
contact: SergeyMenshykh
date: 2023-08-15
deciders: shawncal
consulted:
informed:
---

# PUT 및 POST RestAPI 작업을 위한 동적 페이로드 구성과 매개변수 네임스페이싱

## 배경 및 문제 상황

현재 SK OpenAPI는 필요한 모든 메타데이터가 사용 가능함에도 불구하고 PUT 및 POST RestAPI 작업의 페이로드/본문을 동적으로 생성하는 것을 허용하지 않습니다. 이 기능이 원래 완전히 개발되지 않았고 결국 제거된 이유 중 하나는 PUT 및 POST RestAPI 작업의 JSON 페이로드/본문 콘텐츠에 다양한 수준에서 동일한 이름의 속성이 포함될 수 있기 때문입니다. 평면적인 컨텍스트 변수 목록에서 해당 값을 모호하지 않게 해석하는 방법이 명확하지 않았습니다. 이 기능이 아직 추가되지 않은 또 다른 이유는 'payload' 컨텍스트 변수와 RestAPI 작업 데이터 계약 스키마(OpenAPI, JSON 스키마, Typings?)가 있으면 LLM이 동적으로 구성할 필요 없이 완전한 JSON 페이로드/본문 콘텐츠를 제공하기에 충분해야 했기 때문입니다.

<!-- 이 항목은 선택 사항입니다. 필요 없으면 자유롭게 제거하세요. -->

## 결정 동인

- PUT 및 POST RestAPI 작업의 페이로드/본문을 동적으로 구성할 수 있는 메커니즘을 만듭니다.
- PUT 및 POST RestAPI 작업에서 다양한 수준의 동일한 이름을 가진 페이로드 속성을 구분할 수 있는 메커니즘(네임스페이싱)을 개발합니다.
- 가능한 한 호환성을 깨는 변경을 최소화하고 코드의 하위 호환성을 유지합니다.

## 검토된 옵션

- 기본적으로 페이로드의 동적 생성 및/또는 네임스페이싱을 활성화합니다.
- 구성에 따라 페이로드의 동적 생성 및/또는 네임스페이싱을 활성화합니다.

## 결정 결과

선택된 옵션: "구성에 따라 페이로드의 동적 생성 및/또는 네임스페이싱을 활성화". 이 옵션은 호환성을 유지하므로 변경이 어떤 SK 소비자 코드에도 영향을 미치지 않습니다. 또한 SK 소비자 코드가 시나리오에 따라 두 메커니즘을 쉽게 제어하여 켜거나 끌 수 있습니다.

## 추가 세부 사항

### 페이로드 동적 생성 활성화

PUT 및 POST RestAPI 작업의 페이로드/본문 동적 생성을 활성화하려면 AI 플러그인을 임포트할 때 `OpenApiSkillExecutionParameters` 실행 매개변수의 `EnableDynamicPayload` 속성을 `true`로 설정하세요:

```csharp
var plugin = await kernel.ImportPluginFunctionsAsync("<skill name>", new Uri("<chatGPT-plugin>"), new OpenApiSkillExecutionParameters(httpClient) { EnableDynamicPayload = true });
```

다음과 같은 페이로드가 필요한 RestAPI 작업의 페이로드를 동적으로 구성하려면:

```json
{
  "value": "secret-value",
  "attributes": {
    "enabled": true
  }
}
```

다음 인수를 컨텍스트 변수 컬렉션에 등록하세요:

```csharp
var contextVariables = new ContextVariables();
contextVariables.Set("value", "secret-value");
contextVariables.Set("enabled", true);
```

### 네임스페이싱 활성화

네임스페이싱을 활성화하려면 AI 플러그인을 임포트할 때 `OpenApiSkillExecutionParameters` 실행 매개변수의 `EnablePayloadNamespacing` 속성을 `true`로 설정하세요:

```csharp
var plugin = await kernel.ImportPluginFunctionsAsync("<skill name>", new Uri("<chatGPT-plugin>"), new OpenApiSkillExecutionParameters(httpClient) { EnablePayloadNamespacing = true });
```

네임스페이싱 메커니즘은 매개변수 이름 앞에 부모 매개변수 이름을 점으로 구분하여 접두사를 붙이는 것에 의존한다는 것을 기억하세요. 따라서 컨텍스트 변수에 인수를 추가할 때 '네임스페이스된' 매개변수 이름을 사용하세요. 다음 JSON을 고려해 봅시다:

```json
{
  "upn": "<sender upn>",
  "receiver": {
    "upn": "<receiver upn>"
  },
  "cc": {
    "upn": "<cc upn>"
  }
}
```

이 JSON에는 서로 다른 수준에 `upn` 속성이 포함되어 있습니다. 매개변수(속성 값)에 대한 인수 등록은 다음과 같습니다:

```csharp
var contextVariables = new ContextVariables();
contextVariables.Set("upn", "<sender-upn-value>");
contextVariables.Set("receiver.upn", "<receiver-upn-value>");
contextVariables.Set("cc.upn", "<cc-upn-value>");
```
