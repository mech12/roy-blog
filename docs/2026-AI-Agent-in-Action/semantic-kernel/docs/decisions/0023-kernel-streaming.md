---
# 이 항목들은 선택 사항입니다. 필요 없는 항목은 자유롭게 삭제하세요.
status: proposed
date: 2023-11-13
deciders: rogerbarreto,markwallace-microsoft,SergeyMenshykh,dmytrostruk
consulted:
informed:
---

# Kernel 및 함수 사용을 위한 스트리밍 기능 - Phase 1

## 맥락 및 문제 설명

코파일럿 구현에서 LLM(대규모 언어 모델)의 메시지를 스트리밍으로 출력하는 것은 매우 일반적이며, 현재 ISKFunctions.InvokeAsync 또는 Kernel.RunAsync 메서드를 사용하면 이것이 불가능합니다. 이로 인해 사용자는 현재 스트리밍을 지원하는 유일한 인터페이스인 `ITextCompletion` 및 `IChatCompletion` 서비스를 직접 사용하기 위해 Kernel과 함수를 우회해야 합니다.

현재 스트리밍은 모든 제공자가 지원하는 기능이 아니며, 설계의 일부로 서비스가 텍스트뿐만 아니라 이미지, 오디오, 비디오 등 다른 유형의 데이터 스트리밍도 지원할 수 있는 적절한 추상화를 갖추도록 보장하려고 합니다.

SK 개발자가 스트리밍 데이터를 가져오려고 할 때 이를 명확히 알 수 있어야 합니다.

## 결정 요인

1. SK 개발자는 Kernel.RunAsync 또는 ISKFunctions.InvokeAsync 메서드를 사용하여 Kernel과 함수에서 스트리밍 데이터를 가져올 수 있어야 합니다

2. SK 개발자는 데이터를 제네릭 방식으로 가져올 수 있어야 하므로, Kernel과 함수가 텍스트에 국한되지 않고 모든 유형의 데이터를 스트리밍할 수 있어야 합니다.

3. 스트리밍을 지원하지 않는 모델에서 스트리밍을 사용하는 SK 개발자도 전체 데이터를 나타내는 하나의 스트리밍 업데이트만으로 사용할 수 있어야 합니다.

## 범위 밖

- 이 단계에서는 계획(plan)을 사용한 스트리밍은 지원되지 않습니다. 시도하면 예외가 발생합니다.
- Kernel 스트리밍은 여러 함수(파이프라인)를 지원하지 않습니다.
- 이 단계에서는 입력 스트리밍이 지원되지 않습니다.
- 스트리밍 함수의 Post Hook 건너뛰기, 반복 및 취소는 지원되지 않습니다.

## 검토한 옵션

### 옵션 1 - 전용 스트리밍 인터페이스

SK 개발자가 커넥터에서 직접 string, byte 배열을 포함한 스트리밍 데이터를 제네릭 방식으로 가져올 수 있게 하는 전용 스트리밍 인터페이스를 사용하며, Kernel과 함수 구현이 텍스트에 국한되지 않고 모든 유형의 데이터를 스트리밍할 수 있게 합니다.

이 접근 방식은 커널과 함수에서 IAsyncEnumerable 형식으로 반환되는 스트리밍 데이터의 유형을 SK 개발자에게 명확히 하는 전용 인터페이스도 노출합니다.

`ITextCompletion`과 `IChatCompletion`은 `byte[]`와 `string` 스트리밍 데이터를 직접 가져오는 새 API와 특수화된 `StreamingContent` 반환을 갖게 됩니다.

SK 개발자는 `Kernel.RunStreamingAsync<T>()` 및 `ISKFunction.InvokeStreamingAsync<T>`에 제네릭 타입을 지정하여 스트리밍 데이터를 가져올 수 있습니다. 타입이 지정되지 않으면 Kernel과 함수는 데이터를 StreamingContent로 반환합니다.

타입이 지정되지 않았거나 문자열 표현으로 캐스팅할 수 없으면 예외가 발생합니다.

지정된 타입이 `StreamingContent`이거나 커넥터가 지원하는 다른 타입이면 오류가 발생하지 않습니다.

## 사용자 경험 목표

