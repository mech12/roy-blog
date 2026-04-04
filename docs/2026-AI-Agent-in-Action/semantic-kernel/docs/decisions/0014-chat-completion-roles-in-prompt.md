---
# 이 항목들은 선택 사항입니다. 필요 없는 항목은 자유롭게 삭제하세요.
status: accepted
contact: SergeyMenshykh
date: 2023-10-23
deciders: markwallace-microsoft, matthewbolanos
consulted:
informed:
---

# 채팅 완성 역할을 위한 SK 프롬프트 구문

## 맥락 및 문제 설명

현재 SK는 프롬프트 내 텍스트 블록을 assistant, system, user와 같은 특정 역할을 가진 메시지로 표시하는 기능이 없습니다. 이로 인해 SK는 프롬프트를 채팅 완성 커넥터가 요구하는 메시지 목록으로 분할할 수 없습니다.

또한, 프롬프트는 Handlebars, Jinja 등 다양한 템플릿 엔진이 지원하는 범위의 템플릿 구문으로 정의할 수 있습니다. 이러한 각 구문은 채팅 메시지나 역할을 고유한 방식으로 표현할 수 있습니다. 따라서 적절한 추상화가 마련되지 않으면 템플릿 엔진 구문이 SK 도메인으로 누출되어, SK가 템플릿 엔진과 결합되고 새로운 엔진을 지원하는 것이 불가능해질 수 있습니다.

<!-- 이 항목은 선택 사항입니다. 필요 없으면 삭제하세요. -->

## 결정 요인

- 프롬프트 내 텍스트 블록을 역할이 있는 메시지로 표시하여, 채팅 완성 커넥터에서 사용할 채팅 메시지 목록으로 변환할 수 있어야 합니다.
- 템플릿 엔진 메시지/역할에 특화된 구문은 SK 메시지/역할 구문으로 매핑되어, SK를 특정 템플릿 엔진 구문으로부터 추상화해야 합니다.

## 검토한 옵션

**1. 메시지/역할 태그가 프롬프트에 명시된 함수에 의해 생성됩니다.** 이 옵션은 많은 템플릿 엔진이 템플릿에 명시된 함수를 호출할 수 있다는 사실에 기반합니다. 따라서 내부 함수를 템플릿 엔진에 등록하면, 해당 함수가 제공된 인수를 기반으로 메시지/모델 태그를 생성합니다. 프롬프트 템플릿 엔진이 함수를 실행하고 결과를 프롬프트 템플릿에 출력하면, 렌더링된 프롬프트에 각 메시지/역할에 대한 섹션이 이 태그들로 장식됩니다. 다음은 SK 기본 템플릿 엔진과 Handlebars를 사용하여 이를 수행하는 예시입니다:

함수:

```csharp
internal class SystemFunctions
{
    public string Message(string role)
    {
        return $"<message role=\"{role}\">";
    }
}
```

프롬프트:

```bash
{{message role="system"}}
You are a bank manager. Be helpful, respectful, appreciate diverse language styles.
{{message role="system"}}

{{message role="user"}}
I want to {{$input}}
{{message role="user"}}
```

렌더링된 프롬프트:

```xml
<message role="system">
You are a bank manager. Be helpful, respectful, appreciate diverse language styles.
</message>
<message role="user">
I want to buy a house.
</message>
```

**2. 메시지/역할 태그가 프롬프트별 메커니즘에 의해 생성됩니다.** 이 옵션은 함수 외의 템플릿 엔진 구문 구조, 헬퍼, 핸들러를 활용하여 최종 프롬프트에 SK 메시지/역할 태그를 주입합니다.
아래 예시에서 handlebars 구문을 사용하는 프롬프트를 파싱하려면 블록 헬퍼(Handlebars 엔진이 이를 만나면 호출되는 콜백)를 등록하여 결과 프롬프트에 SK 메시지/역할 태그를 출력해야 합니다.

블록 헬퍼:

