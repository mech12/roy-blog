---
# 이것들은 선택적 요소입니다. 필요 없는 항목은 자유롭게 제거하세요.
status: accepted
contact: westey-m
date: 2025-04-17
deciders: westey-m, markwallace-microsoft, alliscode, TaoChenOSU, moonbox3, crickman
consulted: westey-m, markwallace-microsoft, alliscode, TaoChenOSU, moonbox3, crickman
informed: westey-m, markwallace-microsoft, alliscode, TaoChenOSU, moonbox3, crickman
---

# 메모리를 가진 에이전트

## 메모리란 무엇을 의미하는가?

메모리란 대화 중에 학습된 정보와 기술을 기억하고
같은 대화 또는 이후의 대화에서 이를 재사용할 수 있는 능력을 의미합니다.

## 맥락과 문제 설명

현재 우리는 다양한 특성을 가진 여러 에이전트 타입을 지원합니다:

1. 인프로세스 vs 원격.
2. 서비스에서 대화 상태를 저장하고 유지하는 원격 에이전트 vs 각 호출 시 호출자가 대화 상태를 제공해야 하는 에이전트.

이 범위의 에이전트 타입 전반에 걸쳐 고급 메모리 기능을 지원해야 합니다.

### 메모리 범위

고려해야 할 메모리의 또 다른 측면은 다양한 메모리 타입의 범위입니다.
대부분의 에이전트 구현에는 지시사항과 기술이 있지만, 에이전트는 단일 대화에 묶여 있지 않습니다.
에이전트가 호출될 때마다 해당 호출 동안 참여할 대화가 지정됩니다.

사용자에 대한 또는 사용자와의 대화에 대한 메모리는 이러한 대화 중 하나에서 추출되어
같은 사용자와의 동일한 또는 다른 대화에서 회상됩니다.
이러한 메모리에는 일반적으로 사용자가 시스템의 다른 사용자와 공유하고 싶지 않은 정보가 포함됩니다.

특정 사용자나 대화에 묶여 있지 않은 다른 유형의 메모리도 존재합니다.
예를 들어, 에이전트는 무언가를 수행하는 방법을 학습하여 다양한 사용자와의 많은 대화에서 이를 수행할 수 있습니다.
이러한 유형의 메모리에서는 물론 다른 사용자 간에 개인 정보가 유출되는 위험이 있으므로 이를 방지하는 것이 중요합니다.

### 메모리 기능 패키징

위의 모든 메모리 타입은 대화 스레드에 소프트웨어 컴포넌트를 연결하여 모든 에이전트에 대해 지원할 수 있습니다.
이는 다음의 간단한 메커니즘으로 달성됩니다:

1. 에이전트에 전달되는 메시지와 에이전트로부터의 메시지를 검사하고 사용합니다.
2. 호출별로 에이전트에 추가 컨텍스트를 전달합니다.

현재 `AgentThread` 구현에서, 에이전트가 호출되면 모든 입력 및 출력 메시지가 이미 `AgentThread`에 전달되며
`AgentThread`에 연결된 모든 컴포넌트에서 사용할 수 있습니다.
에이전트가 원격/외부이고 서비스에서 대화 상태를 관리하는 경우, 메시지를 `AgentThread`에 전달하는 것이 서비스의 스레드에 어떤 영향도 미치지 않을 수 있습니다. 서비스가 원격 호출 중에 이미 스레드를 업데이트했을 것이기 때문입니다.
그러나 연결된 컴포넌트에서 메시지를 구독할 수 있게 합니다.

호출별 추가 컨텍스트를 얻기 위한 두 번째 요구사항의 경우, 에이전트가 전달받은 스레드에 요청하여 연결된 각 컴포넌트에 에이전트에 전달할 컨텍스트를 제공하도록 요청할 수 있습니다.
이를 통해 컴포넌트는 필요에 따라 포함하고 있는 메모리를 에이전트에 제공할 수 있습니다.

다양한 메모리 기능은 별도의 컴포넌트를 사용하여 구축할 수 있습니다. 각 컴포넌트는 다음과 같은 특성을 가집니다:

