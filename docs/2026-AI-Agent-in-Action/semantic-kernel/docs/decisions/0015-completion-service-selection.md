---
# 이 항목들은 선택 사항입니다. 필요 없는 항목은 자유롭게 삭제하세요.
status: superseded by [ADR-0038](0038-completion-service-selection.md)
contact: SergeyMenshykh
date: 2023-10-25
deciders: markwallace-microsoft, matthewbolanos
consulted:
informed:
---

# 완성 서비스 유형 선택 전략

## 맥락 및 문제 설명

현재 SK는 모든 텍스트 프롬프트를 텍스트 완성 서비스를 사용하여 실행합니다. 새로운 채팅 완성 프롬프트와 이미지 등 잠재적으로 다른 프롬프트 유형의 추가가 예정되어 있어, 이러한 프롬프트를 실행할 완성 서비스 유형을 선택하는 방법이 필요합니다.

<!-- 이 항목은 선택 사항입니다. 필요 없으면 삭제하세요. -->

## 결정 요인

- 시맨틱 함수는 텍스트, 채팅 또는 이미지 프롬프트를 처리할 때 사용할 완성 서비스 유형을 식별할 수 있어야 합니다.

## 검토한 옵션

**1. "prompt_type" 속성으로 완성 서비스 유형을 식별합니다.** 이 옵션은 프롬프트 템플릿 설정 모델 클래스인 `PromptTemplateConfig`에 'prompt_type' 속성을 추가하는 것을 전제로 합니다. 이 속성은 프롬프트 개발자가 한 번 지정하며, `SemanticFunction` 클래스가 해당 특정 완성 서비스 유형의 인스턴스를 해석할 때 어떤 완성 서비스 유형(인스턴스가 아님)을 사용할지 결정하는 데 사용됩니다.

**프롬프트 템플릿**

```json
{
    "schema": "1",
    "description": "Hello AI, what can you do for me?",
    "prompt_type": "<text|chat|image>",
    "models": [...]
}
```

**시맨틱 함수 의사 코드**

```csharp
if(string.IsNullOrEmpty(promptTemplateConfig.PromptType) || promptTemplateConfig.PromptType == "text")
{
    var service = this._serviceSelector.SelectAIService<ITextCompletion>(context.ServiceProvider, this._modelSettings);
    //프롬프트를 렌더링하고, 서비스를 호출하고, 결과를 처리하여 반환
}
else (promptTemplateConfig.PromptType == "chat")
{
    var service = this._serviceSelector.SelectAIService<IChatCompletion>(context.ServiceProvider, this._modelSettings);
    //프롬프트를 렌더링하고, 서비스를 호출하고, 결과를 처리하여 반환
},
else (promptTemplateConfig.PromptType == "image")
{
    var service = this._serviceSelector.SelectAIService<IImageGeneration>(context.ServiceProvider, this._modelSettings);
    //프롬프트를 렌더링하고, 서비스를 호출하고, 결과를 처리하여 반환
}
```

**예시**

```json
name: ComicStrip.Create
prompt: "Generate ideas for a comic strip based on {{$input}}. Design characters, develop the plot, ..."
config: {
	"schema": 1,
	"prompt_type": "text",
	...
}

name: ComicStrip.Draw
prompt: "Draw the comic strip - {{$comicStrip.Create $input}}"
config: {
	"schema": 1,
	"prompt_type": "image",
	...
}
```

장점:

- 어떤 완성 서비스 **유형**을 사용할지 결정적으로 지정하므로, 이미지 프롬프트가 텍스트 완성 서비스에서 렌더링되거나 그 반대가 되는 일이 없습니다.

단점:

- 프롬프트 개발자가 지정해야 할 속성이 하나 더 추가됩니다.

**2. 프롬프트 내용으로 완성 서비스 유형을 식별합니다.** 이 옵션의 아이디어는 렌더링된 프롬프트를 분석하여 정규식으로 프롬프트 유형과 관련된 특정 마커의 존재 여부를 확인하는 것입니다. 예를 들어, 렌더링된 프롬프트에 `<message role="*"></message>` 태그가 있으면 해당 프롬프트가 채팅 프롬프트이며 채팅 완성 서비스에서 처리해야 함을 나타낼 수 있습니다. 이 접근 방식은 텍스트와 채팅 두 가지 완성 서비스 유형만 있을 때는 안정적으로 작동할 수 있습니다. 로직이 간단하기 때문입니다: 렌더링된 프롬프트에서 메시지 태그가 발견되면 채팅 완성 서비스로 처리하고, 그렇지 않으면 텍스트 완성 서비스를 사용합니다. 그러나 새로운 프롬프트 유형을 추가하기 시작하면 이 로직은 신뢰할 수 없게 되며, 해당 프롬프트에 프롬프트 유형을 식별하는 특정 마커가 없는 경우 더욱 그렇습니다. 예를 들어, 이미지 프롬프트를 추가하면 이미지 프롬프트에 해당 유형을 식별하는 고유 마커가 없는 한 텍스트 프롬프트와 이미지 프롬프트를 구별할 수 없습니다.

```csharp
if (Regex.IsMatch(renderedPrompt, @"<message>.*?</message>"))
{
    var service = this._serviceSelector.SelectAIService<IChatCompletion>(context.ServiceProvider, this._modelSettings);
    //프롬프트를 렌더링하고, 서비스를 호출하고, 결과를 처리하여 반환
},
else
{
    var service = this._serviceSelector.SelectAIService<ITextCompletion>(context.ServiceProvider, this._modelSettings);
    //프롬프트를 렌더링하고, 서비스를 호출하고, 결과를 처리하여 반환
}
```

**예시**

```json
name: ComicStrip.Create
prompt: "Generate ideas for a comic strip based on {{$input}}. Design characters, develop the plot, ..."
config: {
	"schema": 1,
	...
}

name: ComicStrip.Draw
prompt: "Draw the comic strip - {{$comicStrip.Create $input}}"
config: {
	"schema": 1,
	...
}
```

장점:

- 프롬프트 유형을 식별하기 위한 새로운 속성이 필요하지 않습니다.

단점:

- 프롬프트에 프롬프트 유형을 구체적으로 식별하는 고유 마커가 포함되어 있지 않으면 신뢰할 수 없습니다.

## 결정 결과

'2. 프롬프트 내용으로 완성 서비스 유형을 식별' 옵션을 선택하기로 결정했으며, 이 옵션으로 지원할 수 없는 다른 완성 서비스 유형이 등장하거나 완성 서비스 유형을 선택하기 위한 다른 메커니즘 사용에 대한 확실한 요구 사항이 있을 때 재검토할 것입니다.
