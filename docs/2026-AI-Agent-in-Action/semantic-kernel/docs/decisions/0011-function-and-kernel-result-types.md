---
# 이 항목들은 선택 사항입니다. 필요 없는 항목은 자유롭게 제거하세요.
status: accepted
contact: dmytrostruk
date: 2023-09-21
deciders: shawncal, dmytrostruk
consulted: 
informed: 
---
# SKContext를 Function/Kernel 결과 타입으로 사용하는 대신 FunctionResult 및 KernelResult 모델로 대체

## 배경 및 문제 상황

`function.InvokeAsync`와 `kernel.RunAsync` 메서드는 결과 타입으로 `SKContext`를 반환합니다. 이에는 여러 문제가 있습니다:

1. `SKContext`에는 `string`인 `Result` 속성이 포함되어 있습니다. 이에 기반하여 복합 타입을 반환하거나 Kernel에서 스트리밍 기능을 구현하는 것이 불가능합니다.
2. `SKContext`에는 LLM 전용 로직에 결합된 `ModelResults` 속성이 포함되어 있어, 특정 경우의 시맨틱 함수에만 적용 가능합니다.
3. `SKContext`는 파이프라인에서 함수 간 정보를 전달하는 메커니즘으로서 내부 구현이어야 합니다. Kernel 호출자는 입력/요청을 제공하고 결과를 받아야 하지, `SKContext`를 받아서는 안 됩니다.
4. `SKContext`에는 파이프라인의 특정 함수에 대한 정보에 접근할 방법 없이 마지막으로 실행된 함수와 관련된 정보만 포함됩니다.

## 결정 동인

1. Kernel은 복합 타입을 반환할 수 있어야 하며 스트리밍 기능을 지원해야 합니다.
2. Kernel은 AI 로직에 결합되지 않는 방식으로 함수 실행과 관련된 데이터(예: 사용된 토큰 수)를 반환할 수 있어야 합니다.
3. `SKContext`는 함수 간 정보를 전달하는 내부 메커니즘으로 작동해야 합니다.
4. 함수 결과와 커널 결과를 구분할 수 있는 방법이 있어야 합니다. 이 엔티티들은 본질적으로 다르며 향후 다른 속성 세트를 포함할 수 있기 때문입니다.
5. 파이프라인 중간에서 특정 함수 결과에 접근할 수 있는 가능성은 사용자에게 함수가 어떻게 수행되었는지에 대한 더 많은 통찰을 제공합니다.

## 검토된 옵션

1. `dynamic`을 반환 타입으로 사용 - 이 옵션은 어느 정도 유연성을 제공하지만, .NET 세계에서 선호되는 강한 타이핑을 제거합니다. 또한 함수 결과와 Kernel 결과를 구분할 방법이 없습니다.
2. 새로운 타입 정의 - `FunctionResult`와 `KernelResult` - 선택된 접근 방식.

## 결정 결과

새로운 `FunctionResult`와 `KernelResult` 반환 타입은 함수에서 복합 타입 반환, 스트리밍 지원, 각 함수 결과에 개별적으로 접근하는 시나리오를 다뤄야 합니다.

### 복합 타입과 스트리밍

복합 타입과 스트리밍을 위해 `FunctionResult`에 단일 함수 결과를 저장하는 `object Value` 속성이 정의되고, `KernelResult`에는 실행 파이프라인의 마지막 함수 결과를 저장합니다. 더 나은 사용성을 위해 제네릭 메서드 `GetValue<T>`를 사용하여 `object Value`를 특정 타입으로 캐스트할 수 있습니다.

예제:

```csharp
// 문자열
var text = (await kernel.RunAsync(function)).GetValue<string>();

// 복합 타입
var myComplexType = (await kernel.RunAsync(function)).GetValue<MyComplexType>();

// 스트리밍
var results = (await kernel.RunAsync(function)).GetValue<IAsyncEnumerable<int>>();

await foreach (var result in results)
{
    Console.WriteLine(result);
}
```

`FunctionResult`/`KernelResult`가 `TypeA`를 저장하고 있는데 호출자가 `TypeB`로 캐스트하려고 하면 타입에 대한 세부 정보와 함께 `InvalidCastException`이 발생합니다. 이는 호출자에게 캐스팅에 어떤 타입을 사용해야 하는지에 대한 정보를 제공합니다.

### 메타데이터

함수 실행과 관련된 추가 정보를 반환하기 위해 `FunctionResult`에 `Dictionary<string, object> Metadata` 속성이 추가됩니다. 이를 통해 함수가 어떻게 수행되었는지에 대한 통찰을 제공하는 모든 종류의 정보를 호출자에게 전달할 수 있습니다(예: 사용된 토큰 수, AI 모델 응답 등).

예제:

```csharp
var functionResult = await function.InvokeAsync(context);
Console.WriteLine(functionResult.Metadata["MyInfo"]);
```

### 다중 함수 결과

`KernelResult`에는 함수 결과 컬렉션 `IReadOnlyCollection<FunctionResult> FunctionResults`가 포함됩니다. 이를 통해 `KernelResult`에서 특정 함수 결과를 가져올 수 있습니다. `FunctionResult`의 `FunctionName` 및 `PluginName` 속성은 컬렉션에서 특정 함수를 가져오는 데 도움이 됩니다.

예제:

```csharp
var kernelResult = await kernel.RunAsync(function1, function2, function3);

var functionResult2 = kernelResult.FunctionResults.First(l => l.FunctionName == "Function2" && l.PluginName == "MyPlugin");

Assert.Equal("Result2", functionResult2.GetValue<string>());
```
