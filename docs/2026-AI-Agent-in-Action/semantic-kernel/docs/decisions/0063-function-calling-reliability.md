---
status: proposed
contact: sergeymenshykh
date: 2025-01-21
deciders: dmytrostruk, markwallace, rbarreto, sergeymenshykh, westey-m,
consulted: stephentoub
---

# 함수 호출 신뢰성

## 맥락과 문제 설명
SK 함수 호출의 신뢰성을 결정하는 핵심 측면 중 하나는 AI 모델이 알린 정확한 이름으로 함수를 호출하는 능력입니다.

원하는 것보다 더 자주 AI 모델은 함수를 호출할 때 함수 이름을 환각합니다. 대부분의 경우,
함수 이름에서 환각되는 것은 단 한 문자이며 나머지 함수 이름은 정확합니다. 이 문자는 하이픈 `-`으로, SK가 함수를 고유하게 식별하기 위해 모든 플러그인에 걸쳐 플러그인 이름과 함수 이름 사이의 구분자로 사용하여 함수의 정규화된 이름(FQN)을 형성합니다. 예를 들어, 플러그인 이름이 `foo`이고 함수 이름이 `bar`인 경우, 함수의 FQN은 `foo-bar`입니다. 지금까지 관찰된 환각된 이름은 `foo_bar`, `foo.bar`입니다.

### 이슈 #1: 밑줄 구분자 환각 - `foo_bar`

AI 모델이 밑줄 구분자 `_`를 환각하면, SK는 이 오류를 감지하고 _"Error: Function call request for a function that wasn't defined."_ 메시지를
후속 요청에서 원래 함수 호출과 함께 함수 결과의 일부로 모델에 반환합니다.
일부 모델은 이 오류에서 자동으로 복구하여 올바른 이름으로 함수를 호출할 수 있지만, 다른 모델은 그렇지 않습니다.

### 이슈 #2: 점 구분자 환각 - `foo.bar`

이 이슈는 이슈 #1과 유사하지만, 이 경우 구분자는 `.`입니다. SK가 이 오류를 감지하고 후속 요청에서 AI 모델에 반환하려고 시도하지만,
요청이 다음 예외와 함께 실패합니다: _"Invalid messages[3].tool_calls[0].function.name: string does not match pattern. Expected a string that matches the pattern ^[a-zA-Z0-9_-]+$."_
이 실패의 이유는 환각된 구분자 `.`가 함수 이름에 허용되지 않기 때문입니다. 본질적으로, 모델이 자체적으로 환각한 함수 이름을 거부합니다.

### 이슈 #3: 자동 복구 메커니즘의 신뢰성

알려진 이름과 다른 이름으로 함수가 호출되면, 함수를 찾을 수 없어 위에서 설명한 대로 AI 모델에 오류 메시지가 반환됩니다.
이 오류 메시지는 AI 모델에 문제에 대한 힌트를 제공하여 올바른 이름으로 함수를 호출하여 자동 복구하도록 돕습니다.
그러나 자동 복구 메커니즘은 서로 다른 모델에서 안정적으로 작동하지 않습니다.
예를 들어, `gpt-4o-mini(2024-07-18)` 모델에서는 작동하지만 `gpt-4(0613)`와 `gpt-4o(2024-08-06)` 모델에서는 실패합니다.
AI 모델이 복구할 수 없는 경우, 단순히 오류 메시지의 변형을 반환합니다: _"I'm sorry, but I can't provide the answer right now due to a system error. Please try again later."_

## 결정 동인

- 함수 이름 환각 발생을 최소화합니다.
- 자동 복구 메커니즘의 신뢰성을 향상시킵니다.

## 검토한 옵션
일부 옵션은 상호 배타적이지 않으며 결합할 수 있습니다.

### 옵션 1: 함수 FQN에 함수 이름만 사용

이 옵션은 함수의 FQN으로 함수 이름만 사용하는 것을 제안합니다. 예를 들어, 플러그인 `foo`의 함수 `bar`의 FQN은 단순히 `bar`가 됩니다.
함수 이름만 사용함으로써, 자주 환각되는 구분자 `-`의 필요성을 제거합니다.

