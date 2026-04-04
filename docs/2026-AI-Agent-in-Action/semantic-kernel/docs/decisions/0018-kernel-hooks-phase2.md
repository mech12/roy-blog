## 맥락 및 문제 설명

현재 Kernel의 invoking 및 invoked 핸들러는 프롬프트를 핸들러에 노출하지 않습니다.

이 제안은 프롬프트를 핸들러에 노출하는 방법입니다.

- 실행 전 / Invoking

  - Get: LLM 호출 전 현재 `SemanticFunction.TemplateEngine`에 의해 생성된 프롬프트
  - Set: LLM에 전송하기 전 프롬프트 내용 수정

- 실행 후 / Invoked

  - Get: 생성된 프롬프트

## 결정 요인

- 프롬프트 템플릿은 Kernel.RunAsync 실행 내에서 함수 실행당 한 번만 생성되어야 합니다.
- 핸들러는 LLM 실행 전에 프롬프트를 확인하고 수정할 수 있어야 합니다.
- 핸들러는 LLM 실행 후에 프롬프트를 확인할 수 있어야 합니다.
- Kernel.RunAsync(function) 또는 ISKFunction.InvokeAsync(kernel) 호출 시 이벤트가 트리거되어야 합니다.

## 범위 밖

- Pre-Hooks를 사용한 계획 단계 건너뛰기.
- Pre/Post Hooks에서 사용된 서비스(Template Engine, IAIServices 등) 가져오기.
- Pre/Post Hooks에서 요청 설정 가져오기.

## Pre/Post Hooks에 대한 Kernel의 현재 상태

Kernel의 현재 상태:

```csharp
class Kernel : IKernel

RunAsync()
{
    var context = this.CreateNewContext(variables);
    var functionDetails = skFunction.Describe();
    var functionInvokingArgs = this.OnFunctionInvoking(functionDetails, context);

    functionResult = await skFunction.InvokeAsync(context, cancellationToken: cancellationToken);
    var functionInvokedArgs = this.OnFunctionInvoked(functionDetails, functionResult);
}
```

## 개발자 경험

다음은 프롬프트를 가져오거나 수정하기 위해 Pre/Post Hooks를 사용할 때 최종 사용자가 기대하는 코딩 경험입니다.

```csharp
const string FunctionPrompt = "Write a random paragraph about: {{$input}}.";

var excuseFunction = kernel.CreateSemanticFunction(...);

void MyPreHandler(object? sender, FunctionInvokingEventArgs e)
{
    Console.WriteLine($"{e.FunctionView.PluginName}.{e.FunctionView.Name} : Pre Execution Handler - Triggered");

    // 시맨틱 함수가 아닌 경우 false를 반환합니다
    if (e.TryGetRenderedPrompt(out var prompt))
    {
        Console.WriteLine("Rendered Prompt:");
        Console.WriteLine(prompt);

        // 필요한 경우 프롬프트를 업데이트합니다
        e.TryUpdateRenderedPrompt("Write a random paragraph about: Overriding a prompt");
    }
}

void MyPostHandler(object? sender, FunctionInvokedEventArgs e)
{
    Console.WriteLine($"{e.FunctionView.PluginName}.{e.FunctionView.Name} : Post Execution Handler - Triggered");
    // 시맨틱 함수가 아닌 경우 false를 반환합니다
    if (e.TryGetRenderedPrompt(out var prompt))
    {
        Console.WriteLine("Used Prompt:");
        Console.WriteLine(prompt);
    }
}

kernel.FunctionInvoking += MyPreHandler;
kernel.FunctionInvoked += MyPostHandler;

const string Input = "I missed the F1 final race";
var result = await kernel.RunAsync(Input, excuseFunction);
Console.WriteLine($"Function Result: {result.GetValue<string>()}");
```

예상 출력:

```
MyPlugin.MyFunction : Pre Execution Handler - Triggered
Rendered Prompt:
Write a random paragraph about: I missed the F1 final race.

MyPlugin.MyFunction : Post Execution Handler - Triggered
Used Prompt:
Write a random paragraph about: Overriding a prompt

FunctionResult: <LLM Completion>
```

