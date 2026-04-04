---
# 이 항목들은 선택 사항입니다. 필요 없는 항목은 자유롭게 제거하세요.
status: accepted
contact: sergeymenshykh
date: 2024-10-07
deciders: markwallace, sergeymenshykh, westey-m, 
consulted: eiriktsarpalis, stephentoub
informed:
---

# SK에 JsonSerializerOptions를 통합하는 방법 검토

## 컨텍스트 및 문제 설명
현재 SK는 함수 파라미터 및 반환 타입에 대한 스키마 생성, 마샬링 프로세스의 일부로 JSON에서 대상 타입으로의 역직렬화, AI 모델의 SK 간 직렬화 등을 위해 JSON 직렬화 및 스키마 생성 기능에 의존합니다.
  
현재 직렬화 코드는 JsonSerializerOptions(JSOs)를 사용하지 않거나, 커스텀 JSOs를 제공할 수 없는 특정 목적을 위해 하드코딩된 미리 정의된 JSOs를 사용합니다. 이것은 JSON 직렬화가 기본적으로 리플렉션을 사용하는 비-AOT 시나리오에서는 완벽하게 작동합니다. 그러나 필요한 모든 리플렉션 API를 지원하지 않는 Native AOT 앱에서는 리플렉션 기반 직렬화가 작동하지 않으며 크래시가 발생합니다.
   
