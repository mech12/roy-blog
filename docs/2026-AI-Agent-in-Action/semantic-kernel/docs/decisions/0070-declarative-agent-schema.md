---
# 이것들은 선택적 요소입니다. 필요 없는 항목은 자유롭게 제거하세요.
status: proposed
contact: markwallace-microsoft
date: 2025-01-17
deciders: markwallace-microsoft, bentho, crickman
consulted: {의견을 구하는 모든 사람 목록 (일반적으로 주제 전문가); 양방향 소통 대상}
informed: {진행 상황을 지속적으로 전달받는 모든 사람 목록; 단방향 소통 대상}
---

# 선언적 에이전트 형식을 위한 스키마

## 맥락과 문제 설명

이 ADR은 Semantic Kernel Agent Framework를 사용하여 로드하고 실행할 수 있는 에이전트를 정의하는 데 사용할 수 있는 스키마를 설명합니다.

현재 Agent Framework는 에이전트를 정의하고 실행하기 위해 코드 우선 접근 방식을 사용합니다.
이 ADR에서 정의된 스키마를 사용하면 개발자가 에이전트를 선언적으로 정의하고 Semantic Kernel이 에이전트를 인스턴스화하고 실행하도록 할 수 있습니다.

다음은 우리가 할 수 있어야 하는 것을 보여주는 의사 코드입니다:

```csharp
Kernel kernel = Kernel
    .CreateBuilder()
    .AddAzureAIClientProvider(...)
    .Build();
var text =
    """
    type: azureai_agent
    name: AzureAIAgent
    description: AzureAIAgent Description
    instructions: AzureAIAgent Instructions
    model:
      id: gpt-4o-mini
    tools:
        - name: tool1
          type: code_interpreter
    """;

AzureAIAgentFactory factory = new();
var agent = await KernelAgentYaml.FromAgentYamlAsync(kernel, text, factory);
```

위의 코드는 가장 간단한 경우를 나타내며 다음과 같이 작동합니다:

1. `Kernel` 인스턴스는 AzureAI 에이전트를 생성할 때 `AzureAIClientProvider` 인스턴스와 같은 적절한 서비스를 가지고 있습니다.
2. `KernelAgentYaml.FromAgentYamlAsync`는 내장 Agent 인스턴스 중 하나를 생성합니다. 즉, `ChatCompletionAgent`, `OpenAIAssistantsAgent`, `AzureAIAgent` 중 하나입니다.
3. 새 Agent 인스턴스는 필요한 서비스와 도구로 구성된 자체 `Kernel` 인스턴스와 기본 초기 상태로 초기화됩니다.

참고: 일반 `Agent` 인스턴스만 생성하고 사용자 입력으로 Agent 인스턴스를 호출할 수 있는 메서드를 포함하도록 `Agent` 추상화를 확장하는 것을 고려하세요.

```csharp
Kernel kernel = ...
string text = EmbeddedResource.Read("MyAgent.yaml");
AgentFactory agentFactory = new AggregatorAgentFactory(
    new ChatCompletionAgentFactory(),
    new OpenAIAssistantAgentFactory(),
    new AzureAIAgentFactory());
var agent = KernelAgentYaml.FromAgentYamlAsync(kernel, text, factory);;
```

위의 예는 다양한 Agent 타입이 어떻게 지원되는지를 보여줍니다.

**참고:**

1. YAML 프론트매터가 포함된 마크다운(즉, Prompty 형식)이 사용되는 주요 직렬화 형식입니다.
2. Agent 상태 제공은 현재 Agent Framework에서 지원되지 않습니다.
3. Agent Framework가 모든 Agent를 호출할 수 있는 추상화를 정의해야 하는지 결정해야 합니다.
4. JSON도 기본 옵션으로 지원할 예정입니다.

현재 Semantic Kernel은 세 가지 Agent 타입을 지원하며 다음과 같은 속성을 가집니다:

1. [`ChatCompletionAgent`](https://learn.microsoft.com/en-us/dotnet/api/microsoft.semantickernel.agents.chatcompletionagent?view=semantic-kernel-dotnet):
   - `Arguments`: 에이전트에 대한 선택적 인수. (ChatHistoryKernelAgent에서 상속)
   - `Description`: 에이전트의 설명 (선택사항). (Agent에서 상속)
   - `HistoryReducer`: (ChatHistoryKernelAgent에서 상속)
   - `Id`: 에이전트의 식별자 (선택사항). (Agent에서 상속)
   - `Instructions`: 에이전트의 지시사항 (선택사항). (KernelAgent에서 상속)
   - `Kernel`: 에이전트 수명 전반에 걸쳐 사용되는 서비스, 플러그인, 필터를 포함하는 Kernel. (KernelAgent에서 상속)
   - `Logger`: 이 Agent와 연결된 ILogger. (Agent에서 상속)
   - `LoggerFactory`: 이 Agent를 위한 ILoggerFactory. (Agent에서 상속)
   - `Name`: 에이전트의 이름 (선택사항). (Agent에서 상속)
2. [`OpenAIAssistantAgent`](https://learn.microsoft.com/en-us/dotnet/api/microsoft.semantickernel.agents.agent.description?view=semantic-kernel-dotnet#microsoft-semantickernel-agents-agent-description):
   - `Arguments`: 에이전트에 대한 선택적 인수.
   - `Definition`: 어시스턴트 정의.
   - `Description`: 에이전트의 설명 (선택사항). (Agent에서 상속)
   - `Id`: 에이전트의 식별자 (선택사항). (Agent에서 상속)
   - `Instructions`: 에이전트의 지시사항 (선택사항). (KernelAgent에서 상속)
   - `IsDeleted`: DeleteAsync(CancellationToken)를 통해 어시스턴트가 삭제되었을 때 설정됩니다. 다른 방법으로 제거된 어시스턴트는 호출 시 예외가 발생합니다.
   - `Kernel`: 에이전트 수명 전반에 걸쳐 사용되는 서비스, 플러그인, 필터를 포함하는 Kernel. (KernelAgent에서 상속)
   - `Logger`: 이 Agent와 연결된 ILogger. (Agent에서 상속)
   - `LoggerFactory`: 이 Agent를 위한 ILoggerFactory. (Agent에서 상속)
   - `Name`: 에이전트의 이름 (선택사항). (Agent에서 상속)
   - `PollingOptions`: 폴링 동작을 정의합니다
3. [`AzureAIAgent`](https://github.com/microsoft/semantic-kernel/blob/main/dotnet/src/Agents/AzureAI/AzureAIAgent.cs)
   - `Definition`: 어시스턴트 정의.
   - `PollingOptions`: 실행 처리를 위한 폴링 동작을 정의합니다.
   - `Description`: 에이전트의 설명 (선택사항). (Agent에서 상속)
   - `Id`: 에이전트의 식별자 (선택사항). (Agent에서 상속)
   - `Instructions`: 에이전트의 지시사항 (선택사항). (KernelAgent에서 상속)
   - `IsDeleted`: DeleteAsync(CancellationToken)를 통해 어시스턴트가 삭제되었을 때 설정됩니다. 다른 방법으로 제거된 어시스턴트는 호출 시 예외가 발생합니다.
   - `Kernel`: 에이전트 수명 전반에 걸쳐 사용되는 서비스, 플러그인, 필터를 포함하는 Kernel. (KernelAgent에서 상속)
   - `Logger`: 이 Agent와 연결된 ILogger. (Agent에서 상속)
   - `LoggerFactory`: 이 Agent를 위한 ILoggerFactory. (Agent에서 상속)
   - `Name`: 에이전트의 이름 (선택사항). (Agent에서 상속)

선언적으로 정의된 에이전트를 실행할 때 일부 속성은 런타임에 의해 결정됩니다:

- `Kernel`: 런타임이 Agent가 사용할 `Kernel` 인스턴스를 생성합니다. 이 `Kernel` 인스턴스는 Agent가 필요로 하는 모델과 도구로 구성되어야 합니다.
- `Logger` 또는 `LoggerFactory`: 런타임이 올바르게 구성된 `Logger` 또는 `LoggerFactory`를 제공합니다.
- **Functions**: 런타임은 Agent가 필요로 하는 모든 함수를 해결할 수 있어야 합니다. 예를 들어, VSCode 확장은 개발자가 에이전트를 테스트할 수 있는 매우 기본적인 런타임을 제공하며 현재 프로젝트에 정의된 `KernelFunctions`를 해결할 수 있어야 합니다. 이에 대한 예시는 ADR 뒷부분에 있습니다.

동작을 정의하는 Agent 속성(예: `HistoryReducer`)에 대해 Semantic Kernel은 **반드시**:

- 선언적으로 구성할 수 있는 구현을 제공해야 합니다. 즉, 개발자가 겪을 가장 일반적인 시나리오에 대한 것입니다.
- `Kernel`에서 구현을 해결할 수 있어야 합니다. 예를 들어, 필수 서비스 또는 `KernelFunction`으로서.

## 결정 동인

- 스키마는 Agent 서비스에 비의존적이어야 합니다(**필수**). 즉, Azure, Open AI, Mistral AI 등을 대상으로 하는 에이전트에서 작동해야 합니다.
- 스키마는 에이전트에 모델 설정을 할당할 수 있어야 합니다(**필수**).
- 스키마는 에이전트에 도구(예: 함수, 코드 인터프리터, 파일 검색 등)를 할당할 수 있어야 합니다(**필수**).
- 스키마는 에이전트가 사용할 새로운 유형의 도구를 정의할 수 있어야 합니다(**필수**).
- 스키마는 Semantic Kernel 프롬프트(Prompty 형식 포함)를 사용하여 에이전트 지시사항을 정의할 수 있어야 합니다(**필수**).
- 스키마는 확장 가능해야 하며(**필수**), 자체 설정과 도구를 가진 새로운 Agent 타입에 대한 지원을 Semantic Kernel에 추가할 수 있어야 합니다.
- 스키마는 제3자가 Semantic Kernel에 새로운 Agent 타입을 기여할 수 있어야 합니다(**필수**).
- ... <!-- 동인의 수는 달라질 수 있습니다 -->

이 문서는 다음 사용 사례를 설명합니다:

1. 에이전트와 파일에 대한 메타데이터.
2. 함수 도구에 대한 접근과 동작을 안내하는 지시사항 세트를 가진 에이전트 생성.
3. 에이전트 지시사항(및 기타 속성)의 템플릿 허용.
4. 모델 구성 및 여러 모델 구성 제공.
5. 에이전트가 사용할 데이터 소스(컨텍스트/지식) 구성.
6. 에이전트가 사용할 추가 도구 구성. 예: 코드 인터프리터, OpenAPI 엔드포인트.
7. 에이전트에 대한 추가 모달리티 활성화. 예: 음성.
8. 오류 조건. 예: 모델이나 함수 도구를 사용할 수 없는 경우.

### 범위 외

- 이 ADR은 멀티 에이전트 선언적 형식이나 프로세스 선언적 형식을 다루지 않습니다.

## 검토한 옵션

- [Microsoft 365 Copilot용 선언적 에이전트 스키마 1.2](https://learn.microsoft.com/en-us/microsoft-365-copilot/extensibility/declarative-agent-manifest-1.2) 사용
- Microsoft 365 Copilot용 선언적 에이전트 스키마 1.2 확장
- [Semantic Kernel 프롬프트 스키마](https://learn.microsoft.com/en-us/semantic-kernel/concepts/prompts/yaml-schema#sample-yaml-prompt) 확장

## 옵션의 장단점

### Microsoft 365 Copilot용 선언적 에이전트 스키마 1.2 사용

Semantic Kernel은 이미 이를 지원합니다. [선언적 Agent 개념 샘플](https://github.com/microsoft/semantic-kernel/blob/main/dotnet/samples/Concepts/Agents/DeclarativeAgents.cs)을 참조하세요.

- 좋은 점, Microsoft 365 Copilot에서 채택한 기존 표준입니다.
- 중립, 스키마가 도구를 두 가지 속성으로 분리합니다. 즉, 코드 인터프리터를 포함하는 `capabilities`와 API 플러그인 매니페스트를 지정하는 `actions`.
- 나쁜 점, 다른 유형의 에이전트를 지원하지 않습니다.
- 나쁜 점, 에이전트와 연결할 AI 모델을 지정하고 구성하는 방법을 제공하지 않습니다.
- 나쁜 점, 에이전트 지시사항에 프롬프트 템플릿을 사용하는 방법을 제공하지 않습니다.
- 나쁜 점, `actions` 속성이 REST API 호출에 집중되어 있으며 네이티브 및 시맨틱 함수를 지원하지 않습니다.

### Microsoft 365 Copilot용 선언적 에이전트 스키마 1.2 확장

가능한 확장사항:

1. 프롬프트 템플릿을 사용하여 에이전트 지시사항을 생성할 수 있습니다.
2. 사용 가능한 모델에 따른 폴백을 포함하여 에이전트 모델 설정을 지정할 수 있습니다.
3. 함수의 더 나은 정의. 예: 네이티브 및 시맨틱 함수 지원.

- 좋은 점, {근거 a}
- 좋은 점, {근거 b}
- 중립, {근거 c}
- 나쁜 점, {근거 d}
- ...

### Semantic Kernel 프롬프트 스키마 확장

- 좋은 점, {근거 a}
- 좋은 점, {근거 b}
- 중립, {근거 c}
- 나쁜 점, {근거 d}
- ...

## 결정 결과

선택한 옵션: "{옵션 1의 제목}", 이유는
{정당화. 예: KO 기준 결정 동인을 충족하는 유일한 옵션 | 힘 {force}를 해결하는 옵션 | ... | 아래에서 가장 우수한 결과를 보이는 옵션}.

<!-- 이것은 선택적 요소입니다. 자유롭게 제거하세요. -->

### 결과

- 좋은 점, {긍정적 결과, 예: 하나 이상의 원하는 품질 향상, ...}
- 나쁜 점, {부정적 결과, 예: 하나 이상의 원하는 품질 저하, ...}
- ... <!-- 결과의 수는 달라질 수 있습니다 -->

<!-- 이것은 선택적 요소입니다. 자유롭게 제거하세요. -->

## 검증

{ADR의 구현/준수가 어떻게 검증되는지 설명합니다. 예: 리뷰 또는 ArchUnit 테스트로}

<!-- 이것은 선택적 요소입니다. 자유롭게 제거하세요. -->

## 추가 정보

### 코드 우선 방식 대 선언적 형식

아래는 다양한 유형의 에이전트를 생성하기 위한 코드 우선 방식과 동등한 선언적 구문을 보여주는 예시입니다.

다음 사용 사례를 고려하세요:

1. `ChatCompletionAgent`
2. 프롬프트 템플릿을 사용하는 `ChatCompletionAgent`
3. 함수 호출이 있는 `ChatCompletionAgent`
4. 함수 호출이 있는 `OpenAIAssistantAgent`
5. 도구가 있는 `OpenAIAssistantAgent`

#### `ChatCompletionAgent`

코드 우선 접근 방식:

```csharp
ChatCompletionAgent agent =
    new()
    {
        Name = "Parrot",
        Instructions = "Repeat the user message in the voice of a pirate and then end with a parrot sound.",
        Kernel = kernel,
    };
```

선언적 Semantic Kernel 스키마:

```yml
type: chat_completion_agent
name: Parrot
instructions: Repeat the user message in the voice of a pirate and then end with a parrot sound.
```

**참고**:

- `ChatCompletionAgent`가 기본 에이전트 타입이 될 수 있으므로 명시적인 `type` 속성이 필요하지 않습니다.

#### 프롬프트 템플릿을 사용하는 `ChatCompletionAgent`

코드 우선 접근 방식:

```csharp
string generateStoryYaml = EmbeddedResource.Read("GenerateStory.yaml");
PromptTemplateConfig templateConfig = KernelFunctionYaml.ToPromptTemplateConfig(generateStoryYaml);

ChatCompletionAgent agent =
    new(templateConfig, new KernelPromptTemplateFactory())
    {
        Kernel = this.CreateKernelWithChatCompletion(),
        Arguments = new KernelArguments()
        {
            { "topic", "Dog" },
            { "length", "3" },
        }
    };
```

에이전트 YAML이 다른 파일을 가리킵니다. Semantic Kernel의 선언적 에이전트 구현은 이미 별도의 지시사항 파일을 로드하는 이 기법을 사용합니다.

지시사항을 정의하는 데 사용되는 프롬프트 템플릿.
```yml
---
name: GenerateStory
description: A function that generates a story about a topic.  
template:
  format: semantic-kernel
  parser: semantic-kernel
inputs:
  - name: topic
    description: The topic of the story.
    is_required: true
    default: dog
  - name: length
    description: The number of sentences in the story.
    is_required: true
    default: 3
---
Tell a story about {{$topic}} that is {{$length}} sentences long.
```

**참고**: Semantic Kernel이 이 파일을 직접 로드할 수 있습니다.

#### 함수 호출이 있는 `ChatCompletionAgent`

코드 우선 접근 방식:

```csharp
ChatCompletionAgent agent =
    new()
    {
        Instructions = "Answer questions about the menu.",
        Name = "RestaurantHost",
        Description = "This agent answers questions about the menu.",
        Kernel = kernel,
        Arguments = new KernelArguments(new OpenAIPromptExecutionSettings() { Temperature = 0.4, FunctionChoiceBehavior = FunctionChoiceBehavior.Auto() }),
    };

KernelPlugin plugin = KernelPluginFactory.CreateFromType<MenuPlugin>();
agent.Kernel.Plugins.Add(plugin);
```

Semantic Kernel 스키마를 사용한 선언적 방식:

```yml
---
name: RestaurantHost
name: RestaurantHost
description: This agent answers questions about the menu.
model:
  id: gpt-4o-mini
  options:
    temperature: 0.4
    function_choice_behavior:
      type: auto
      functions:
        - MenuPlugin.GetSpecials
        - MenuPlugin.GetItemPrice
---
Answer questions about the menu.
```

#### 함수 호출이 있는 `OpenAIAssistantAgent`

코드 우선 접근 방식:

```csharp
OpenAIAssistantAgent agent =
    await OpenAIAssistantAgent.CreateAsync(
        clientProvider: this.GetClientProvider(),
        definition: new OpenAIAssistantDefinition("gpt_4o")
        {
            Instructions = "Answer questions about the menu.",
            Name = "RestaurantHost",
            Metadata = new Dictionary<string, string> { { AssistantSampleMetadataKey, bool.TrueString } },
        },
        kernel: new Kernel());

KernelPlugin plugin = KernelPluginFactory.CreateFromType<MenuPlugin>();
agent.Kernel.Plugins.Add(plugin);
```

Semantic Kernel 스키마를 사용한 선언적 방식:

아래 구문을 사용하면 어시스턴트는 정의에 함수가 포함되지 않습니다.
함수는 Agent와 연결된 `Kernel` 인스턴스에 추가되어야 하며, Agent가 호출될 때 전달됩니다.

```yml
---
name: RestaurantHost
type: openai_assistant
description: This agent answers questions about the menu.
model:
  id: gpt-4o-mini
  options:
    temperature: 0.4
    function_choice_behavior:
      type: auto
      functions:
        - MenuPlugin.GetSpecials
        - MenuPlugin.GetItemPrice
    metadata:
      sksample: true
---
Answer questions about the menu.
``

또는

```yml
---
name: RestaurantHost
type: openai_assistant
description: This agent answers questions about the menu.
execution_settings:
  default:
    temperature: 0.4
tools:
  - type: function
    name: MenuPlugin-GetSpecials
    description: Provides a list of specials from the menu.
  - type: function
    name: MenuPlugin-GetItemPrice
    description: Provides the price of the requested menu item.
    parameters: '{"type":"object","properties":{"menuItem":{"type":"string","description":"The name of the menu item."}},"required":["menuItem"]}'
---
Answer questions about the menu.
```

**참고**: Agent를 생성하는 데 사용되는 `Kernel` 인스턴스에는 서비스로 등록된 `OpenAIClientProvider` 인스턴스가 있어야 합니다.

#### 도구가 있는 `OpenAIAssistantAgent`

코드 우선 접근 방식:

```csharp
OpenAIAssistantAgent agent =
    await OpenAIAssistantAgent.CreateAsync(
        clientProvider: this.GetClientProvider(),
        definition: new(this.Model)
        {
            Instructions = "You are an Agent that can write and execute code to answer questions.",
            Name = "Coder",
            EnableCodeInterpreter = true,
            EnableFileSearch = true,
            Metadata = new Dictionary<string, string> { { AssistantSampleMetadataKey, bool.TrueString } },
        },
        kernel: new Kernel());
```

Semantic Kernel을 사용한 선언적 방식:

```yml
---
name: Coder
type: openai_assistant
tools:
    - type: code_interpreter
    - type: file_search
---
You are an Agent that can write and execute code to answer questions.
```

### 선언적 형식 사용 사례

#### 에이전트와 파일에 대한 메타데이터

```yaml
name: RestaurantHost
type: azureai_agent
description: This agent answers questions about the menu.
version: 0.0.1
```

#### 함수 도구에 대한 접근과 동작을 안내하는 지시사항 세트를 가진 에이전트 생성

#### 에이전트 지시사항(및 기타 속성)의 템플릿 허용

#### 모델 구성 및 여러 모델 구성 제공

#### 에이전트가 사용할 데이터 소스(컨텍스트/지식) 구성

#### 에이전트가 사용할 추가 도구 구성. 예: 코드 인터프리터, OpenAPI 엔드포인트

#### 에이전트에 대한 추가 모달리티 활성화. 예: 음성

#### 오류 조건. 예: 모델이나 함수 도구를 사용할 수 없는 경우