## 검토한 옵션

### 모든 옵션에 공통된 개선 사항

`Dictionary<string, object>` 속성인 `Metadata`를 `FunctionInvokedEventArgs`에서 `SKEventArgs` 추상 클래스로 이동합니다.

장점:

- 이렇게 하면 모든 SKEventArgs가 확장 가능해져, `specialization`이 불가능할 때 EventArgs에 추가 정보를 전달할 수 있습니다.

### 옵션 1: Kernel이 SemanticFunctions를 인식

```csharp
class Kernel : IKernel

RunAsync()
{

    if (skFunction is SemanticFunction semanticFunction)
    {
        var prompt = await semanticFunction.TemplateEngine.RenderAsync(semanticFunction.Template, context);
        var functionInvokingArgs = this.OnFunctionInvoking(functionDetails, context, prompt);
        // InvokeWithPromptAsync 내부
        functionResult = await semanticFunction.InternalInvokeWithPromptAsync(prompt, context, cancellationToken: cancellationToken);
    }
    else
    {
        functionResult = await skFunction.InvokeAsync(context, cancellationToken: cancellationToken);
    }
}
class SemanticFunction : ISKFunction

public InvokeAsync(context, cancellationToken)
{
    var prompt = _templateEngine.RenderAsync();
    return InternalInvokeWithPromptAsync(prompt, context, cancellationToken);
}

internal InternalInvokeWithPromptAsync(string prompt)
{
    ... LLM을 호출하는 현재 로직
}
```

### 장단점

장점:

- 구현이 더 간단하고 빠릅니다
- 변경 사항이 적으며 대부분 `Kernel`과 `SemanticFunction` 클래스에 한정됩니다

단점:

- `Kernel`이 `SemanticFunction` 구현 세부 사항을 인식합니다
- 사용자 정의 `ISKFunctions` 구현의 프롬프트를 표시하도록 확장할 수 없습니다

### 옵션 2: ISKFunction에 이벤트 처리 위임 (인터페이스 접근 방식)

```csharp
class Kernel : IKernel
{
    RunAsync() {
        var functionInvokingArgs = await this.TriggerEvent<FunctionInvokingEventArgs>(this.FunctionInvoking, skFunction, context);

        var functionResult = await skFunction.InvokeAsync(context, cancellationToken: cancellationToken);

        var functionInvokedArgs = await this.TriggerEvent<FunctionInvokedEventArgs>(
            this.FunctionInvoked,
            skFunction,
            context);
    }

    private TEventArgs? TriggerEvent<TEventArgs>(EventHandler<TEventArgs>? eventHandler, ISKFunction function, SKContext context) where TEventArgs : SKEventArgs
    {
        if (eventHandler is null)
        {
            return null;
        }

        if (function is ISKFunctionEventSupport<TEventArgs> supportedFunction)
        {
            var eventArgs = await supportedFunction.PrepareEventArgsAsync(context);
            eventHandler.Invoke(this, eventArgs);
            return eventArgs;
        }

        // 추가 인터페이스로 데이터를 추가하는 것을 고려합니다.

        // 함수가 특정 이벤트를 지원하지 않으면:
        return null; // 무시하거나 예외를 던집니다.
        throw new NotSupportedException($"The provided function \"{function.Name}\" does not supports and implements ISKFunctionHandles<{typeof(TEventArgs).Name}>");
    }
}

public interface ISKFunctionEventSupport<TEventArgs> where TEventArgs : SKEventArgs
{
    Task<TEventArgs> PrepareEventArgsAsync(SKContext context, TEventArgs? eventArgs = null);
}

class SemanticFunction : ISKFunction,
    ISKFunctionEventSupport<FunctionInvokingEventArgs>,
    ISKFunctionEventSupport<FunctionInvokedEventArgs>
{

    public FunctionInvokingEventArgs PrepareEventArgsAsync(SKContext context, FunctionInvokingEventArgs? eventArgs = null)
    {
        var renderedPrompt = await this.RenderPromptTemplateAsync(context);
        context.Variables.Set(SemanticFunction.RenderedPromptKey, renderedPrompt);

        return new SemanticFunctionInvokingEventArgs(this.Describe(), context);
        // 또는                                                          Metadata Dictionary<string, object>
        return new FunctionInvokingEventArgs(this.Describe(), context, new Dictionary<string, object>() { { RenderedPrompt, renderedPrompt } });
    }

    public FunctionInvokedEventArgs PrepareEventArgsAsync(SKContext context, FunctionInvokedEventArgs? eventArgs = null)
    {
        return Task.FromResult<FunctionInvokedEventArgs>(new SemanticFunctionInvokedEventArgs(this.Describe(), context));
    }
}

public sealed class SemanticFunctionInvokedEventArgs : FunctionInvokedEventArgs
{
    public SemanticFunctionInvokedEventArgs(FunctionDescription functionDescription, SKContext context)
        : base(functionDescription, context)
    {
        _context = context;
        Metadata[RenderedPromptKey] = this._context.Variables[RenderedPromptKey];
    }

    public string? RenderedPrompt => this.Metadata[RenderedPromptKey];

}

public sealed class SemanticFunctionInvokingEventArgs : FunctionInvokingEventArgs
{
    public SemanticFunctionInvokingEventArgs(FunctionDescription functionDescription, SKContext context)
        : base(functionDescription, context)
    {
        _context = context;
    }
    public string? RenderedPrompt => this._context.Variables[RenderedPromptKey];
}
```