```csharp
//(제네릭 매개변수로 타입 제공)

// Kernel에서 Raw 스트리밍 데이터 가져오기
await foreach(string update in kernel.RunStreamingAsync<byte[]>(function, variables))

// Kernel에서 String으로 스트리밍 데이터 가져오기
await foreach(string update in kernel.RunStreamingAsync<string>(function, variables))

// Kernel에서 StreamingContent로 스트리밍 데이터 가져오기
await foreach(StreamingContent update in kernel.RunStreamingAsync<StreamingContent>(variables, function))
// 또는
await foreach(StreamingContent update in kernel.RunStreamingAsync(function, variables)) // 위의 제네릭이 기본값)
{
    Console.WriteLine(update);
}
```

모든 스트림 콘텐츠에 대한 추상 클래스로, 커넥터가 스트리밍 결과와 관련된 데이터 및 메타데이터를 포함하는 `StreamingContent`의 특수화된 타입을 제공하는 책임을 집니다.

```csharp

public abstract class StreamingContent
{
    public abstract int ChoiceIndex { get; }

    /// 청크 콘텐츠의 문자열 표현을 반환합니다
    public abstract override string ToString();

    /// 이전 청크 콘텐츠와 구성/추가할 수 있는 방식의 청크 콘텐츠의 추상 byte[] 표현.
    /// 기본 타입의 특성에 따라, 이 메서드가 <see cref="ToString"/>보다 더 효율적일 수 있습니다.
    public abstract byte[] ToByteArray();

    /// 내부 청크 콘텐츠 객체 참조. (Breaking glass).
    /// 각 커넥터는 콘텐츠 청크를 나타내는 자체 내부 객체를 가집니다.
    /// 이 속성의 사용은 "안전하지 않은" 것으로 간주됩니다. 꼭 필요한 경우에만 사용하세요.
    public object? InnerContent { get; }

    /// 콘텐츠와 관련된 메타데이터.
    public Dictionary<string, object>? Metadata { get; set; }

    /// 함수 호출과 관련된 현재 컨텍스트.
    internal SKContext? Context { get; set; }

    /// <param name="innerContent">내부 콘텐츠 객체 참조</param>
    protected StreamingContent(object? innerContent)
    {
        this.InnerContent = innerContent;
    }
}
```

StreamingChatContent의 특수화 예시

```csharp
//
public class StreamingChatContent : StreamingContent
{
    public override int ChoiceIndex { get; }
    public FunctionCall? FunctionCall { get; }
    public string? Content { get; }
    public AuthorRole? Role { get; }
    public string? Name { get; }

    public StreamingChatContent(AzureOpenAIChatMessage chatMessage, int resultIndex) : base(chatMessage)
    {
        this.ChoiceIndex = resultIndex;
        this.FunctionCall = chatMessage.InnerChatMessage?.FunctionCall;
        this.Content = chatMessage.Content;
        this.Role = new AuthorRole(chatMessage.Role.ToString());
        this.Name = chatMessage.InnerChatMessage?.Name;
    }

    public override byte[] ToByteArray() => Encoding.UTF8.GetBytes(this.ToString());
    public override string ToString() => this.Content ?? string.Empty;
}
```

`IChatCompletion`과 `ITextCompletion` 인터페이스는 제네릭 스트리밍 콘텐츠 데이터를 가져오는 새 API를 갖게 됩니다.

```csharp
interface ITextCompletion + IChatCompletion
{
    IAsyncEnumerable<T> GetStreamingContentAsync<T>(...);

    // T가 지원되지 않으면 예외 발생
}

interface IKernel
{
    // T 타입의 스트리밍 함수 콘텐츠 가져오기
    IAsyncEnumerable<T> RunStreamingAsync<T>(ContextVariables variables, ISKFunction function);
}

interface ISKFunction
{
    // T 타입의 스트리밍 함수 콘텐츠 가져오기
    IAsyncEnumerable<T> InvokeStreamingAsync<T>(SKContext context);
}
```

## 프롬프트/시맨틱 함수 동작

프롬프트 함수가 스트리밍 API를 사용하여 호출되면, 커넥터의 스트리밍 구현을 사용하려고 시도합니다.
커넥터는 특수화된 타입의 `StreamingContent`를 제공하는 책임이 있으며, 기본 백엔드 API가 스트리밍을 지원하지 않더라도 출력은 전체 데이터가 포함된 하나의 streamingcontent가 됩니다.

## 메서드/네이티브 함수 동작

메서드 함수는 반복자에서 반환된 객체를 `StreamingMethodContent`로 감싸는 방식으로 `StreamingContent`를 자동으로 지원합니다.