Native-AOT 시나리오에서 직렬화를 활성화하려면, 모든 직렬화 코드가 `JsonSerializerContext` 기본 클래스로 표현되는 소스 생성 컨텍스트 계약을 사용해야 합니다. 자세한 내용은 [System.Text.Json에서 소스 생성 사용 방법](https://learn.microsoft.com/en-us/dotnet/standard/serialization/system-text-json/source-generation?pivots=dotnet-8-0#specify-source-generation-mode) 문서를 참조하세요. 또한 SK 공개 API를 통해 이러한 소스 생성 클래스를 JSON 직렬화 기능에 공급할 수 있는 방법이 있어야 합니다.
   
이 ADR은 Native-AOT가 활성화된 SK 컴포넌트의 JSON 직렬화 코드에 소스 생성 계약이 구성된 JSOs를 전달하기 위한 잠재적 옵션을 설명합니다.

## 결정 요인

- 외부 소스 생성 컨텍스트 계약을 SK JSON 직렬화 기능에 제공할 수 있어야 합니다.
- 소스 생성 컨텍스트 계약을 SK 컴포넌트에 공급하는 것이 직관적이고 쉬워야 합니다.
- Microsoft.Extensions.AI와 쉽게 통합할 수 있어야 합니다.

## 고려된 옵션

- 옵션 #1: 모든 SK 컴포넌트에 대한 하나의 전역 JSOs
- 옵션 #2: SK 컴포넌트별 JSOs
- 옵션 #3: SK 컴포넌트 작업별 JSOs

## 옵션 #1: 모든 SK 컴포넌트에 대한 하나의 전역 JSOs
이 옵션은 `Kernel` 클래스에 `JsonSerializerOptions` 타입의 새 `JsonSerializerOptions` 속성을 추가하는 것을 전제로 합니다. 모든 외부 소스 생성 컨텍스트 계약이 여기에 등록되며, JSOs가 필요한 모든 SK 컴포넌트가 여기서 해석합니다:

```csharp
public sealed class MyPlugin { public Order CreateOrder() => new(); }

public sealed class Order { public string? Number { get; set; } }

[JsonSerializable(typeof(Order))]
internal sealed partial class OrderJsonSerializerContext : JsonSerializerContext
{
}

public async Task TestAsync()
{
    JsonSerializerOptions options = new JsonSerializerOptions();
    options.TypeInfoResolverChain.Add(OrderJsonSerializerContext.Default);

    Kernel kernel = new Kernel();
    kernel.JsonSerializerOptions = options;

    // 다음 Kernel 확장 메서드들은 모두 `Kernel.JsonSerializerOptions` 속성에 구성된 JSOs를 사용합니다
    kernel.CreateFunctionFromMethod(() => new Order());
    kernel.CreateFunctionFromPrompt("<prompt>");
    kernel.CreatePluginFromFunctions("<plugin>", [kernel.CreateFunctionFromMethod(() => new Order())]);
    kernel.CreatePluginFromType<MyPlugin>("<plugin>");
    kernel.CreatePluginFromPromptDirectory("<directory>", "<plugin>");
    kernel.CreatePluginFromObject(new MyPlugin(), "<plugin>");

    // AI 커넥터도 `Kernel.JsonSerializerOptions` 속성을 사용할 수 있습니다
    var onnxService = new OnnxRuntimeGenAIChatCompletionService("<modelId>", "<modelPath>");
    var res = await onnxService.GetChatMessageContentsAsync(new ChatHistory(), new PromptExecutionSettings(), kernel);

    // 아래 API들은 `Kernel` 인스턴스에 접근할 수 없으므로 `Kernel.JsonSerializerOptions` 속성을 사용할 수 없습니다
    KernelFunctionFactory.CreateFromMethod(() => new Order(), options);
    KernelFunctionFactory.CreateFromPrompt("<prompt>", options);

    KernelPluginFactory.CreateFromObject(new MyPlugin(), options, "<plugin>");
    KernelPluginFactory.CreateFromType<MyPlugin>(options, "<plugin>");
    KernelPluginFactory.CreateFromFunctions("<plugin>", [kernel.CreateFunctionFromMethod(() => new Order())]);
}
```

장점:  
- 모든 SK 컴포넌트가 한 곳에서 구성된 JSOs를 사용합니다. 필요한 경우 다른 옵션을 가진 kernel 클론을 제공할 수 있습니다.
   
단점:  
- SK 컴포넌트가 아직 kernel에 의존하지 않는 경우 의존하도록 변경해야 할 수 있습니다.
- JSOs가 초기화되는 방식에 따라, 이 옵션은 AOT 앱에서 비-AOT 호환 API 사용에 대해 다른 옵션만큼 명시적이지 않아, 런타임 오류를 기반으로 소스 생성 계약을 등록하기 위한 시행착오가 필요할 수 있습니다.
- 위와 유사하게, 어떤 컴포넌트/API가 JSOs를 필요로 하는지 명확하지 않아 런타임에서 발견이 지연될 수 있습니다.
- SK에서 JSOs를 제공하는 또 다른 방법을 추가하게 됩니다. 저수준 KernelFunctionFactory와 KernelPluginFactory는 메서드 파라미터를 통해 JSOs를 받습니다.
- SK AI 커넥터는 작업에서 kernel의 **선택적** 인스턴스를 받는데, 이는 혼합된 신호를 보냅니다. 한편으로는 선택적이므로 AI 커넥터가 kernel 없이 작동할 수 있다는 의미이고, 다른 한편으로는 kernel이 제공되지 않으면 AOT 앱에서 작업이 실패합니다.
- 하나 이상의 kernel 인스턴스가 필요한 시나리오에서, 각 인스턴스가 고유한 JSOs를 가질 수 있으며, 함수가 생성된 kernel의 JSOs가 함수의 수명 동안 사용됩니다. 함수가 호출될 수 있는 다른 kernel의 JSOs는 적용되지 않으며, 함수가 생성된 kernel의 JSOs가 사용됩니다.

### Kernel에 JSON Serializer Options(JSOs)를 제공하는 방법:
1. `Kernel` 생성자를 통해.
    ```csharp
    private readonly JsonSerializerOptions? _serializerOptions = null;

    // 기존 AOT 비호환 생성자
    [RequiresUnreferencedCode("Uses reflection to handle various aspects of JSON serialization in SK, making it incompatible with AOT scenarios.")]
    [RequiresDynamicCode("Uses reflection to handle various aspects of JSON serialization in SK, making it incompatible with AOT scenarios.")]
    public Kernel(IServiceProvider? services = null,KernelPluginCollection? plugins = null) {}

    // 새 AOT 호환 생성자
    public Kernel(JsonSerializerOptions jsonSerializerOptions, IServiceProvider? services = null,KernelPluginCollection? plugins = null) 
    { 
        this._serializerOptions = jsonSerializerOptions;
        this._serializerOptions.MakeReadOnly(); // 초기 JSOs로 생성된 SK 컴포넌트가 인식하지 못할 수 있는 변경 방지.
    }

    public JsonSerializerOptions JsonSerializerOptions => this._serializerOptions ??= JsonSerializerOptions.Default;
    ```
    장점:
    - 컴파일 시간에 비-AOT 호환 생성자 사용에 대한 AOT 관련 경고가 표시됩니다.

2. `Kernel.JsonSerializerOptions` 속성 setter를 통해
    ```csharp
    private readonly JsonSerializerOptions? _serializerOptions = null;

    public JsonSerializerOptions JsonSerializerOptions
    {
        get
        {
            return this._serializerOptions ??= ??? // JsonSerializerOptions.Default는 비-AOT 시나리오에서 작동하지만 AOT에서는 실패합니다.
        }
        set
        {
            this._serializerOptions = value;
        }
    }
    ```
    단점:
    - AOT 애플리케이션에서 kernel 초기화 중에 AOT 경고가 생성되지 않아, 런타임 실패가 발생합니다.
    - SK 컴포넌트(KernelFunction은 생성자를 통해 JSOs를 받음)가 생성된 후에 할당된 JSOs는 해당 컴포넌트에 의해 인식되지 않습니다.

3. DI
    요구 사항이 구체화된 후 결정 예정.

## 옵션 #2: SK 컴포넌트별 JSOs
이 옵션은 컴포넌트의 인스턴스화 사이트 또는 생성자에서 JSOs를 제공하는 것을 전제로 합니다:
```csharp
    public sealed class Order { public string? Number { get; set; } }

    [JsonSerializable(typeof(Order))]
    internal sealed partial class OrderJsonSerializerContext : JsonSerializerContext
    {
    }

    JsonSerializerOptions options = new JsonSerializerOptions();
    options.TypeInfoResolverChain.Add(OrderJsonSerializerContext.Default);

    // 다음 kernel 확장 메서드들은 모두 해당 파라미터로 명시적으로 제공된 JSOs를 받습니다:
    kernel.CreateFunctionFromMethod(() => new Order(), options);
    kernel.CreateFunctionFromPrompt("<prompt>", options);
    kernel.CreatePluginFromFunctions("<plugin>", [kernel.CreateFunctionFromMethod(() => new Order(), options)]);
    kernel.CreatePluginFromType<MyPlugin>("<plugin>", options);
    kernel.CreatePluginFromPromptDirectory("<directory>", "<plugin>", options);
    kernel.CreatePluginFromObject(new MyPlugin(), "<plugin>", options);

    // AI 커넥터는 호출 사이트가 아닌 인스턴스화 사이트에서 JSOs를 받습니다.
    var onnxService = new OnnxRuntimeGenAIChatCompletionService("<modelId>", "<modelPath>", options);
    var res = await onnxService.GetChatMessageContentsAsync(new ChatHistory(), new PromptExecutionSettings());

    // 아래 API들은 이미 인스턴스화 사이트에서 JSOs를 받습니다.
    KernelFunctionFactory.CreateFromMethod(() => new Order(), options);
    KernelFunctionFactory.CreateFromPrompt("<prompt>", options);

    KernelPluginFactory.CreateFromObject(new MyPlugin(), options, "<plugin>");
    KernelPluginFactory.CreateFromType<MyPlugin>(options, "<plugin>");
    KernelPluginFactory.CreateFromFunctions("<plugin>", [kernel.CreateFunctionFromMethod(() => new Order())]);
```
장점:
- 각 컴포넌트 인스턴스화 사이트에서 컴파일 시간에 AOT 경고가 생성됩니다.
- 모든 SK 컴포넌트에서 동일한 방식으로 JSOs를 사용합니다.
- SK 컴포넌트가 Kernel에 의존할 필요가 없습니다.

단점:
- 소스 생성 컨텍스트를 등록하는 중앙 위치가 없습니다. 이것은 애플리케이션이 서로 상속 관계를 가질 수 있는 다양한 클래스에 걸쳐 많은 부트스트래핑 코드를 가진 경우에는 장점이 될 수 있습니다.

AI 커넥터는 생성자의 파라미터로 또는 선택적 속성으로 JSOs를 받을 수 있습니다. 하나 또는 몇 개의 커넥터가 AOT 호환으로 리팩토링될 때 결정됩니다.

## 옵션 #3: SK 컴포넌트 작업별 JSOs
이 옵션은 인스턴스화 사이트가 아닌 컴포넌트 작업 호출 사이트에서 JSOs를 제공하는 것을 전제로 합니다.

장점:
- 각 컴포넌트 작업 호출 사이트에서 컴파일 시간에 AOT 경고가 생성됩니다.

단점:
- 외부 소스 생성 계약이 필요한 모든 SK 컴포넌트에 대해 JSOs를 받는 새로운 작업/메서드 오버로드를 추가해야 합니다.
- SK에서 JSOs를 제공하는 또 다른 방법을 추가하게 됩니다. 저수준 KernelFunctionFactory와 KernelPluginFactory는 메서드 파라미터를 통해 JSOs를 받습니다.
- 모든 SK 컴포넌트에 적용할 수 없습니다. KernelFunction은 스키마 생성 목적으로 호출되기 전에 JSOs가 필요합니다.
- 메서드 호출마다 JSOs가 생성될 수 있는 비효율적인 JSOs 사용을 장려하며, 이는 메모리 면에서 비용이 높을 수 있습니다.

## 결정 결과
"옵션 #2 SK 컴포넌트별 JSOs"가 다른 옵션보다 선호되었습니다. 이 옵션은 컴포넌트의 인스턴스화/생성 사이트에서 JSOs를 제공하는 명시적이고, 통일되고, 명확하고, 간단하고, 효과적인 방법을 제공하기 때문입니다.