```csharp
this.handlebarsEngine.RegisterHelper("system", (EncodedTextWriter output, Context context, Arguments arguments) => {
  //<message role="system"> 태그 출력
});
this.handlebarsEngine.RegisterHelper("user", (EncodedTextWriter output, Context context, Arguments arguments) => {
  //<message role="user"> 태그 출력
});
```

프롬프트:

```bash
{{#system~}}
You are a bank manager. Be helpful, respectful, appreciate diverse language styles.
{{~/system}}
{{#user~}}
I want to {{$input}}
{{~/user}}
```

렌더링된 프롬프트:

```xml
<message role="system">
You are a bank manager. Be helpful, respectful, appreciate diverse language styles.
</message>
<message role="user">
I want to buy a house.
</message>
```

**3. 메시지/역할 태그가 프롬프트 템플릿 엔진 위에 적용됩니다.** 이 옵션은 프롬프트에 SK 메시지/역할 태그를 직접 지정하여, 템플릿 엔진이 이를 파싱/처리하지 않고 일반 텍스트로 간주하는 방식으로 메시지/역할 블록을 표시하는 것을 전제로 합니다.
아래 예시에서 `<message role="*">` 태그는 system과 user 메시지의 경계를 표시하며, SK 기본 템플릿 엔진은 이를 처리 없이 일반 텍스트로 간주합니다.

프롬프트:

```xml
<message role="system">
You are a bank manager. Be helpful, respectful, appreciate diverse language styles.
</message>
<message role="user">
I want to {{$input}}
</message>
```

렌더링된 프롬프트:

```xml
<message role="system">
You are a bank manager. Be helpful, respectful, appreciate diverse language styles.
</message>
<message role="user">
I want to buy a house.
</message>
```

## 장단점

**1. 메시지/역할 태그가 프롬프트에 명시된 함수에 의해 생성**

장점:

- 함수를 한 번 정의하면 함수 호출을 지원하는 프롬프트 템플릿에서 재사용할 수 있습니다.

단점:

- 일부 템플릿 엔진에서 함수가 지원되지 않을 수 있습니다.
- 사용자가 직접 가져올 필요 없도록 시스템/내부 함수가 SK에 의해 사전 등록되어야 합니다.
- 각 프롬프트 템플릿 엔진은 시스템/내부 함수를 검색하고 호출하는 방법을 갖추어야 합니다.

**2. 메시지/역할 태그가 프롬프트별 메커니즘에 의해 생성**

장점:

- 해당 특정 엔진의 다른 구문 구조와 조화를 이루는 최적의 템플릿 엔진 구문 구조로 메시지/역할을 표현할 수 있습니다.

단점:

- 각 프롬프트 템플릿 엔진이 SK 메시지/역할 태그를 출력하기 위해 템플릿 구문 구조 렌더링을 처리하는 콜백/핸들러를 등록해야 합니다.

**3. 메시지/역할 태그가 프롬프트 템플릿 엔진 위에 적용**

장점:

- 프롬프트 템플릿 엔진에 변경이 필요하지 않습니다.

단점:

- 메시지/역할 태그 구문이 해당 템플릿 엔진의 다른 구문 구조와 조화를 이루지 못할 수 있습니다.
- 메시지/역할 태그의 구문 오류가 프롬프트 템플릿 엔진이 아닌 프롬프트를 파싱하는 컴포넌트에서 감지됩니다.

## 결정 결과

하나의 가능한 옵션으로만 제한하지 않기로 합의했습니다. 이는 해당 옵션이 향후 지원해야 할 새로운 템플릿 엔진에 적용 불가능할 수 있기 때문입니다. 대신, 새로운 템플릿 엔진이 추가될 때마다 모든 옵션을 검토하고 해당 특정 템플릿 엔진에 최적인 옵션을 선택해야 합니다.

또한, 현재 `BasicPromptTemplateEngine` 엔진을 사용하는 SK에서 메시지/역할 프롬프트 구문을 지원하기 위해 "3. 메시지/역할 태그가 프롬프트 템플릿 엔진 위에 적용" 옵션으로 진행하기로 합의했습니다.
