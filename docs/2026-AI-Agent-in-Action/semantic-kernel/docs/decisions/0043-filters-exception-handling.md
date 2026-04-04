---
# 선택적 요소입니다. 필요 없는 항목은 자유롭게 제거하세요.
status: accepted
contact: dmytrostruk
date: 2024-04-24
deciders: sergeymenshykh, markwallace, rbarreto, dmytrostruk, stoub
---

# 필터에서의 예외 처리

## 배경 및 문제 설명

Semantic Kernel의 .NET 버전에서, 커널 함수가 예외를 던지면 어떤 코드가 이를 잡을 때까지 실행 스택을 통해 전파됩니다. `kernel.InvokeAsync(function)`에 대한 예외를 처리하려면 이 코드를 `try/catch` 블록으로 감싸야 하며, 이는 예외를 처리하는 직관적인 접근 방식입니다.

불행히도, `try/catch` 블록은 프롬프트를 기반으로 함수가 호출되는 자동 함수 호출 시나리오에서는 유용하지 않습니다. 이 경우, 함수가 예외를 던지면 `Error: Exception while invoking function.` 메시지가 `tool` 작성자 역할로 채팅 히스토리에 추가되며, 이는 무언가 잘못되었다는 일부 컨텍스트를 LLM에 제공해야 합니다.

예외를 던지고 AI에 오류 메시지를 보내는 대신 함수 결과를 재정의할 수 있는 능력에 대한 요구 사항이 있으며, 이를 통해 LLM 동작을 제어할 수 있어야 합니다.

## 검토된 옵션

### [옵션 1] 기존 `IFunctionFilter` 인터페이스에 새 메서드 추가

추상화:

```csharp
public interface IFunctionFilter
{
    void OnFunctionInvoking(FunctionInvokingContext context);

    void OnFunctionInvoked(FunctionInvokedContext context);

    // 새 메서드
    void OnFunctionException(FunctionExceptionContext context);
}
```

단점:

- 기존 인터페이스에 새 메서드를 추가하면 브레이킹 변경이 되며, 현재 필터 사용자가 새 메서드를 구현하도록 강제합니다.
- 이 메서드는 예외 처리가 필요하지 않을 때에도 함수 필터를 사용할 때 항상 구현해야 합니다. 반면에 이 메서드는 아무것도 반환하지 않으므로 항상 비어 있을 수 있으며, .NET 멀티타겟팅을 사용하면 C# 8 이상에서 기본 구현을 정의할 수 있어야 합니다.

### [옵션 2] 새로운 `IExceptionFilter` 인터페이스 도입

새 인터페이스는 예외 객체를 수신하고, 예외를 취소하거나 새로운 유형의 예외를 다시 던질 수 있게 합니다. 이 옵션은 나중에 글로벌 예외 처리를 위한 상위 수준 필터로도 추가될 수 있습니다.

추상화:

```csharp
public interface IExceptionFilter
{
    // ExceptionContext 클래스는 실제 예외, 커널 함수 등에 대한 정보를 포함합니다.
    void OnException(ExceptionContext context);
}
```

사용법:

```csharp
public class MyFilter : IFunctionFilter, IExceptionFilter
{
    public void OnFunctionInvoking(FunctionInvokingContext context) { }

    public void OnFunctionInvoked(FunctionInvokedContext context) { }

    public void OnException(ExceptionContext context) {}
}
```

장점:

- 브레이킹 변경이 아니며, 모든 예외 처리 로직은 기존 필터 메커니즘 위에 추가되어야 합니다.
- ASP.NET의 `IExceptionFilter` API와 유사합니다.

단점:

- 예외 처리를 위해 별도의 인터페이스를 구현해야 한다는 것이 직관적이지 않고 기억하기 어려울 수 있습니다.

### [옵션 3] 기존 `IFunctionFilter` 인터페이스에서 Context 모델 확장

`IFunctionFilter.OnFunctionInvoked` 메서드에서 `Exception` 속성을 추가하여 `FunctionInvokedContext` 모델을 확장할 수 있습니다. 이 경우 `OnFunctionInvoked`가 트리거되면 함수 실행 중 예외가 있었는지 관찰할 수 있습니다.

예외가 있었다면 사용자는 아무것도 하지 않을 수 있으며 예외는 평소대로 던져집니다. 즉, 처리하려면 함수 호출을 `try/catch` 블록으로 감싸야 합니다. 그러나 해당 예외를 취소하고 함수 결과를 재정의하는 것도 가능하며, 이는 함수 실행과 LLM에 전달되는 내용에 대한 더 많은 제어를 제공합니다.

추상화:

```csharp
public sealed class FunctionInvokedContext : FunctionFilterContext
{
    // 기타 속성...

    public Exception? Exception { get; private set; }
}
```