1. 호출별로 에이전트에 제공할 수 있는 일부 컨텍스트를 저장할 수 있습니다.
2. 대화에서 학습하고 컨텍스트를 구축하기 위해 대화의 메시지를 검사할 수 있습니다.
3. 에이전트가 메모리를 직접 저장, 검색, 업데이트 또는 삭제할 수 있도록 플러그인을 등록할 수 있습니다.

### 일시 중단 / 재개

에이전트를 호스팅하는 서비스를 구축하는 것은 도전적입니다.
상태 유지 서비스를 구축하기 어렵지만, 서비스 소비자는 외부에서 상태 유지처럼 보이는 경험을 기대합니다.
예를 들어, 각 호출에서 사용자는 서비스가 진행 중인 대화를 계속할 수 있기를 기대합니다.

이는 서비스가 로컬 대화 상태 관리(예: `ChatHistory`를 통한)를 사용하는 로컬 에이전트를 노출하는 경우
해당 대화 상태가 서비스의 각 호출마다 로드되고 유지되어야 함을 의미합니다.

또한 인메모리 상태를 가질 수 있는 모든 메모리 컴포넌트도 로드되고 유지되어야 함을 의미합니다.

이러한 경우, `OnSuspend` 및 `OnResume` 메서드는 컴포넌트에 상태를 저장하거나 다시 로드해야 한다는 알림을 허용합니다.
상태를 어디에 어떻게 저장하거나 로드할지는 각 컴포넌트가 결정합니다.

## 메모리 컴포넌트를 위한 제안된 인터페이스

메모리 컴포넌트가 필요로 하는 이벤트 유형은 메모리에 고유하지 않으며, 다른 기능을 패키징하는 데에도 사용할 수 있습니다.
따라서 다른 시나리오에서도 사용할 수 있고 에이전트가 아닌 시나리오에서도 사용할 수 있는 보다 일반적으로 이름 지어진 타입을 만드는 것이 제안됩니다.

이 타입은 에이전트뿐만 아니라 다른 시스템에서도 사용할 수 있으므로 `Microsoft.SemanticKernel.Abstractions` nuget에 있어야 합니다.

```csharp
namespace Microsoft.SemanticKernel;

public abstract class AIContextBehavior
{
    public virtual IReadOnlyCollection<AIFunction> AIFunctions => Array.Empty<AIFunction>();

    public virtual Task OnThreadCreatedAsync(string? threadId, CancellationToken cancellationToken = default);
    public virtual Task OnThreadDeleteAsync(string? threadId, CancellationToken cancellationToken = default);

    // OnThreadCheckpointAsync는 초기 릴리스에 포함되지 않으며, 향후 포함될 수 있습니다.
    public virtual Task OnThreadCheckpointAsync(string? threadId, CancellationToken cancellationToken = default);

    public virtual Task OnNewMessageAsync(string? threadId, ChatMessage newMessage, CancellationToken cancellationToken = default);
    public abstract Task<string> OnModelInvokeAsync(ICollection<ChatMessage> newMessages, CancellationToken cancellationToken = default);

    public virtual Task OnSuspendAsync(string? threadId, CancellationToken cancellationToken = default);
    public virtual Task OnResumeAsync(string? threadId, CancellationToken cancellationToken = default);
}
```

## 여러 컴포넌트 관리

여러 컴포넌트를 관리하기 위해 `AIContextBehavior`를 제안합니다.
이 클래스는 컴포넌트를 등록하고 새 메시지 알림, AI 호출 등을 포함된 컴포넌트에 위임할 수 있게 합니다.

## 에이전트와의 통합

`AgentThread` 클래스에 `AIContextBehaviorManager`를 추가하여 모든 `AgentThread`에 컴포넌트를 연결할 수 있도록 제안합니다.

`Agent`가 호출되면, `AIContextBehaviorManager`를 통해 각 컴포넌트에서 `OnModelInvokeAsync`를 호출하여
이 호출에 대해 에이전트에 전달할 결합된 컨텍스트 세트를 얻습니다. 이는 `Agent` 클래스 내부에서 이루어지며 사용자에게 투명합니다.

