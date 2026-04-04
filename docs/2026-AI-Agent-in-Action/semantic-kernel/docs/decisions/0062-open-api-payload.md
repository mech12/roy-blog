---
status: proposed
contact: sergeymenshykh
date: 2024-10-25
deciders: dmytrostruk, markwallace, rbarreto, sergeymenshykh, westey-m, 
---

# OpenAPI 함수에 페이로드 제공하기

## 맥락과 문제 설명
현재 SK OpenAPI 함수의 페이로드는 호출자가 제공하거나 SK가 OpenAPI 문서 메타데이터와 제공된 인수로부터 동적으로 구성할 수 있습니다.

이 ADR은 OpenAPI 기능이 현재 페이로드를 처리하는 기존 옵션의 개요를 제공하고 복잡한 페이로드의 동적 생성을 간소화하기 위한 새로운 옵션을 제안합니다.

## SK에서 페이로드를 처리하기 위한 기존 옵션 개요

### 1. `payload`와 `content-type` 인수
이 옵션은 호출자가 OpenAPI 스키마에 맞는 페이로드를 생성하고 OpenAPI 함수를 호출할 때 인수로 전달할 수 있게 합니다.
```csharp
// createEvent 함수가 있는 OpenAPI 플러그인을 가져오고 동적 페이로드 구성을 비활성화합니다
KernelPlugin plugin = await kernel.ImportPluginFromOpenApiAsync("<plugin-name>", new Uri("<plugin-uri>"), new OpenApiFunctionExecutionParameters 
{ 
    EnableDynamicPayload = false 
});

// createEvent 함수를 위한 페이로드 생성
string payload = """
{
    "subject": "IT Meeting",
    "start": {
        "dateTime": "2023-10-01T10:00:00",
        "timeZone": "UTC"
    },
    "end": {
        "dateTime": "2023-10-01T11:00:00",
        "timeZone": "UTC"
    },
    "tags": [
        { "name": "IT" },
        { "name": "Meeting" }
    ]
}
""";

// createEvent 함수를 위한 인수 생성
KernelArguments arguments = new ()
{
    ["payload"] = payload,
    ["content-type"] = "application/json"
};

// createEvent 함수 호출
FunctionResult functionResult = await kernel.InvokeAsync(plugin["createEvent"], arguments);
```

Semantic Kernel은 페이로드를 어떤 방식으로도 검증하거나 수정하지 않습니다. 페이로드가 유효하고 OpenAPI 스키마에 맞는지 확인하는 것은 호출자의 책임입니다.


### 2. 리프 속성으로부터의 동적 페이로드 구성
이 옵션은 SK가 OpenAPI 스키마와 제공된 인수를 기반으로 페이로드를 동적으로 구성할 수 있게 합니다.
호출자는 OpenAPI 함수를 호출할 때 페이로드를 제공할 필요가 없습니다. 그러나 호출자는 동일한 이름의 페이로드 속성 값으로 사용될 인수를 제공해야 합니다.
```csharp
// createEvent 함수가 있는 OpenAPI 플러그인을 가져오고 동적 페이로드 구성을 비활성화합니다
KernelPlugin plugin = await kernel.ImportPluginFromOpenApiAsync("<plugin-name>", new Uri("<plugin-uri>"), new OpenApiFunctionExecutionParameters 
{ 
    EnableDynamicPayload = true // 기본값은 true입니다
});

// 예상 페이로드 구조
//{
//    "subject": "...",
//    "start": {
//        "dateTime": "...",
//        "timeZone": "..."
//     },
//    "duration": "PT1H",
//    "tags":[{
//        "name": "...",
//      }
//    ],
//}

// createEvent 함수를 위한 인수 생성
KernelArguments arguments = new()
{
    ["subject"] = "IT Meeting",
    ["dateTime"] = DateTimeOffset.Parse("2023-10-01T10:00:00"),
    ["timeZone"] = "UTC",
    ["duration"] = "PT1H",
    ["tags"] = new[] { new Tag("work"), new Tag("important") }
};

// createEvent 함수 호출
FunctionResult functionResult = await kernel.InvokeAsync(plugin["createEvent"], arguments);
```

이 옵션은 루트 속성에서 시작하여 아래로 내려가면서 페이로드 스키마를 순회하고, 도중에 모든 리프 속성(자식 속성이 없는 속성)을 수집합니다.
호출자는 식별된 리프 속성에 대한 인수를 제공해야 하며, SK는 스키마와 제공된 인수를 기반으로 페이로드를 구성합니다.