사용법:

```csharp
public class MyFilter : IFunctionFilter
{
    public void OnFunctionInvoking(FunctionInvokingContext context) { }

    public void OnFunctionInvoked(FunctionInvokedContext context)
    {
        // 이는 함수 실행 중 예외가 발생했음을 의미합니다.
        // 무시하면 예외는 평소대로 던져집니다.
        if (context.Exception is not null)
        {
            // 처리 가능한 옵션:

            // 1. 함수 실행 중 발생한 예외를 던지지 않음
            context.Exception = null;

            // 2. LLM에 의미 있는 값으로 결과를 재정의
            context.Result = new FunctionResult(context.Function, "Friendly message instead of exception");

            // 3. 필요한 경우 다른 유형의 예외를 다시 던짐 - 옵션 1.
            context.Exception = new Exception("New exception");

            // 3. 필요한 경우 다른 유형의 예외를 다시 던짐 - 옵션 2.
            throw new Exception("New exception");
        }
    }
}
```

장점:

- 기존 구현에 최소한의 변경이 필요하며 기존 필터 사용자를 깨뜨리지 않습니다.
- ASP.NET의 `IActionFilter` API와 유사합니다.
- 확장 가능하며, 필요할 때 다른 유형의 필터(프롬프트 또는 함수 호출 필터)에 대한 유사한 Context 모델을 확장할 수 있습니다.

단점:

- `context.Exception = null` 또는 `context.Exception = new AnotherException()` 방식의 예외 처리는 네이티브 `try/catch` 접근 대신 .NET 친화적이지 않습니다.

### [옵션 4] `next` 델리게이트를 추가하여 `IFunctionFilter` 시그니처 변경.

이 접근 방식은 현재 필터가 작동하는 방식을 변경합니다. 필터에 `Invoking`과 `Invoked` 두 개의 메서드를 갖는 대신, 함수 실행 중 호출되는 하나의 메서드만 있으며 `next` 델리게이트가 파이프라인에 등록된 다음 필터 또는 남은 필터가 없는 경우 함수 자체를 호출합니다.

추상화:

```csharp
public interface IFunctionFilter
{
    Task OnFunctionInvocationAsync(FunctionInvocationContext context, Func<FunctionInvocationContext, Task> next);
}
```

사용법:

```csharp
public class MyFilter : IFunctionFilter
{
    public async Task OnFunctionInvocationAsync(FunctionInvocationContext context, Func<FunctionInvocationContext, Task> next)
    {
        // 함수 호출 전 일부 액션 수행
        await next(context);
        // 함수 호출 후 일부 액션 수행
    }
}
```

네이티브 `try/catch` 접근 방식을 사용한 예외 처리:

```csharp
public async Task OnFunctionInvocationAsync(FunctionInvocationContext context, Func<FunctionInvocationContext, Task> next)
{
    try
    {
        await next(context);
    }
    catch (Exception exception)
    {
        this._logger.LogError(exception, "Something went wrong during function invocation");

        // 예시: 함수 결과 값 재정의
        context.Result = new FunctionResult(context.Function, "Friendly message instead of exception");

        // 예시: 필요한 경우 다른 유형의 예외를 다시 던짐
        throw new InvalidOperationException("New exception");
    }
}
```

장점:

- 예외를 처리하고 다시 던지는 네이티브 방식.
- ASP.NET의 `IAsyncActionFilter`와 `IEndpointFilter` API와 유사합니다.
- 두 개(`Invoking/Invoked`) 대신 구현할 필터 메서드가 하나 - 이를 통해 호출 컨텍스트 정보를 클래스 수준에 저장하는 대신 하나의 메서드에 유지할 수 있습니다. 예를 들어, 함수 실행 시간을 측정하기 위해 `await next(context)` 호출 전에 `Stopwatch`를 생성하고 시작하여 호출 후에 사용할 수 있으며, `Invoking/Invoked` 메서드 접근 방식에서는 데이터를 필터 액션 간에 다른 방식으로, 예를 들어 클래스 수준에 설정하여 전달해야 하며 이는 유지 관리가 더 어렵습니다.
- 취소 로직이 필요 없음(예: `context.Cancel = true`). 작업을 취소하려면 단순히 `await next(context)`를 호출하지 않으면 됩니다.

단점:

- 모든 필터에서 `await next(context)`를 수동으로 호출하는 것을 기억해야 합니다. 호출하지 않으면 파이프라인의 다음 필터 및/또는 함수 자체가 호출되지 않습니다.

## 결정 결과

옵션 4를 진행하고 이 접근 방식을 함수, 프롬프트 및 함수 호출 필터에 적용합니다.