```csharp
var additionalInstructions = await currentAgentThread.OnModelInvokeAsync(messages, cancellationToken).ConfigureAwait(false);
```

## 사용 예시

### 동일한 메모리 컴포넌트를 사용하는 여러 스레드

```csharp
// 메모리를 저장하기 위한 벡터 저장소를 생성합니다.
var vectorStore = new InMemoryVectorStore();
// 벡터 저장소의 "Memories" 컬렉션에 연결되고 "user/12345" 네임스페이스 아래에 메모리를 저장하는 메모리 저장소를 생성합니다.
using var textMemoryStore = new VectorDataTextMemoryStore<string>(vectorStore, textEmbeddingService, "Memories", "user/12345", 1536);

// 대화에서 사용자 사실을 추출하여 벡터 저장소에 저장하고
// 추가 지시사항으로 에이전트에 전달하는 메모리 컴포넌트를 생성합니다.
var userFacts = new UserFactsMemoryComponent(this.Fixture.Agent.Kernel, textMemoryStore);

// 스레드를 생성하고 메모리 컴포넌트를 연결합니다.
var agentThread1 = new ChatHistoryAgentThread();
agentThread1.ThreadExtensionsManager.Add(userFacts);
var asyncResults1 = agent.InvokeAsync("Hello, my name is Caoimhe.", agentThread1);

// 두 번째 스레드를 생성하고 메모리 컴포넌트를 연결합니다.
var agentThread2 = new ChatHistoryAgentThread();
agentThread2.ThreadExtensionsManager.Add(userFacts);
var asyncResults2 = agent.InvokeAsync("What is my name?.", agentThread2);
// 예상 응답에 Caoimhe가 포함됩니다.
```

### RAG 컴포넌트 사용

```csharp
// 벡터 저장소와 RAG 저장소/컴포넌트 생성
var vectorStore = new InMemoryVectorStore();
using var ragStore = new TextRagStore<string>(vectorStore, textEmbeddingService, "Memories", 1536, "group/g2");
var ragComponent = new TextRagComponent(ragStore, new TextRagComponentOptions());

// 벡터 저장소에 문서 업서트.
await ragStore.UpsertDocumentsAsync(
[
    new TextRagDocument("The financial results of Contoso Corp for 2023 is as follows:\nIncome EUR 174 000 000\nExpenses EUR 152 000 000")
    {
        SourceName = "Contoso 2023 Financial Report",
        SourceReference = "https://www.consoso.com/reports/2023.pdf",
        Namespaces = ["group/g2"]
    }
]);
    
// 새 에이전트 스레드를 생성하고 RAG 컴포넌트를 등록합니다
var agentThread = new ChatHistoryAgentThread();
agentThread.ThreadExtensionsManager.RegisterThreadExtension(ragComponent);

// 에이전트를 호출합니다.
var asyncResults1 = agent.InvokeAsync("What was the income of Contoso for 2023", agentThread);
// 예상 응답에 문서에서 가져온 1억 7,400만 수입이 포함됩니다.
```

## 결정할 사항

### 확장 기본 클래스 이름

1. ConversationStateExtension

    1.1. 너무 길음

2. MemoryComponent

    2.1. 너무 구체적임

3. AIContextBehavior

결정: 3. AIContextBehavior.

### 추상화 위치

1. Microsoft.SemanticKernel.<baseclass>
2. Microsoft.SemanticKernel.Memory.<baseclass>
3. Microsoft.SemanticKernel.Memory.<baseclass> (별도 nuget에)

결정: 1. Microsoft.SemanticKernel.<baseclass>.

### 메모리 컴포넌트 위치

1. 각 컴포넌트마다 nuget
2. Microsoft.SemanticKernel.Core nuget
3. Microsoft.SemanticKernel.Memory nuget
4. Microsoft.SemanticKernel.ConversationStateExtensions nuget

결정: 2. Microsoft.SemanticKernel.Core nuget