장점:
- 환각의 원인(구분자)을 제거하여 함수 이름 환각을 줄이거나 제거합니다(이슈 #1 및 #2).
- 함수 FQN에서 플러그인 이름이 소비하는 토큰 수를 줄입니다.

단점:
- 함수 이름이 모든 플러그인에 걸쳐 고유하지 않을 수 있습니다. 예를 들어, 두 플러그인에 같은 이름의 함수가 있으면, 두 함수 모두 AI 모델에 제공되고 SK는 처음 발견하는 함수를 호출합니다.
    - [ADR 검토 회의에서] 중복이 발견되면, 플러그인 이름을 중복 항목이나 모든 알려진 함수에 동적으로 추가할 수 있습니다.
- 플러그인 이름의 부재로 인해 함수 이름에 대한 컨텍스트가 부족할 수 있습니다. 예를 들어, `GetData` 함수는 `Weather` 플러그인의 컨텍스트에서와 `Stocks` 플러그인의 컨텍스트에서 다른 의미를 가집니다.
    - [ADR 검토 회의에서] 플러그인 이름/컨텍스트는 플러그인 개발자가 함수 이름이나 설명에 추가하거나 SK가 함수 설명에 자동으로 추가할 수 있습니다.
- 환각된 함수 이름을 처리할 수 없습니다. 예를 들어, AI 모델이 `bar` 대신 함수 FQN을 `b0r`로 환각하는 경우.


가능한 구현:
```csharp
// 작업 수준에서
FunctionChoiceBehaviorOptions options = new new()
{
    UseFunctionNameAsFqn = true
};

var settings = new AzureOpenAIPromptExecutionSettings() { FunctionChoiceBehavior = FunctionChoiceBehavior.Auto(options) };

var result = await this._chatCompletionService.GetChatMessageContentAsync(chatHistory, settings, this._kernel);

// 또는 AI 커넥터 구성 수준에서
IKernelBuilder builder = Kernel.CreateBuilder();
builder.AddOpenAIChatCompletion("<model-id>", "<api-key>", functionNamePolicy: FunctionNamePolicy.UseFunctionNameAsFqn);

// 또는 플러그인 수준에서
string pluginName = string.Empty;

// 플러그인 이름이 빈 문자열이 아니면, 플러그인 이름으로 사용됩니다.
// null이면, 플러그인 타입에서 플러그인 이름이 추론됩니다.
// 빈 문자열이면, 플러그인 이름이 생략되고,
// 모든 함수가 플러그인 이름 없이 알려집니다.
kernel.ImportPluginFromType<Bar>(pluginName);
```


### 옵션 2: 사용자 정의 구분자

이 옵션은 구분자 문자 또는 문자 시퀀스를 설정 가능하게 만드는 것을 제안합니다. 개발자는 AI 모델이 실수로 생성할 가능성이 적은 구분자를 지정할 수 있습니다. 예를 들어, `_` 또는 `a1b`를 구분자로 선택할 수 있습니다.

이 솔루션은 함수 이름 환각 발생을 줄일 수 있습니다(이슈 #1 및 #2).

장점:
- 구분자를 환각 가능성이 낮은 문자로 변경하여 함수 이름 환각을 줄입니다.

단점:
- 구분자가 플러그인 이름에 사용되는 경우에는 작동하지 않습니다. 예를 들어, 밑줄 기호가 `my_plugin` 플러그인 이름의 일부이면서 구분자로도 사용되면, `my_plugin_myfunction` FQN이 됩니다.
    - [ADR 검토 회의에서] SK는 알리기 전에 플러그인 이름과 함수 이름에서 구분자의 모든 출현을 동적으로 제거할 수 있습니다.
- 환각된 함수 이름을 처리할 수 없습니다. 예를 들어, AI 모델이 `MyPlugin_my_function` 대신 함수 FQN을 `MyPlugin_my_func`로 생성하는 경우.

가능한 구현:
```csharp
// 작업 수준에서
FunctionChoiceBehaviorOptions options = new new()
{
    FqnSeparator = "_"
};

var settings = new AzureOpenAIPromptExecutionSettings() { FunctionChoiceBehavior = FunctionChoiceBehavior.Auto(options) };

var result = await this._chatCompletionService.GetChatMessageContentAsync(chatHistory, settings, this._kernel);

// 또는 AI 커넥터 구성 수준에서
IKernelBuilder builder = Kernel.CreateBuilder();
builder.AddOpenAIChatCompletion("<model-id>", "<api-key>", functionNamePolicy: FunctionNamePolicy.Custom("_"));
```

### 옵션 3: 구분자 없음

이 옵션은 플러그인 이름과 함수 이름 사이에 구분자를 사용하지 않는 것을 제안합니다. 대신 직접 연결됩니다.
예를 들어, 플러그인 `foo`의 함수 `bar`의 FQN은 `foobar`가 됩니다.

장점:
- 환각의 원인(구분자)을 제거하여 함수 이름 환각을 줄입니다(이슈 #1 및 #2).

단점:
- 다른 함수 조회 휴리스틱이 필요합니다.

### 옵션 4: 사용자 정의 FQN 파서

이 옵션은 함수 FQN을 플러그인 이름과 함수 이름으로 분리할 수 있는 사용자 정의 외부 FQN 파서를 제안합니다. 파서는 AI 모델이 호출한 함수 FQN을 받아 플러그인 이름과 함수 이름을 모두 반환합니다. 이를 위해, 파서는 다양한 구분자 문자를 사용하여 FQN을 파싱하려고 시도합니다:
```csharp
static (string? PluginName, string FunctionName) ParseFunctionFqn(ParseFunctionFqnContext context)
{
    static (string? PluginName, string FunctionName)? Parse(ParseFunctionFqnContext context, char separator)
    {
        string? pluginName = null;
        string functionName = context.FunctionFqn;

        int separatorPos = context.FunctionFqn.IndexOf(separator, StringComparison.Ordinal);
        if (separatorPos >= 0)
        {
            pluginName = context.FunctionFqn.AsSpan(0, separatorPos).Trim().ToString();
            functionName = context.FunctionFqn.AsSpan(separatorPos + 1).Trim().ToString();
        }

        // 함수가 커널에 등록되어 있는지 확인
        if (context.Kernel is { } kernel && kernel.Plugins.TryGetFunction(pluginName, functionName, out _))
        {
            return (pluginName, functionName);
        }

        return null;
    }

    // 하이픈, 점, 밑줄을 순차적으로 구분자로 사용해 봅니다.
    var result = Parse(context, '-') ??
                    Parse(context, '.') ??
                    Parse(context, '_');

    if (result is not null)
    {
        return result.Value;
    }

    // 구분자를 찾지 못하면, AI 커넥터가 기본 동작을 적용할 수 있도록 함수 이름을 그대로 반환합니다.
    return (null, context.FunctionFqn);
}
```

[ADR 검토 회의에서] 대안으로, 파서가 함수 자체를 반환할 수 있습니다. 이는 추가 조사가 필요합니다.
이 [PR](https://github.com/microsoft/semantic-kernel/pull/10206)은 파서가 어디서 어떻게 사용되는지에 대한 더 많은 통찰을 제공할 수 있습니다.

장점:
- AI 모델에 특화된 사용자 정의 휴리스틱을 적용하여 함수 구분자 환각을 완화합니다(줄이거나 완전히 제거하지는 않음).
- SK AI 커넥터에서 쉽게 구현할 수 있습니다.


가능한 구현:
```csharp
// 작업 수준에서
static (string? PluginName, string FunctionName) ParseFunctionFqn(ParseFunctionFqnContext context)
{
    ...
}

FunctionChoiceBehaviorOptions options = new new()
{
    FqnParser = ParseFunctionFqn
};

var settings = new AzureOpenAIPromptExecutionSettings() { FunctionChoiceBehavior = FunctionChoiceBehavior.Auto(options) };

var result = await this._chatCompletionService.GetChatMessageContentAsync(chatHistory, settings, this._kernel);

// 또는 AI 커넥터 구성 수준에서
IKernelBuilder builder = Kernel.CreateBuilder();
builder.AddOpenAIChatCompletion("<model-id>", "<api-key>", functionNamePolicy: FunctionNamePolicy.Custom("_", ParseFunctionFqn));
```

### 옵션 5: 개선된 자동 복구 메커니즘

현재 알려지지 않은 함수가 호출되면, SK는 오류 메시지를 반환합니다: _"Error: Function call request for a function that wasn't defined."_
`gpt-4(0613)`, `gpt-4o-mini(2024-07-18)`, `gpt-4o(2024-08-06)` 세 개의 AI 모델 중 `gpt-4o-mini`만이 이 오류에서 자동으로 복구하여 올바른 이름으로 함수를 성공적으로 호출할 수 있습니다.
나머지 두 모델은 복구에 실패하고 다음과 유사한 최종 메시지를 반환합니다: _"I'm sorry, but I can't provide the answer right now due to a system error."_

그러나 오류 메시지에 함수 이름을 추가하고 - "Error: Function call request for **foo.bar** function that wasn't defined." 그리고
채팅 히스토리에 "You can call tools. If a tool call failed, correct yourself." 시스템 메시지를 추가하면, 세 모델 모두 오류에서 자동 복구하여 올바른 이름으로 함수를 호출할 수 있습니다.

이를 고려하여, 오류 메시지에 함수 이름을 추가하고 자동 복구 메커니즘을 개선하기 위해 시스템 메시지를 추가하는 것을 권장할 수 있습니다.

장점:
- 더 많은 모델이 오류에서 자동 복구할 수 있습니다.

단점:
- 자동 복구 메커니즘이 모든 AI 모델에서 작동하지 않을 수 있습니다.

가능한 구현:
```csharp
// 호출자 코드
 var chatHistory = new ChatHistory();
 chatHistory.AddSystemMessage("You can call tools. If a tool call failed, correct yourself.");
 chatHistory.AddUserMessage("<prompt>");


// 함수 호출 프로세서에서
if (!checkIfFunctionAdvertised(functionCall))
{
    // errorMessage = "Error: Function call request for a function that wasn't defined.";
    errorMessage = $"Error: Function call request for the function that wasn't defined - {functionCall.FunctionName}.";
    return false;
}
```
 
### 옵션 6: 함수 이름에서 허용되지 않는 문자 제거

이 옵션은 AI 모델에 오류 메시지를 반환할 때 함수 FQN에서 허용되지 않는 문자를 제거하여 이슈 2를 해결하는 것을 제안합니다.
이 변경은 AI 모델에 대한 요청이 다음 예외로 실패하는 것을 방지합니다: _"Invalid messages[3].tool_calls[0].function.name: string does not match pattern. Expected a string that matches the pattern `^[a-zA-Z0-9_-]+$`"_.

장점:
- AI 모델이 오류에서 자동 복구하는 것을 방해하는 이슈 2를 제거합니다.


가능한 구현:
```csharp
// AI 커넥터에서

var fqn = FunctionName.ToFullyQualifiedName(callRequest.FunctionName, callRequest.PluginName, OpenAIFunction.NameSeparator);

// 허용되지 않는 모든 문자를 밑줄로 대체합니다.
fqn = Regex.Replace(fqn, "[^a-zA-Z0-9_-]", "_");

toolCalls.Add(ChatToolCall.CreateFunctionToolCall(callRequest.Id, fqn, BinaryData.FromString(argument ?? string.Empty)));
```

## 결정 결과
공개 API 표면에 변경이 필요하지 않은 옵션 - 옵션 5와 6부터 시작하고, 적용된 두 옵션의 영향을 평가한 후 필요한 경우 다른 옵션을 진행하기로 결정되었습니다.
