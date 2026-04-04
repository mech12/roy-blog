---
# 이 항목들은 선택 사항입니다. 필요 없는 항목은 자유롭게 삭제하세요.
status: accepted
date: 2023-10-27
contact: SergeyMenshykh
deciders: markwallace, mabolan
consulted:
informed:
---
# 프롬프트 구문의 완성 서비스 모델 매핑

## 맥락 및 문제 설명
현재 SK는 렌더링된 프롬프트를 수정 없이 그대로 구성된 텍스트 완성 서비스/커넥터에 전달하여 모든 프롬프트를 텍스트 완성 서비스로 실행합니다. 새로운 채팅 완성 프롬프트와 이미지 등 잠재적으로 다른 프롬프트 유형의 추가가 예정되어 있어, 완성별 프롬프트 구문을 해당 완성 서비스 데이터 모델에 매핑하는 방법이 필요합니다.

예를 들어, 채팅 완성 프롬프트의 [채팅 완성 구문](https://github.com/microsoft/semantic-kernel/blob/main/docs/decisions/0014-chat-completion-roles-in-prompt.md):
```xml
<message role="system">
    You are a creative assistant helping individuals and businesses with their innovative projects.
</message>
<message role="user">
    I want to brainstorm the idea of {{$input}}
</message>
```
은 두 개의 채팅 메시지를 가진 [ChatHistory](https://github.com/microsoft/semantic-kernel/blob/main/dotnet/src/SemanticKernel.Abstractions/AI/ChatCompletion/ChatHistory.cs) 클래스의 인스턴스로 매핑되어야 합니다:

```csharp
var messages = new ChatHistory();
messages.Add(new ChatMessage(new AuthorRole("system"), "You are a creative assistant helping individuals and businesses with their innovative projects."));
messages.Add(new ChatMessage(new AuthorRole("user"), "I want to brainstorm the idea of {{$input}}"));
```

이 ADR은 프롬프트 구문 매핑 기능의 위치에 대한 잠재적 옵션을 설명합니다.

## 검토한 옵션
**1. 완성 커넥터 클래스.** 이 옵션은 완성 커넥터 클래스가 `프롬프트 구문 -> 완성 서비스 데이터 모델` 매핑을 담당하도록 제안합니다. 이 매핑 기능이 커넥터 클래스 자체에서 구현될지 매퍼 클래스에 위임될지는 구현 단계에서 결정해야 하며 이 ADR의 범위 밖입니다.

장점:
 - 새로운 완성 유형 커넥터(오디오, 비디오 등)가 추가될 때 `SemanticFunction`을 새로운 프롬프트 구문 매핑 지원을 위해 변경할 필요가 없습니다.

 - 프롬프트를 다음으로 실행할 수 있습니다
    - Kernel.RunAsync
    - 완성 커넥터

단점:
 - 기존 유형이든 새로운 유형이든 모든 새 완성 커넥터가 매핑 기능을 구현해야 합니다

**2. SemanticFunction 클래스.** 이 옵션은 `SemanticFunction` 클래스가 매핑을 담당하도록 제안합니다. 이전 옵션과 마찬가지로 이 기능의 정확한 위치(`SemanticFunction` 클래스인지 매퍼 클래스인지)는 구현 단계에서 결정해야 합니다.

장점:
 - 새로운 유형이든 기존 유형이든 새 커넥터가 매핑 기능을 구현할 필요가 없습니다

단점:
 - SK가 새로운 완성 유형을 지원해야 할 때마다 `SemanticFunction` 클래스를 변경해야 합니다
 - 프롬프트는 Kernel.RunAsync 메서드로만 실행할 수 있습니다.

## 결정 결과
옵션 1 - `1. 완성 커넥터 클래스`로 진행하기로 합의했습니다. 이는 더 유연한 솔루션이며 `SemanticFunction` 클래스를 수정하지 않고 새 커넥터를 추가할 수 있기 때문입니다.
