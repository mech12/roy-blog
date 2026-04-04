---
# 이 항목들은 선택 사항입니다. 필요 없는 항목은 자유롭게 제거하세요.
status: accepted
contact: markwallace-microsoft
date: 2023-06-16
deciders: shawncal,dluc
consulted: 
informed: 
---
# 다양한 타입의 다중 네이티브 함수 인수 지원 추가

## 배경 및 문제 상황

네이티브 함수를 일반적인 C# 경험에 더 가깝게 만듭니다.

## 결정 동인

- 네이티브 스킬은 이제 원하는 수의 매개변수를 가질 수 있습니다. 매개변수는 동일한 이름의 컨텍스트 변수에서 채워집니다. 해당 이름의 컨텍스트 변수가 없으면 속성이나 기본 매개변수 값을 통해 제공된 기본값으로 채워지며, 기본값이 없으면 함수 호출이 실패합니다. 첫 번째 매개변수는 이름이나 기본값으로 입력을 가져오지 못할 경우 "input"에서도 채워질 수 있습니다.
- 설명은 이제 .NET DescriptionAttribute로 지정하고, DefaultValue는 DefaultValueAttribute로 지정합니다. C# 컴파일러는 DefaultValueAttribute를 인식하여 제공된 값의 타입이 매개변수의 타입과 일치하는지 확인합니다. 이제 선택적 매개변수 값을 사용하여 기본값을 지정할 수도 있습니다.
- SKFunction은 이제 민감도를 제외하면 순수한 마커 속성입니다. 유일한 목적은 스킬을 임포트할 때 어떤 public 멤버가 네이티브 함수로 임포트되는지 선별하는 것입니다. 델리게이트에서 직접 함수를 임포트할 때 이미 이 속성이 필요하지 않았으며, MethodInfo에서 임포트할 때도 해당 요구 사항이 해제되었습니다.
- SKFunctionContextParameterAttribute는 더 이상 사용되지 않으며 이후 제거될 예정입니다. 대신 DescriptionAttribute, DefaultValueAttribute, SKName 속성을 사용합니다. 시그니처에 정의되지 않은 변수에 접근해야 하는 드문 경우에는 메서드에 SKParameter 속성을 사용할 수 있으며, 이 속성에는 Description과 DefaultValue 선택적 속성이 있습니다.
- SKFunctionInputAttribute는 더 이상 사용되지 않으며 이후 제거될 예정입니다. 대신 DescriptionAttribute, DefaultValueAttribute, SKName 속성(후자는 이름으로 "Input" 사용)을 사용합니다. 그러나 SKName을 사용해야 하는 경우는 매우 드물어야 합니다.
- InvokeAsync는 이제 예외를 잡아서 컨텍스트에 저장합니다. 이는 네이티브 스킬이 컨텍스트와 직접 상호작용하는 대신 예외를 던져서 모든 실패를 처리해야 함을 의미합니다.
- 비동기 메서드의 "Async" 접미사를 제거하도록 이름 선택 휴리스틱이 업데이트되었습니다. 이제 메서드에 [SKName]을 사용해야 할 이유가 거의 없습니다.
- 완전성을 위해 ValueTasks를 반환 타입으로 지원하여 개발자가 이에 대해 고민할 필요가 없도록 했습니다. 그냥 작동합니다.
- 메서드에서 ILogger 또는 CancellationToken을 받을 수 있는 기능을 추가했습니다. 이들은 SKContext에서 채워집니다. 이로써 네이티브 함수에 SKContext를 전달해야 할 이유가 거의 없어졌습니다.
- 문자열이 아닌 인수 지원을 추가했습니다. 모든 C# 기본 타입과 많은 핵심 .NET 타입이 지원되며, 해당하는 TypeConverters를 사용하여 문자열 컨텍스트 변수를 적절한 타입으로 파싱합니다. TypeConverterAttribute가 지정된 사용자 정의 타입도 사용할 수 있으며, 관련 TypeConverter가 적절하게 사용됩니다. 이는 WinForms 같은 UI 프레임워크와 ASP.NET MVC에서 사용하는 것과 동일한 메커니즘입니다.
- 마찬가지로, 문자열이 아닌 반환 타입 지원을 추가했습니다.

## 결정 결과