### 장단점

장점:

- `Kernel`이 `SemanticFunction` 구현 세부 사항이나 다른 `ISKFunction` 구현을 인식하지 않습니다
- 시맨틱 함수의 프롬프트를 포함하여 사용자 정의 `ISKFunctions` 구현별 전용 EventArgs를 표시하도록 확장할 수 있습니다
- `ISKFunctionEventSupport<NewEvent>` 인터페이스를 통해 Kernel의 향후 이벤트를 지원하도록 확장할 수 있습니다
- 함수가 자체 EventArgs 특수화를 가질 수 있습니다
- 인터페이스는 선택 사항이므로 사용자 정의 `ISKFunctions`는 구현 여부를 선택할 수 있습니다

단점:

- 이제 사용자 정의 함수가 이벤트를 지원하려면 `ISKFunctionEventSupport` 인터페이스를 구현해야 할 책임이 있습니다
- 다른 `ISKFunction`에서 이벤트를 처리하려면 컨텍스트와 프롬프트 + 기타 데이터를 다른 이벤트 처리 메서드에서 관리하기 위한 더 복잡한 접근 방식이 필요합니다

### 옵션 3: ISKFunction에 이벤트 처리 위임 (InvokeAsync 델리게이트 접근 방식)

`ISKFunction.InvokeAsync` 인터페이스에 Kernel 이벤트 핸들러 델리게이트 래퍼를 추가합니다.
이 접근 방식은 `Kernel`과 `ISKFunction` 구현 간에 이벤트 처리 책임을 공유하며, 흐름 제어는 Kernel이 처리하고 `ISKFunction`은 델리게이트 래퍼를 호출하고 핸들러에 전달될 `SKEventArgs`에 데이터를 추가하는 책임을 집니다.

