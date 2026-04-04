---
# 선택적 요소입니다. 필요 없는 항목은 자유롭게 제거하세요.
status: accepted
contact: markwallace
date: 2024-03-15
deciders: sergeymenshykh, markwallace, rbarreto, dmytrostruk
consulted: 
informed: stoub, matthewbolanos
---

# {해결된 문제와 솔루션의 짧은 제목}

## 배경 및 문제 설명

`KernelFunctionMetadata.PluginName` 속성은 `KernelPlugin.GetFunctionsMetadata` 호출의 부작용으로 채워집니다.
이 동작의 이유는 `KernelFunction` 인스턴스가 여러 `KernelPlugin` 인스턴스와 연결될 수 있도록 하기 위함입니다.
이 동작의 단점은 `KernelFunctionMetadata.PluginName` 속성이 `IFunctionFilter` 콜백에서 사용할 수 없다는 것입니다.

이 ADR의 목적은 개발자가 `KernelFunctionMetadata.PluginName`이 채워지는 시점을 결정할 수 있는 변경을 제안하는 것입니다.

이슈:

1. [KernelFunction 메타데이터에서 PluginName을 수정해야 하는지 조사](https://github.com/microsoft/semantic-kernel/issues/4706)
1. [IFunctionFilter의 FunctionInvokingContext 내 Plugin name이 null임](https://github.com/microsoft/semantic-kernel/issues/5452)

## 결정 동인

- 기존 애플리케이션을 깨뜨리지 않아야 합니다.
- `KernelFunctionMetadata.PluginName` 속성을 `IFunctionFilter` 콜백에서 사용할 수 있는 기능을 제공해야 합니다.

## 검토된 옵션

- 각 `KernelFunction`이 `KernelPlugin`에 추가될 때 복제하고 복제된 `KernelFunctionMetadata`에 플러그인 이름을 설정합니다.
- `KernelPluginFactory.CreateFromFunctions`에 연관된 `KernelFunctionMetadata` 인스턴스에 플러그인 이름을 설정할 수 있는 새 매개변수를 추가합니다. 한번 설정되면 `KernelFunctionMetadata.PluginName`은 변경할 수 없습니다. 변경을 시도하면 `InvalidOperationException`이 발생합니다.
- 현재 상태를 유지하고 이 사용 사례를 지원하지 않습니다. Semantic Kernel의 동작이 일관성 없어 보일 수 있기 때문입니다.

## 결정 결과

선택된 옵션: 각 `KernelFunction` 복제, 결과가 일관된 동작이며 동일한 함수를 여러 `KernelPlugin`에 추가할 수 있기 때문입니다.

## 옵션별 장단점

### 각 `KernelFunction` 복제

PR: https://github.com/microsoft/semantic-kernel/pull/5422

- 나쁨, 동일한 함수를 여러 `KernelPlugin`에 추가할 수 있음.
- 나쁨, 동작이 일관적이기 때문.
- 좋음, API 시그니처에 브레이킹 변경이 없음.
- 나쁨, 추가 `KernelFunction` 인스턴스가 생성됨.

### `KernelPluginFactory.CreateFromFunctions`에 새 매개변수 추가

PR: https://github.com/microsoft/semantic-kernel/pull/5171

- 좋음, 추가 `KernelFunction` 인스턴스가 생성되지 않음.
- 나쁨, 동일한 함수를 여러 `KernelPlugin`에 추가할 수 없음.
- 나쁨, 혼란스러울 수 있음. 즉, `KernelPlugin`이 어떻게 생성되느냐에 따라 다르게 동작함.
- 나쁨, API 시그니처에 사소한 브레이킹 변경이 있음.