이 옵션에는 서로 다른 수준에서 동일한 이름을 가진 속성이 포함된 페이로드를 생성할 때 제한이 있습니다.
가져오기 프로세스가 각 OpenAPI 작업에 대한 커널 함수를 생성한다는 점을 고려하면, 동일한 이름을 가진 매개변수가 둘 이상인 커널 함수를 생성하는 실행 가능한 방법이 없습니다.
이러한 페이로드를 가진 플러그인을 가져오려고 시도하면 다음 오류가 발생합니다: "The function has two or more parameters with the same name `<property-name>`."

또한 두 개 이상의 속성이 서로를 참조하여 루프를 생성하는 순환 참조가 페이로드 스키마에서 발생할 가능성이 있습니다.
SK는 이러한 순환 참조를 감지하고 오류를 발생시켜 작업 가져오기에 실패합니다.

이 옵션의 또 다른 특성은 배열 속성을 순회하지 않고 리프 속성으로 간주한다는 것입니다.
이는 호출자가 배열 타입의 속성에 대한 인수를 제공해야 하지만, 배열 요소나 배열 요소의 속성에 대해서는 제공하지 않아야 함을 의미합니다.
위의 예에서, 객체 배열은 "tags" 배열 속성에 대한 인수로 제공되어야 합니다.

### 3. 네임스페이스를 사용한 리프 속성으로부터의 동적 페이로드 구성
이 옵션은 서로 다른 수준에서 동일한 이름을 가진 속성을 처리하는 것과 관련하여 위에서 설명한 동적 페이로드 구성 옵션의 제한을 해결합니다.
자식 속성 이름 앞에 부모 속성 이름을 추가하여 효과적으로 고유한 이름을 만듭니다.
호출자는 여전히 속성에 대한 인수를 제공해야 하며, SK가 나머지를 처리합니다.
```csharp
// createEvent 함수가 있는 OpenAPI 플러그인을 가져오고 동적 페이로드 구성을 비활성화합니다
KernelPlugin plugin = await kernel.ImportPluginFromOpenApiAsync("<plugin-name>", new Uri("<plugin-uri>"), new OpenApiFunctionExecutionParameters 
{ 
    EnableDynamicPayload = true,
    EnablePayloadNamespacing = true
});


// 예상 페이로드 구조
//{
//    "subject": "...",
//    "start": {
//        "dateTime": "...",
//        "timeZone": "..."
//    },
//    "end": {
//        "dateTime": "...",
//        "timeZone": "..."
//    },
//    "tags":[{
//        "name": "...",
//      }
//    ],
//}

// createEvent 함수를 위한 인수 생성
KernelArguments arguments = new()
{
    ["subject"] = "IT Meeting",
    ["start.dateTime"] = DateTimeOffset.Parse("2023-10-01T10:00:00"),
    ["start.timeZone"] = "UTC",
    ["end.dateTime"] = DateTimeOffset.Parse("2023-10-01T11:00:00"),
    ["end.timeZone"] = "UTC",
    ["tags"] = new[] { new Tag("work"), new Tag("important") }
};

// createEvent 함수 호출
FunctionResult functionResult = await kernel.InvokeAsync(plugin["createEvent"], arguments);
```

이 옵션은 이전 옵션과 마찬가지로 루트 속성에서 아래로 모든 리프 속성을 수집하기 위해 페이로드 스키마를 순회합니다. 리프 속성이 발견되면, SK는 부모 속성을 확인합니다.
부모가 존재하면, 리프 속성 이름 앞에 부모 속성 이름을 점으로 구분하여 추가하여 고유한 이름을 만듭니다.
예를 들어, `start` 객체의 `dateTime` 속성은 `start.dateTime`으로 이름이 지정됩니다.

이 옵션은 이전 옵션과 동일한 방식으로 배열 속성을 처리하여 리프 속성으로 간주하므로, 호출자가 해당 인수를 제공해야 합니다.

이 옵션도 페이로드 스키마의 순환 참조에 영향을 받으며, SK가 순환 참조를 감지하면 작업 가져오기에 실패합니다.

## SK에서 페이로드를 처리하기 위한 새로운 옵션

### 맥락과 문제 설명
SK는 페이로드를 동적으로 구성하고 이 책임을 호출자에게서 덜어주기 위해 많은 노력을 기울입니다.