```csharp
class Kernel : IKernel
{
    RunAsync() {
        var functionInvokingDelegateWrapper = new(this.FunctionInvoking);
        var functionInvokedDelegateWrapper = new(this.FunctionInvoked);

        var functionResult = await skFunction.InvokeAsync(context, functionInvokingDelegateWrapper, functionInvokingDelegateWrapper, functionInvokedDelegateWrapper);

        // Kernel은 델리게이트 결과를 분석하고 흐름 관련 결정을 내립니다
        if (functionInvokingDelegateWrapper.EventArgs.CancelRequested ... ) { ... }
        if (functionInvokingDelegateWrapper.EventArgs.SkipRequested ... ) { ... }
        if (functionInvokedDelegateWrapper.EventArgs.Repeat ... ) { ... }
    }
}

class SemanticFunction : ISKFunction {
    InvokeAsync(
        SKContext context,
        FunctionInvokingDelegateWrapper functionInvokingDelegateWrapper,
        FunctionInvokedDelegateWrapper functionInvokedDelegateWrapper)
    {
        // SemanticFunction은 델리게이트 래퍼를 호출하고 `Kernel`과 책임을 공유해야 합니다.
        if (functionInvokingDelegateWrapper.Handler is not null)
        {
            var renderedPrompt = await this.RenderPromptTemplateAsync(context);
            functionInvokingDelegateWrapper.EventArgs.RenderedPrompt = renderedPrompt;

            functionInvokingDelegateWrapper.Handler.Invoke(this, functionInvokingDelegateWrapper.EventArgs);

            if (functionInvokingDelegateWrapper.EventArgs?.CancelToken.IsCancellationRequested ?? false)
            {
                // 처리되지 않은 결과를 강제해야 합니다
                return new SKFunctionResult(context);

                // 또는 InvokeAsync가 null FunctionResult?를 반환할 수 있도록 합니다
                return null;
            }
        }
    }
}

// EventHandler 래퍼
class FunctionDelegateWrapper<TEventArgs> where TEventArgs : SKEventArgs
{
    FunctionInvokingDelegateWrapper(EventHandler<TEventArgs> eventHandler) {}

    // Set은 특수화된 eventargs를 설정할 수 있게 합니다.
    public TEventArgs EventArgs { get; set; }
    public EventHandler<TEventArgs> Handler => _eventHandler;
}
```

### 장단점

장점:

- `ISKFunction`이 EventArgs에서 데이터(렌더링된 프롬프트)와 상태를 처리하고 노출하는 코드/복잡성이 적습니다
- `Kernel`이 `SemanticFunction` 구현 세부 사항이나 다른 `ISKFunction` 구현을 인식하지 않습니다
- `Kernel`의 코드/복잡성이 적습니다
- 시맨틱 함수의 프롬프트를 포함하여 사용자 정의 `ISKFunctions` 구현별 전용 EventArgs를 표시하도록 확장할 수 있습니다

단점:

- 필요한 경우 새 이벤트를 추가할 수 없습니다 (ISKFunction 인터페이스 변경 필요)
- 함수가 의존성(Kernel) 이벤트와 관련된 동작을 구현해야 합니다
- Kernel이 이벤트 핸들러의 결과와 상호 작용해야 하므로, 커널 수준에서 참조로 결과에 접근하기 위한 래퍼 전략이 필요합니다 (흐름 제어)
- Kernel 이벤트 핸들러의 전체 책임을 함수로 다운스트림 전달하는 것은 적절하지 않습니다 (단일 책임 원칙)

### 옵션 4: ISKFunction에 이벤트 처리 위임 (SKContext 델리게이트 접근 방식)

`ISKFunction.InvokeAsync` 인터페이스에 Kernel 이벤트 핸들러 델리게이트 래퍼를 추가합니다.
이 접근 방식은 `Kernel`과 `ISKFunction` 구현 간에 이벤트 처리 책임을 공유하며, 흐름 제어는 Kernel이 처리하고 `ISKFunction`은 델리게이트 래퍼를 호출하고 핸들러에 전달될 `SKEventArgs`에 데이터를 추가하는 책임을 집니다.