```csharp
public sealed class StreamingMethodContent : StreamingContent
{
    public override int ChoiceIndex => 0;

    /// 콘텐츠 청크를 나타내는 메서드 객체 값
    public object Value { get; }

    /// 기본 구현
    public override byte[] ToByteArray()
    {
        if (this.Value is byte[])
        {
            // 메서드 값이 byte[]이면 직접 반환합니다
            return (byte[])this.Value;
        }

        // 기본적으로 네이티브 값이 byte[]가 아니면 값의 UTF8 문자열 표현을 출력합니다
        return Encoding.UTF8.GetBytes(this.Value?.ToString());
    }

    /// <inheritdoc/>
    public override string ToString()
    {
        return this.Value.ToString();
    }

    /// <summary>
    /// <see cref="StreamingMethodContent"/> 클래스의 새 인스턴스를 초기화합니다.
    /// </summary>
    /// <param name="innerContent">청크를 나타내는 기본 객체</param>
    public StreamingMethodContent(object innerContent) : base(innerContent)
    {
        this.Value = innerContent;
    }
}
```

MethodFunction이 `IAsyncEnumerable`을 반환하면 각 열거 가능한 결과가 자동으로 `StreamingMethodContent`로 감싸져 스트리밍 동작과 전체 추상화의 일관성을 유지합니다.

MethodFunction이 `IAsyncEnumerable`이 아닌 경우, 완전한 결과가 `StreamingMethodContent`로 감싸져 단일 항목으로 반환됩니다.

## 장점

1. 사용자 경험 목표 섹션의 모든 옵션이 가능합니다.
2. Kernel과 함수 구현이 텍스트에 국한되지 않고 모든 유형의 데이터를 스트리밍할 수 있습니다
3. SK 개발자가 `GetStreamingContentAsync<T>` 메서드에서 기대하는 스트리밍 콘텐츠 타입을 제공할 수 있습니다.
4. SK 개발자가 동일한 결과 타입으로 Kernel, 함수 및 커넥터에서 스트리밍을 가져올 수 있습니다.

## 단점

1. SK 개발자가 `StreamingContent`의 특수화된 타입을 사용하려면 올바른 **StreamingContent 확장 메서드**를 사용하거나 `<T>`에 타입을 직접 제공하기 위해 어떤 커넥터가 사용되고 있는지 알아야 합니다.
2. 커넥터가 올바른 특수 타입의 `StreamingContent`를 지원하는 더 큰 책임을 갖게 됩니다.

### 옵션 2 - 전용 스트리밍 인터페이스 (클래스 반환)

옵션 1의 모든 변경 사항에 아래의 작은 차이점이 있습니다:

- Kernel과 SKFunction 스트리밍 API 인터페이스는 `IAsyncEnumerable<T>`도 구현하는 `StreamingFunctionResult<T>`를 반환합니다
- 커넥터 스트리밍 API 인터페이스는 `IAsyncEnumerable<T>`도 구현하는 `StreamingConnectorContent<T>`를 반환합니다

`StreamingConnectorContent` 클래스는 함수가 `StreamingFunctionResult` 메타데이터를 채우는 데 사용할 수 있는 청크가 아닌 요청과 관련된 정보를 전달하기 위한 하나의 방법으로 커넥터에 필요합니다.

## 사용자 경험 목표

옵션 2의 가장 큰 장점:

```csharp
// 호출자가 스트리밍에 대해 더 많이 알아야 할 때 스트리밍을 시작하기 전에 결과 참조를 가져올 수 있습니다.
var streamingResult = await kernel.RunStreamingAsync(function);
// streamingResult 속성으로 작업 수행

// streamingResult를 소비하려면 추가 await가 필요합니다:
await foreach(StreamingContent chunk content in await streamingResult)
```

다른 작업 사용은 매우 유사합니다(반복자를 가져오기 위해 추가 `await`만 필요)

```csharp
// Kernel에서 Raw 스트리밍 데이터 가져오기
await foreach(string update in await kernel.RunStreamingAsync<byte[]>(function, variables))

// Kernel에서 String으로 스트리밍 데이터 가져오기
await foreach(string update in await kernel.RunStreamingAsync<string>(function, variables))

// Kernel에서 StreamingContent로 스트리밍 데이터 가져오기
await foreach(StreamingContent update in await kernel.RunStreamingAsync<StreamingContent>(variables, function))
// 또는
await foreach(StreamingContent update in await kernel.RunStreamingAsync(function, variables)) // 위의 제네릭이 기본값)
{
    Console.WriteLine(update);
}

```