그러나 기존 옵션 중 어느 것도 서로 다른 수준에서 동일한 이름을 가진 속성이 포함된 페이로드에 대해 네임스페이스를 사용하는 것이 옵션이 아닌 복잡한 시나리오에 적합하지 않습니다.

이러한 시나리오를 커버하기 위해 SK에서 페이로드를 처리하기 위한 새로운 옵션을 제안합니다.

### 검토한 옵션

- 옵션 #4: 루트 속성으로부터 페이로드 구성

### 옵션 #4: 루트 속성으로부터의 동적 페이로드 구성

페이로드에 동일한 이름의 속성이 포함되어 있고 다양한 이유로 네임스페이스를 사용할 수 없는 경우가 있을 수 있습니다. 페이로드 구성의 책임을 호출자에게 넘기지 않기 위해, SK는 추가 단계를 수행하여 루트 속성으로부터 페이로드를 구성할 수 있습니다. 물론 해당 루트 속성에 대한 인수를 구축하는 복잡성은 호출자 측에 있지만, 네임스페이스 사용이 허용되지 않고 서로 다른 수준에서 동일한 이름의 속성에 대한 인수를 커널 인수의 플랫 목록에서 해결해야 하는 경우 SK가 할 수 있는 것은 많지 않습니다.

```csharp
// createEvent 함수가 있는 OpenAPI 플러그인을 가져오고 동적 페이로드 구성을 비활성화합니다
KernelPlugin plugin = await kernel.ImportPluginFromOpenApiAsync("<plugin-name>", new Uri("<plugin-uri>"), new OpenApiFunctionExecutionParameters { EnableDynamicPayload = false, EnablePayloadNamespacing = true });

// 예상 페이로드 구조
//{
//    "subject": "...",
//    "start": {
//        "dateTime": "...",
//        "timeZone": "..."
//    },
//    "end": {
//        "dateTime": "...",
//        "timeZone": "..."
//    },
//    "tags":[{
//        "name": "...",
//      }
//    ],
//}

// createEvent 함수를 위한 인수 생성
KernelArguments arguments = new()
{
    ["subject"] = "IT Meeting",
    ["start"] = new MeetingTime() { DateTime = DateTimeOffset.Parse("2023-10-01T10:00:00"), TimeZone = TimeZoneInfo.Utc },
    ["end"] = new MeetingTime() { DateTime = DateTimeOffset.Parse("2023-10-01T10:00:00"), TimeZone = TimeZoneInfo.Utc },
    ["tags"] = new[] { new Tag("work"), new Tag("important") }
};

// createEvent 함수 호출
FunctionResult functionResult = await kernel.InvokeAsync(plugin["createEvent"], arguments);
```

이 옵션은 아래 개요 표에 표시된 것처럼 기존 옵션 #1. `payload`와 `content-type` 인수와 옵션 #2. 리프 속성을 사용한 동적 페이로드 구성 사이에 자연스럽게 위치합니다.

### 옵션 개요
| 옵션 | 호출자 | SK | 제한사항 |
|--------|-------|----|--------|
| 1. `payload`와 `content-type` 인수 | 페이로드 구성 | 있는 그대로 사용 | 제한 없음 |
| 4. 루트 속성으로부터의 동적 페이로드 구성 | 루트 속성에 대한 인수 제공 | 페이로드 구성 | 1. `anyOf`, `allOf`, `oneOf` 미지원 |
| 2. 리프 속성으로부터의 동적 페이로드 구성 | 리프 속성에 대한 인수 제공 | 페이로드 구성 | 1. `anyOf`, `allOf`, `oneOf` 미지원, 2. 리프 속성이 고유해야 함, 3. 순환 참조 |
| 3. 리프 속성 + 네임스페이스로부터의 동적 페이로드 구성 | 네임스페이스 속성에 대한 인수 제공 | 페이로드 구성 | 1. `anyOf`, `allOf`, `oneOf` 미지원, 2. 순환 참조 |

### 결정 결과
이러한 옵션들을 논의한 후, 옵션 #4가 기존 옵션 #1에 비해 어떤 이점을 제공한다는 강력한 증거가 없어 구현을 진행하지 않기로 결정되었습니다.

## 샘플
위에서 설명한 기존 옵션의 사용법을 보여주는 샘플은 [Semantic Kernel 샘플 저장소](https://github.com/microsoft/semantic-kernel/blob/main/dotnet/samples/Concepts/Plugins/OpenApiPlugin_PayloadHandling.cs)에서 찾을 수 있습니다.