[PR 1195](https://github.com/microsoft/semantic-kernel/pull/1195)

## 추가 정보

**예제**

_이전_:

```C#
[SKFunction("Adds value to a value")]
[SKFunctionName("Add")]
[SKFunctionInput(Description = "The value to add")]
[SKFunctionContextParameter(Name = "Amount", Description = "Amount to add")]
public Task<string> AddAsync(string initialValueText, SKContext context)
{
    if (!int.TryParse(initialValueText, NumberStyles.Any, CultureInfo.InvariantCulture, out var initialValue))
    {
        return Task.FromException<string>(new ArgumentOutOfRangeException(
            nameof(initialValueText), initialValueText, "Initial value provided is not in numeric format"));
    }

    string contextAmount = context["Amount"];
    if (!int.TryParse(contextAmount, NumberStyles.Any, CultureInfo.InvariantCulture, out var amount))
    {
        return Task.FromException<string>(new ArgumentOutOfRangeException(
            nameof(context), contextAmount, "Context amount provided is not in numeric format"));
    }

    var result = initialValue + amount;
    return Task.FromResult(result.ToString(CultureInfo.InvariantCulture));
}
```

_이후_:

```C#
[SKFunction, Description("Adds an amount to a value")]
public int Add(
    [Description("The value to add")] int value,
    [Description("Amount to add")] int amount) =>
    value + amount;
```

**예제**

_이전_:

```C#
[SKFunction("Wait a given amount of seconds")]
[SKFunctionName("Seconds")]
[SKFunctionInput(DefaultValue = "0", Description = "The number of seconds to wait")]
public async Task SecondsAsync(string secondsText)
{
    if (!decimal.TryParse(secondsText, NumberStyles.Any, CultureInfo.InvariantCulture, out var seconds))
    {
        throw new ArgumentException("Seconds provided is not in numeric format", nameof(secondsText));
    }

    var milliseconds = seconds * 1000;
    milliseconds = (milliseconds > 0) ? milliseconds : 0;

    await this._waitProvider.DelayAsync((int)milliseconds).ConfigureAwait(false);
}
```

_이후_:

```C#
[SKFunction, Description("Wait a given amount of seconds")]
public async Task SecondsAsync([Description("The number of seconds to wait")] decimal seconds)
{
    var milliseconds = seconds * 1000;
    milliseconds = (milliseconds > 0) ? milliseconds : 0;

    await this._waitProvider.DelayAsync((int)milliseconds).ConfigureAwait(false);
}
```

**예제**

_이전_:

```C#
[SKFunction("Add an event to my calendar.")]
[SKFunctionInput(Description = "Event subject")]
[SKFunctionContextParameter(Name = Parameters.Start, Description = "Event start date/time as DateTimeOffset")]
[SKFunctionContextParameter(Name = Parameters.End, Description = "Event end date/time as DateTimeOffset")]
[SKFunctionContextParameter(Name = Parameters.Location, Description = "Event location (optional)")]
[SKFunctionContextParameter(Name = Parameters.Content, Description = "Event content/body (optional)")]
[SKFunctionContextParameter(Name = Parameters.Attendees, Description = "Event attendees, separated by ',' or ';'.")]
public async Task AddEventAsync(string subject, SKContext context)
{
    ContextVariables variables = context.Variables;

    if (string.IsNullOrWhiteSpace(subject))
    {
        context.Fail("Missing variables input to use as event subject.");
        return;
    }

    if (!variables.TryGetValue(Parameters.Start, out string? start))
    {
        context.Fail($"Missing variable {Parameters.Start}.");
        return;
    }

    if (!variables.TryGetValue(Parameters.End, out string? end))
    {
        context.Fail($"Missing variable {Parameters.End}.");
        return;
    }

    CalendarEvent calendarEvent = new()
    {
        Subject = variables.Input,
        Start = DateTimeOffset.Parse(start, CultureInfo.InvariantCulture.DateTimeFormat),
        End = DateTimeOffset.Parse(end, CultureInfo.InvariantCulture.DateTimeFormat)
    };

    if (variables.TryGetValue(Parameters.Location, out string? location))
    {
        calendarEvent.Location = location;
    }

    if (variables.TryGetValue(Parameters.Content, out string? content))
    {
        calendarEvent.Content = content;
    }

    if (variables.TryGetValue(Parameters.Attendees, out string? attendees))
    {
        calendarEvent.Attendees = attendees.Split(new[] { ',', ';' }, StringSplitOptions.RemoveEmptyEntries);
    }

    this._logger.LogInformation("Adding calendar event '{0}'", calendarEvent.Subject);
    await this._connector.AddEventAsync(calendarEvent).ConfigureAwait(false);
}
```

_이후_:

```C#
[SKFunction, Description("Add an event to my calendar.")]
public async Task AddEventAsync(
    [Description("Event subject"), SKName("input")] string subject,
    [Description("Event start date/time as DateTimeOffset")] DateTimeOffset start,
    [Description("Event end date/time as DateTimeOffset")] DateTimeOffset end,
    [Description("Event location (optional)")] string? location = null,
    [Description("Event content/body (optional)")] string? content = null,
    [Description("Event attendees, separated by ',' or ';'.")] string? attendees = null)
{
    if (string.IsNullOrWhiteSpace(subject))
    {
        throw new ArgumentException($"{nameof(subject)} variable was null or whitespace", nameof(subject));
    }

    CalendarEvent calendarEvent = new()
    {
        Subject = subject,
        Start = start,
        End = end,
        Location = location,
        Content = content,
        Attendees = attendees is not null ? attendees.Split(new[] { ',', ';' }, StringSplitOptions.RemoveEmptyEntries) : Enumerable.Empty<string>(),
    };

    this._logger.LogInformation("Adding calendar event '{0}'", calendarEvent.Subject);
    await this._connector.AddEventAsync(calendarEvent).ConfigureAwait(false);
}
```