StreamingConnectorResult는 스트림이 소비되기 전의 결과에 대한 정보와 커넥터 수준에서 스트림이 소비하는 기본 객체(breaking glass)를 저장할 수 있는 클래스입니다.

```csharp

public sealed class StreamingConnectorResult<T> : IAsyncEnumerable<T>
{
    private readonly IAsyncEnumerable<T> _StreamingContentource;

    public object? InnerResult { get; private set; } = null;

    public StreamingConnectorResult(Func<IAsyncEnumerable<T>> streamingReference, object? innerConnectorResult)
    {
        this._StreamingContentource = streamingReference.Invoke();
        this.InnerResult = innerConnectorResult;
    }
}

interface ITextCompletion + IChatCompletion
{
    Task<StreamingConnectorResult<T>> GetStreamingContentAsync<T>();
    // T가 지원되지 않으면 예외 발생
    // 초기 커넥터
}
```

StreamingFunctionResult는 스트림이 소비되기 전의 결과에 대한 정보와 Kernel 및 SKFunctions에서 스트림이 소비하는 기본 객체(breaking glass)를 저장할 수 있는 클래스입니다.

```csharp
public sealed class StreamingFunctionResult<T> : IAsyncEnumerable<T>
{
    internal Dictionary<string, object>? _metadata;
    private readonly IAsyncEnumerable<T> _streamingResult;

    public string FunctionName { get; internal set; }
    public Dictionary<string, object> Metadata { get; internal set; }

    /// <summary>
    /// 내부 객체 참조. (Breaking glass).
    /// 각 커넥터는 결과를 나타내는 자체 내부 객체를 가집니다.
    /// </summary>
    public object? InnerResult { get; private set; } = null;

    /// <summary>
    /// 함수에서 사용하는 <see cref="SKContext"/> 인스턴스.
    /// </summary>
    internal SKContext Context { get; private set; }

    public StreamingFunctionResult(string functionName, SKContext context, Func<IAsyncEnumerable<T>> streamingResult, object? innerFunctionResult)
    {
        this.FunctionName = functionName;
        this.Context = context;
        this._streamingResult = streamingResult.Invoke();
        this.InnerResult = innerFunctionResult;
    }
}

interface ISKFunction
{
    // T 타입에서 가져오기 위한 확장 제네릭 메서드
    Task<StreamingFunctionResult<T>> InvokeStreamingAsync<T>(...);
}

static class KernelExtensions
{
    public static async Task<StreamingFunctionResult<T>> RunStreamingAsync<T>(this Kernel kernel, ISKFunction skFunction, ContextVariables? variables, CancellationToken cancellationToken)
    {
        ...
    }
}
```

## 장점

1. 옵션 1의 모든 장점 +
2. StreamingFunctionResults가 있으면 SK 개발자가 스트림을 소비하기 전에 결과에 대한 더 많은 세부 사항을 알 수 있습니다:
   - 기본 API에서 제공하는 메타데이터,
   - SKContext
   - 함수 이름 및 세부 사항
3. 스트리밍 사용 경험이 옵션 1과 매우 유사합니다(결과를 가져오기 위해 추가 await가 필요)
4. API가 비스트리밍 API와 유사하게 동작합니다(값을 가져오기 위한 결과 표현 반환)

## 단점

1. 옵션 1의 모든 단점 +
2. IAsyncEnumerable을 메서드 결과로 직접 전달할 수 없어 IAsyncEnumerator를 구현하는 Results 내부에 적용되는 델리게이트 접근 방식이 필요한 복잡성이 추가됩니다.
3. 응답 객체를 폐기하기 위해 Results에 IDisposable을 구현해야 하고 호출자가 결과의 폐기를 처리해야 하는 복잡성이 추가됩니다.
4. 호출자가 `StreamingFunctionResult`를 가져오는 즉시 호출자 구현이 이를 소비할 때까지(`IAsyncEnumerable` 열거) 네트워크 연결이 열려 있습니다.

## 결정 결과

옵션 1이 최선의 옵션으로 선택되었습니다. 옵션 2의 작은 이점이 단점에 설명된 복잡성을 정당화하지 못하기 때문입니다.

또한 커넥터 백엔드 응답과 관련된 메타데이터를 `StreamingContent.Metadata` 속성에 추가할 수 있도록 결정했습니다. 이를 통해 SK 개발자가 `StreamingConnectorResult`나 `StreamingFunctionResult` 없이도 메타데이터를 가져올 수 있습니다.
