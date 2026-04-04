---
# 이 항목들은 선택 사항입니다. 필요 없는 항목은 자유롭게 삭제하세요.
status: accepted
contact: teresaqhoang
date: 2023-12-06
deciders: markwallace, alliscode, SergeyMenshykh
consulted: markwallace, mabolan
informed: stephentoub
---

# Handlebars 프롬프트 템플릿 헬퍼

## 맥락 및 문제 설명

Semantic Kernel에서 프롬프트와 플래너를 렌더링하기 위한 템플릿 팩토리로 Handlebars를 사용하고자 합니다. Handlebars는 로직과 데이터로 동적 템플릿을 만들기 위한 간결하고 표현력 있는 구문을 제공합니다. 그러나 Handlebars는 다음과 같은 사용 사례에 관련된 일부 기능과 시나리오에 대한 내장 지원이 없습니다:

- 채팅 완성 커넥터용 역할이 있는 메시지로 텍스트 블록 표시.
- 커널에서 함수를 호출하고 매개변수를 전달.
- 템플릿 컨텍스트에서 변수 설정 및 가져오기.
- 연결, 산술, 비교, JSON 직렬화 등의 일반적인 작업 수행.
- 렌더링된 템플릿에 대한 다양한 출력 타입 및 형식 지원.

따라서 이러한 격차를 해결하고 프롬프트 및 플래너 엔지니어가 템플릿을 작성하는 일관적이고 편리한 방법을 제공하기 위해 사용자 정의 헬퍼로 Handlebars를 확장해야 합니다.

첫째, **_내장 Handlebars 헬퍼가 제공하지 않는 일반적인 작업 및 유틸리티를 위한 정의된 사용자 정의 시스템 헬퍼 세트를 내장_**하여 이를 수행합니다:

- Handlebars 템플릿 팩토리에서 실행할 수 있는 기능을 완전히 제어할 수 있습니다.
- 내장 Handlebars 헬퍼가 제공하지 않지만 모델이 일반적으로 할루시네이션하는 일반적인 작업 및 유틸리티에 대한 헬퍼를 제공하여 템플릿 팩토리의 기능과 사용성을 향상시킵니다.
- 헬퍼를 사용하여 템플릿 데이터/인수에 대한 간단하거나 복잡한 로직 또는 변환을 수행할 수 있으므로 렌더링된 템플릿의 표현력과 가독성을 향상시킵니다.
- 사용자에게 유연성과 편의성을 제공하여 다음을 할 수 있습니다:

  - 구문 선택, 그리고
  - 특정 헬퍼를 확장, 추가 또는 생략

  하여 필요와 선호에 가장 적합하도록 합니다.

- 출력 타입, 형식 또는 오류 처리와 같이 다른 동작이나 요구 사항을 가질 수 있는 특정 작업 또는 유틸리티의 사용자 정의를 허용합니다.

이러한 헬퍼는 인수 평가, 작업 또는 유틸리티 실행, 결과를 템플릿에 기록하는 것을 처리합니다. 이러한 작업의 예로는 `{{concat string1 string2 ...}}`, `{{equal value1 value2}}`, `{{json object}}`, `{{set name=value}}`, `{{get name}}`, `{{or condition1 condition2}}` 등이 있습니다.

둘째, **_커널에 등록된 함수를 헬퍼로 노출_**해야 합니다. 이에 대한 옵션은 아래에 상세히 설명됩니다.

## 결정 요인

- 불필요한 복잡성이나 불일치를 도입하지 않고 기존 Handlebars 헬퍼, 구문, 헬퍼 로딩 메커니즘을 최대한 활용하고자 합니다.
- 프롬프트 및 SK 엔지니어에게 유용하고 직관적인 헬퍼를 제공하고자 합니다.
- 헬퍼가 잘 문서화되고, 테스트되고, 유지 관리되며, 서로 또는 내장 Handlebars 헬퍼와 충돌하지 않도록 보장하고자 합니다.
- 렌더링된 템플릿에 대해 텍스트, JSON 또는 복합 객체와 같은 다양한 출력 타입 및 형식을 지원하고 템플릿이 원하는 출력 타입을 지정할 수 있도록 하고자 합니다.

## 검토한 옵션

커널 함수를 사용자 정의 헬퍼로 확장하기 위해 다음 옵션을 검토했습니다:

**1. 커널에서 함수를 호출하기 위한 단일 헬퍼 사용.** 이 옵션은 `{{invoke pluginName-functionName param1=value1 param2=value2 ...}}`와 같은 제네릭 헬퍼를 사용하여 커널의 모든 함수를 호출하고 매개변수를 전달합니다. 헬퍼가 함수 실행, 매개변수 및 결과 변환, 결과를 템플릿에 기록하는 것을 처리합니다.

**2. 커널의 각 함수에 대해 별도의 헬퍼 사용.** 이 옵션은 `{{pluginName-functionName param1=value1 param2=value2 ...}}`와 같은 각 함수에 대한 새 헬퍼를 등록하여 함수 실행, 매개변수 및 결과 변환, 결과를 템플릿에 기록하는 것을 처리합니다.

## 장단점

### 1. 커널에서 함수를 호출하기 위한 단일 제네릭 헬퍼 사용

장점:

- 하나의 헬퍼 `invoke`만 정의하고 업데이트하면 되므로 헬퍼의 등록과 유지 관리가 단순화됩니다.
- 플러그인이나 함수 이름, 매개변수 세부 사항 또는 결과에 관계없이 커널의 모든 함수를 호출하기 위한 일관되고 통일된 구문을 제공합니다.
- 출력 타입 처리, 실행 제한 또는 오류 처리 등 커널 함수의 사용자 정의와 특수 로직을 허용합니다.
- 함수에 매개변수를 전달하기 위해 위치 인수 또는 이름 인수, 해시 인수를 사용할 수 있습니다.

단점:

- 함수 이름과 매개변수가 제네릭 헬퍼 호출에 감싸져 있으므로 템플릿의 표현력과 가독성이 떨어집니다.
- 모델이 학습하고 추적해야 할 추가 구문이 생겨 렌더링 중 더 많은 오류로 이어질 수 있습니다.

### 2. 커널의 _각_ 함수에 대한 제네릭 헬퍼 사용

장점:

- 옵션 1의 모든 장점을 가지면서, 함수 이름과 매개변수가 템플릿에 직접 작성되므로 템플릿의 표현력과 가독성이 크게 향상됩니다.
- 각 헬퍼가 등록 및 실행에 대해 동일한 템플릿화된 로직을 따르므로 각 함수 처리의 유지 관리가 용이합니다.

단점:

- 함수 이름이나 매개변수 이름이 내장 Handlebars 헬퍼나 커널 변수와 일치하면 충돌이나 혼동이 발생할 수 있습니다.

## 결정 결과

옵션 2: 커널의 모든 함수를 호출하기 위한 특수 헬퍼를 제공하기로 결정했습니다. 이 헬퍼들은 등록된 각 함수에 대해 동일한 로직과 구문을 따릅니다. 특수 유틸리티 로직이나 동작을 가능하게 하는 사용자 정의 시스템 헬퍼와 함께, 이 접근 방식이 Handlebars 템플릿 팩토리와 사용자를 위해 단순성, 표현력, 유연성, 기능성 사이의 최적 균형을 제공한다고 믿습니다.

이 접근 방식으로:

- 내장 [Handlebars.Net 헬퍼](https://github.com/Handlebars-Net/Handlebars.Net.Helpers)를 사용할 수 있습니다.
- 기본적으로 등록되는 유틸리티 헬퍼를 제공합니다.
- 기본적으로 등록되는 프롬프트 헬퍼(예: 채팅 메시지, or)를 제공합니다.
- `Kernel`에 등록된 모든 플러그인 함수를 등록합니다.
- 고객이 헬퍼로 등록되는 플러그인과 헬퍼 시그니처의 구문을 제어할 수 있습니다.
  - 기본적으로 [HandlebarsHelperOptions](https://github.com/Handlebars-Net/Handlebars.Net.Helpers/blob/8f7c9c082e18845f6a620bbe34bf4607dcba405b/src/Handlebars.Net.Helpers/Options/HandlebarsHelpersOptions.cs#L12)에 정의된 모든 옵션을 준수합니다.
  - 또한 이 구성을 확장하여 사용자가 사용자 정의 헬퍼를 등록할 수 있도록 설정할 수 있는 `RegisterCustomHelpersCallback` 옵션을 포함합니다.
- `KernelArguments` 객체를 통해 커널 함수 인수(함수 변수 및 실행 설정)에 쉽게 접근할 수 있습니다.
- 고객이 플러그인 함수가 헬퍼로 등록되는 시점을 제어할 수 있습니다.
  - 기본적으로 템플릿이 렌더링될 때 수행됩니다.
  - 선택적으로 Plugin 컬렉션을 전달하여 Handlebars 템플릿 팩토리가 생성될 때 수행할 수 있습니다.
- 내장 헬퍼, 변수 또는 커널 객체 간 충돌이 발생하면:
  - 문제가 무엇인지 명확하게 설명하는 오류를 발생시키며,
  - 고객이 기본 헬퍼를 등록하지 않는 옵션을 포함하여 자체 구현과 오버라이드를 제공할 수 있습니다. `Options.Categories`를 빈 배열 `[]`로 설정하면 됩니다.

또한 헬퍼를 설계하고 구현하기 위한 가이드라인과 모범 사례를 따르기로 결정했습니다:

- 각 헬퍼의 목적, 구문, 매개변수, 동작을 문서화하고 예시와 테스트를 제공합니다.
- 헬퍼의 이름을 명확하고 일관되게 지정하고, 내장 Handlebars 헬퍼나 커널 함수 또는 변수와의 충돌이나 혼동을 방지합니다.
  - 사용자 정의 시스템 헬퍼에는 독립 함수 이름을 사용합니다(예: json, set)
  - 커널 함수를 처리하기 위해 등록된 헬퍼에는 구분자 "`-`"를 사용하여 시스템 또는 내장 Handlebars 헬퍼와 구별합니다.
- 헬퍼에 매개변수를 전달하기 위해 위치 인수와 해시 인수를 모두 지원하고, 필요한 타입과 개수에 대해 인수를 검증합니다.
- 복합 타입이나 JSON 스키마를 포함하여 헬퍼의 출력 타입, 형식, 오류를 처리합니다.
- 헬퍼를 성능적이고 안전한 방식으로 구현하고, 템플릿 컨텍스트나 데이터에 대한 부작용이나 원치 않는 수정을 방지합니다.

효과적으로 Handlebars 템플릿 엔진에는 네 가지 버킷의 헬퍼가 활성화됩니다:

1. 다음을 포함하는 Handlebars 라이브러리의 기본 헬퍼:
   - 루프와 조건을 가능하게 하는 [내장 헬퍼](https://handlebarsjs.com/guide/builtin-helpers.html) (#if, #each, #with, #unless)
   - [Handlebars.Net.Helpers](https://github.com/Handlebars-Net/Handlebars.Net.Helpers/wiki)
2. 커널의 함수
3. 프롬프트 엔지니어에게 유용한 헬퍼 (예: message, or)
4. 템플릿 데이터나 인수에 대한 간단한 로직 또는 변환을 수행하는 데 사용할 수 있는 유틸리티 헬퍼 (예: set, get, json, concat, equals, range, array)

### Handlebars 프롬프트 템플릿 엔진의 의사 코드

내장 헬퍼가 있는 Handlebars 프롬프트 템플릿 팩토리의 프로토타입 구현은 다음과 같을 수 있습니다:

```csharp
/// Handlebars 헬퍼(내장 및 사용자 정의)에 대한 옵션.
public sealed class HandlebarsPromptTemplateOptions : HandlebarsHelpersOptions
{
  // 내장 시스템 헬퍼를 추적하는 카테고리
  public enum KernelHelperCategories
  {
    Prompt,
    Plugin,
    Context,
    String,
    ...
  }

  /// 플러그인 이름과 함수 이름을 구분하기 위한 기본 문자.
  public string DefaultNameDelimiter { get; set; } = "-";

  /// 사용자 정의 헬퍼 등록을 위한 델리게이트.
  public delegate void RegisterCustomHelpersCallback(IHandlebars handlebarsInstance, KernelArguments executionContext);

  /// 사용자 정의 헬퍼 등록을 위한 콜백.
  public RegisterCustomHelpersCallback? RegisterCustomHelpers { get; set; } = null;

  // 의사 코드, KernelHelperCategories와 기본 HandlebarsHelpersOptions.Categories의 조합.
  public List<Enum> AllCategories = KernelHelperCategories.AddRange(Categories);
}
```

```csharp
// Handlebars 프롬프트 템플릿
internal class HandlebarsPromptTemplate : IPromptTemplate
{
  public async Task<string> RenderAsync(Kernel kernel, KernelArguments arguments, CancellationToken cancellationToken = default)
  {
    arguments ??= new();
    var handlebarsInstance = HandlebarsDotNet.Handlebars.Create();

    // 커널 함수용 헬퍼 추가
    KernelFunctionHelpers.Register(handlebarsInstance, kernel, arguments, this._options.PrefixSeparator, cancellationToken);

    // 내장 시스템 헬퍼 추가
    KernelSystemHelpers.Register(handlebarsInstance, arguments, this._options);

    // 사용자 정의 헬퍼 등록
    if (this._options.RegisterCustomHelpers is not null)
    {
      this._options.RegisterCustomHelpers(handlebarsInstance, arguments);
    }
    ...

    return await Task.FromResult(prompt).ConfigureAwait(true);
  }
}

```

```csharp
/// 커널 함수를 헬퍼로 등록하기 위한 확장 클래스.
public static class KernelFunctionHelpers
{
  public static void Register(
    IHandlebars handlebarsInstance,
    Kernel kernel,
    KernelArguments executionContext,
    string nameDelimiter,
    CancellationToken cancellationToken = default)
  {
      kernel.Plugins.GetFunctionsMetadata().ToList()
          .ForEach(function =>
              RegisterFunctionAsHelper(kernel, executionContext, handlebarsInstance, function, nameDelimiter, cancellationToken)
          );
  }

  private static void RegisterFunctionAsHelper(
    Kernel kernel,
    KernelArguments executionContext,
    IHandlebars handlebarsInstance,
    KernelFunctionMetadata functionMetadata,
    string nameDelimiter,
    CancellationToken cancellationToken = default)
  {
    // 각 함수에 대한 헬퍼 등록
    handlebarsInstance.RegisterHelper(fullyResolvedFunctionName, (in HelperOptions options, in Context context, in Arguments handlebarsArguments) =>
    {
      // 템플릿 인수에서 매개변수 가져오기; 필수 매개변수 및 타입 일치 확인

      // HashParameterDictionary인 경우
      ProcessHashArguments(functionMetadata, executionContext, handlebarsArguments[0] as IDictionary<string, object>, nameDelimiter);

      // 그 외
      ProcessPositionalArguments(functionMetadata, executionContext, handlebarsArguments);

      KernelFunction function = kernel.Plugins.GetFunction(functionMetadata.PluginName, functionMetadata.Name);

      InvokeSKFunction(kernel, function, GetKernelArguments(executionContext), cancellationToken);
    });
  }
  ...
}
```

```csharp
/// 추가 헬퍼를 커널 시스템 헬퍼로 등록하기 위한 확장 클래스.
public static class KernelSystemHelpers
{
    public static void Register(IHandlebars handlebarsInstance, KernelArguments arguments, HandlebarsPromptTemplateOptions options)
    {
        RegisterHandlebarsDotNetHelpers(handlebarsInstance, options);
        RegisterSystemHelpers(handlebarsInstance, arguments, options);
    }

    // https://github.com/Handlebars-Net/Handlebars.Net.Helpers에서 제공하는 모든 헬퍼 등록.
    private static void RegisterHandlebarsDotNetHelpers(IHandlebars handlebarsInstance, HandlebarsPromptTemplateOptions helperOptions)
    {
        HandlebarsHelpers.Register(handlebarsInstance, optionsCallback: options =>
        {
            ...helperOptions
        });
    }

    // 커널을 지원하기 위해 SK 팀이 만든 모든 헬퍼 등록.
    private static void RegisterSystemHelpers(
      IHandlebars handlebarsInstance, KernelArguments arguments, HandlebarsPromptTemplateOptions helperOptions)
    {
      // 각 내장 헬퍼는 Handlebars.Net.Helpers에서 사용하는 것과 동일한 패턴을 따라 자체 정의 클래스를 가집니다.
      // https://github.com/Handlebars-Net/Handlebars.Net.Helpers
      if (helperOptions.AllCategories contains helperCategory)
      ...
      KernelPromptHelpers.Register(handlebarsContext);
      KernelPluginHelpers.Register(handlebarsContext);
      KernelStringHelpers..Register(handlebarsContext);
      ...
    }
}
```

**참고: 이것은 설명 목적으로만 사용되는 프로토타입 구현입니다.**

Handlebars는 렌더링 시 변수로 다양한 객체 타입을 지원합니다. 이를 통해 호출 전에 객체를 직렬화하거나 역직렬화하지 않고도 시맨틱 함수에서 문자열 대신 객체를 직접 사용할 수 있습니다. 예를 들어 배열을 반복하거나 복합 객체의 속성에 접근할 수 있습니다.