```csharp
class Kernel : IKernel
{
    CreateNewContext() {
        var context = new SKContext(...);
        context.AddEventHandlers(this.FunctionInvoking, this.FunctionInvoked);
        return context;
    }
    RunAsync() {
        functionResult = await skFunction.InvokeAsync(context, ...);
        if (this.IsCancelRequested(functionResult.Context)))
            break;
        if (this.IsSkipRequested(functionResult.Context))
            continue;
        if (this.IsRepeatRequested(...))
            goto repeat;

        ...
    }
}

class SKContext {

    internal EventHandlerWrapper<FunctionInvokingEventArgs>? FunctionInvokingHandler { get; private set; }
    internal EventHandlerWrapper<FunctionInvokedEventArgs>? FunctionInvokedHandler { get; private set; }

    internal SKContext(
        ...
        ICollection<EventHandlerWrapper?>? eventHandlerWrappers = null
    {
        ...
        this.InitializeEventWrappers(eventHandlerWrappers);
    }

    void InitializeEventWrappers(ICollection<EventHandlerWrapper?>? eventHandlerWrappers)
    {
        if (eventHandlerWrappers is not null)
        {
            foreach (var handler in eventHandlerWrappers)
            {
                if (handler is EventHandlerWrapper<FunctionInvokingEventArgs> invokingWrapper)
                {
                    this.FunctionInvokingHandler = invokingWrapper;
                    continue;
                }

                if (handler is EventHandlerWrapper<FunctionInvokedEventArgs> invokedWrapper)
                {
                    this.FunctionInvokedHandler = invokedWrapper;
                }
            }
        }
    }
}

class SemanticFunction : ISKFunction {
    InvokeAsync(
        SKContext context
    {
        string renderedPrompt = await this._promptTemplate.RenderAsync(context, cancellationToken).ConfigureAwait(false);

        this.CallFunctionInvoking(context, renderedPrompt);
        if (this.IsInvokingCancelOrSkipRequested(context, out var stopReason))
        {
            return new StopFunctionResult(this.Name, this.PluginName, context, stopReason!.Value);
        }

        string completion = await GetCompletionsResultContentAsync(...);

        var result = new FunctionResult(this.Name, this.PluginName, context, completion);
        result.Metadata.Add(SemanticFunction.RenderedPromptMetadataKey, renderedPrompt);

        this.CallFunctionInvoked(result, context, renderedPrompt);
        if (this.IsInvokedCancelRequested(context, out stopReason))
        {
            return new StopFunctionResult(this.Name, this.PluginName, context, result.Value, stopReason!.Value);
        }

        return result;
    }
}
```

### 장단점

장점:

- `ISKFunction`이 EventArgs에서 데이터(렌더링된 프롬프트)와 상태를 처리하고 노출하는 코드/복잡성이 적습니다.
- `Kernel`이 `SemanticFunction` 구현 세부 사항이나 다른 `ISKFunction` 구현을 인식하지 않습니다
- `Kernel`의 코드/복잡성이 적습니다
- 시맨틱 함수의 프롬프트를 포함하여 사용자 정의 `ISKFunctions` 구현별 전용 EventArgs를 표시하도록 확장할 수 있습니다
- `ISKFunction` 인터페이스가 새 이벤트를 추가하기 위해 변경될 필요가 없으므로 더 확장 가능합니다.
- `SKContext`를 확장하여 호환성 파괴 변경 없이 새 이벤트를 추가할 수 있습니다.

단점:

- 함수가 이제 컨텍스트 내 이벤트를 처리하는 로직을 구현해야 합니다
- Kernel이 이벤트 핸들러의 결과와 상호 작용해야 하므로, 커널 수준에서 참조로 결과에 접근하기 위한 래퍼 전략이 필요합니다 (흐름 제어)
- Kernel 이벤트 핸들러의 전체 책임을 함수로 다운스트림 전달하는 것은 적절하지 않습니다 (단일 책임 원칙)

## 결정 결과

### 옵션 4: ISKFunction에 이벤트 처리 위임 (SKContext 델리게이트 접근 방식)

이 방식은 함수가 일부 커널 로직을 구현하게 하지만, 동일한 실행 컨텍스트에 대해 로직을 다른 메서드로 분리하지 않는다는 큰 장점이 있습니다.

가장 큰 장점:
**`ISKFunction`이 EventArgs에서 데이터와 상태를 처리하고 노출하는 코드/복잡성이 적습니다.**
**`ISKFunction` 인터페이스가 새 이벤트를 추가하기 위해 변경될 필요가 없습니다.**

이 구현은 컨텍스트와 프롬프트를 다른 메서드에서 관리할 필요 없이 InvokeAsync에서 renderedPrompt를 가져올 수 있게 합니다.

위 내용은 호출 과정에서 사용 가능한 다른 데이터에도 적용되며, 새로운 EventArgs 속성으로 추가할 수 있습니다.
