---
# 저장소에서 샘플 코드의 구조를 재편성

status: accepted
contact: rogerbarreto
date: 2024-04-18
deciders: rogerbarreto, markwallace-microsoft, sophialagerkranspandey, matthewbolanos
consulted: dmytrostruk, sergeymenshik, westey-m, eavanvalkenburg
informed:
---

## 배경 및 문제 설명

- 현재 샘플이 구조화된 방식은 정보가 충분하지 않고 찾기 쉽지 않습니다.
- Kernel Syntax Examples의 번호 매기기는 의미를 잃었습니다.
- 프로젝트의 명명이 실제로 무엇인지에 대한 명확한 메시지를 전달하지 못합니다.
- 폴더와 솔루션에 `Examples` 접미사가 있으며, `samples` 안의 모든 것은 이미 `example`이므로 불필요합니다.

### 현재 식별된 샘플 유형

| 유형             | 설명                                                                                              |
| ---------------- | -------------------------------------------------------------------------------------------------------- |
| `GettingStarted` | 시작하기 위한 단계별 튜토리얼                                                            |
| `Concepts`       | 기능별 개념 코드 스니펫                                                              |
| `LearnResources` | Microsoft Learn, DevBlogs 등 온라인 문서 소스와 관련된 코드 스니펫 |
| `Tutorials`      | 더 심층적인 단계별 튜토리얼                                                                     |
| `Demos`          | 하나 이상의 기능을 활용하는 데모 애플리케이션                               |

## 결정 동인 및 원칙

- **쉬운 검색**: 잘 조직된 구조로 다양한 유형의 샘플을 쉽게 찾을 수 있게 함
- **간결한 명명**: 폴더, 솔루션, 예제 이름이 가능한 한 명확하고 짧게
- **명확한 메시지 전달**: Semantic Kernel 특정 용어나 전문 용어 사용 지양
- **크로스 언어**: 샘플 구조가 지원되는 모든 SK 언어에서 유사하게 유지

## 기존 폴더에 대한 전략

| 현재 폴더                       | 제안                                                            |
| ------------------------------------ | ------------------------------------------------------------------- |
| KernelSyntaxExamples/Getting_Started | `GettingStarted`로 이동                                          |
| KernelSyntaxExamples/`Examples??_*`  | `Concepts`의 여러 개념별 하위 폴더로 분해         |
| AgentSyntaxExamples                  | `Concepts`의 `Agents` 특정 하위 폴더로 분해.          |
| DocumentationExamples                | `LearnResources` 하위 폴더로 이동하고 `MicrosoftLearn`으로 이름 변경 |
| CreateChatGptPlugin                  | `Demo` 하위 폴더로 이동                                          |
| HomeAutomation                       | `Demo` 하위 폴더로 이동                                          |
| TelemetryExample                     | `Demo` 하위 폴더로 이동하고 `TelemetryWithAppInsights`로 이름 변경 |
| HuggingFaceImageTextExample          | `Demo` 하위 폴더로 이동하고 `HuggingFaceImageToText`로 이름 변경   |

## 검토된 루트 구조 옵션

아래 옵션들은 `samples` 폴더의 루트 구조에 대해 검토된 잠재적 옵션입니다.

### 옵션 1 - 극도로 좁은 루트 분류

이 옵션은 `samples` 폴더의 루트를 다른 하위 카테고리로 최대한 압축하여 샘플을 찾을 때 미니멀하게 합니다.

제안된 루트 구조

```
samples/
├── Tutorials/
│   └── Getting Started/
├── Concepts/
│   ├── Kernel Syntax**
│   └── Agents Syntax**
├── Resources/
└── Demos/
```

장점:

- 더 단순하고 덜 장황한 구조 (Worse is Better: Less is more 접근)
- 초보자에게 필요와 사용 사례에 더 잘 맞을 수 있는 다른 튜토리얼이 (형제 폴더로) 제시됩니다.
- Getting started가 강제되지 않습니다.

단점:

- `Getting Started`가 튜토리얼이라는 것을 알기 위한 추가 인지 부하가 있을 수 있음

### 옵션 2 - Getting Started 루트 분류

이 옵션은 `옵션 1`에서 제안된 구조에 비해 `Getting Started`를 루트 `samples` 폴더로 가져옵니다.

제안된 루트 구조

```
samples/
├── Getting Started/
├── Tutorials/
├── Concepts/
│   ├── Kernel Syntax Decomposition**
│   └── Agents Syntax Decomposition**
├── Resources/
└── Demos/
```

장점:

- Getting Started가 고객이 가장 먼저 보게 되는 것
- 초보자는 시작하기 위해 한 번의 추가 클릭이 필요합니다.

단점:

- Getting started 예제에 고객에게 유효한 예제가 없으면 더 많은 콘텐츠를 위해 다른 폴더로 돌아가야 합니다.

### 옵션 3 - 보수적 + 사용 사례 기반 루트 분류

이 옵션은 더 보수적이며 Syntax Examples 프로젝트를 루트 옵션으로 유지하고, 사용 사례, 모달리티, 커널 콘텐츠를 위한 새 폴더도 추가합니다.

제안된 루트 구조

```
samples/
|── QuickStart/
|── Tutorials/
├── KernelSyntaxExamples/
├── AgentSyntaxExamples/
├── UseCases/ OR Demos/
├── KernelContent/ OR Modalities/
├── Documentation/ OR Resources/
```

장점:

- 더 보수적인 접근으로, KernelSyntaxExamples와 AgentSyntaxExamples를 루트 폴더로 유지하면 기존 인터넷 링크가 깨지지 않습니다.
- 사용 사례, 모달리티, 커널 콘텐츠는 다양한 유형의 샘플을 위한 더 구체적인 폴더

단점:

- 더 장황한 구조가 샘플을 찾는 데 추가 마찰을 줍니다.
- `KernelContent` 또는 `Modalities`는 고객에게 명확하지 않을 수 있는 내부 용어
- `Documentation`은 문서 전용 폴더로 혼동될 수 있으나, 실제로는 문서에 사용된 코드 샘플을 포함합니다. (명확한 메시지가 아님)
- `Use Cases`는 구현된 실제 사용 사례를 암시할 수 있으나, 실제로는 SK 기능의 간단한 데모입니다.

## KernelSyntaxExamples 분해 옵션

현재 Kernel Syntax Examples에는 70개 이상의 번호가 매겨진 예제가 나란히 있으며, 번호는 진행 의미가 없고 정보가 충분하지 않습니다.

다음 옵션들은 개발된 커널 `Concepts` 및 기능에 기반하여 KernelSyntaxExamples 폴더를 여러 하위 폴더로 분해하는 것에 대해 검토됩니다.

식별된 컴포넌트 지향 개념:

- Kernel

  - Builder
  - Functions
    - Arguments
    - MethodFunctions
    - PromptFunctions
    - Types
    - Results
      - Serialization
      - Metadata
      - Strongly typed
    - InlineFunctions
  - Plugins
    - Describe Plugins
    - OpenAI Plugins
    - OpenAPI Plugins
      - API Manifest
    - gRPC Plugins
    - Mutable Plugins
  - AI Services (커널 호출을 통한 서비스 사용 예제)
    - Chat Completion
    - Text Generation
    - Service Selector
  - Hooks
  - Filters
    - Function Filtering
    - Template Rendering Filtering
    - Function Call Filtering (사용 가능 시)
  - Templates

- AI Services (단일/다중 + 스트리밍 및 비스트리밍 결과를 사용하여 서비스 직접 사용 예제)

  - ExecutionSettings
  - Chat Completion
    - Local Models
      - Ollama
      - HuggingFace
      - LMStudio
      - LocalAI
    - Gemini
    - OpenAI
    - AzureOpenAI
    - HuggingFace
  - Text Generation
    - Local Models
      - Ollama
      - HuggingFace
    - OpenAI
    - AzureOpenAI
    - HuggingFace
  - Text to Image
    - OpenAI
    - AzureOpenAI
  - Image to Text
    - HuggingFace
  - Text to Audio
    - OpenAI
  - Audio to Text
    - OpenAI
  - Custom
    - DYI
    - OpenAI
      - OpenAI File

- Memory Services

  - Search

    - Semantic Memory
    - Text Memory
    - Azure AI Search

  - Text Embeddings
    - OpenAI
    - HuggingFace

- Telemetry
- Logging
- Dependency Injection

- HttpClient

  - Resiliency
  - Usage

- Planners

  - Handlerbars

- Authentication

  - Azure AD

- Function Calling

  - Auto Function Calling
  - Manual Function Calling

- Filtering

  - Kernel Hooks
  - Service Selector

- Templates
- Resilience

- Memory

  - Semantic Memory
  - Text Memory Plugin
  - Search

- RAG

  - Inline
  - Function Calling

- Agents

  - Delegation
  - Charts
  - Collaboration
  - Authoring
  - Tools
  - Chat Completion Agent
    (Agent Syntax Examples가 번호 없이 여기에 들어감)

- Flow Orchestrator

### KernelSyntaxExamples 분해 옵션 1 - 컴포넌트별 개념

이 옵션은 커널 컴포넌트와 기능별로 구조화된 개념을 분해합니다.

처음에는 논리적이고 개념이 어떻게 관련되어 있는지, 제공된 구조를 따라 더 고급 개념으로 발전할 수 있는지 이해하기 쉬워 보입니다.

확장형 (폴더당 파일 수 적음):

```
Concepts/
├── Kernel/
│   ├── Builder/
│   ├── Functions/
│   │   ├── Arguments/
│   │   ├── MethodFunctions/
│   │   ├── PromptFunctions/
│   │   ├── Types/
│   │   ├── Results/
│   │   │   ├── Serialization/
│   │   │   ├── Metadata/
│   │   │   └── Strongly typed/
│   │   └── InlineFunctions/
│   ├── Plugins/
│   │   ├── Describe Plugins/
│   │   ├── OpenAI Plugins/
│   │   ├── OpenAPI Plugins/
│   │   │   └── API Manifest/
│   │   ├── gRPC Plugins/
│   │   └── Mutable Plugins/
│   ├── AI Services (커널 호출을 통한 서비스 사용 예제)/
│   │   ├── Chat Completion/
│   │   ├── Text Generation/
│   │   └── Service Selector/
│   ├── Hooks/
│   ├── Filters/
│   │   ├── Function Filtering/
│   │   ├── Template Rendering Filtering/
│   │   └── Function Call Filtering (사용 가능 시)/
│   └── Templates/
├── AI Services (단일/다중 + 스트리밍 및 비스트리밍 결과를 사용하여 서비스 직접 사용 예제)/
│   ├── ExecutionSettings/
│   ├── Chat Completion/
│   │   ├── LocalModels/
|   │   │   ├── LMStudio/
|   │   │   ├── LocalAI/
|   │   │   ├── Ollama/
|   │   │   └── HuggingFace/
│   │   ├── Gemini/
│   │   ├── OpenAI/
│   │   ├── AzureOpenAI/
│   │   ├── LMStudio/
│   │   ├── Ollama/
│   │   └── HuggingFace/
│   ├── Text Generation/
│   │   ├── LocalModels/
|   │   │   ├── Ollama/
|   │   │   └── HuggingFace/
│   │   ├── OpenAI/
│   │   ├── AzureOpenAI/
│   │   └── HuggingFace/
│   ├── Text to Image/
│   │   ├── OpenAI/
│   │   └── AzureOpenAI/
│   ├── Image to Text/
│   │   └── HuggingFace/
│   ├── Text to Audio/
│   │   └── OpenAI/
│   ├── Audio to Text/
│   │   └── OpenAI/
│   └── Custom/
│       ├── DYI/
│       └── OpenAI/
│           └── OpenAI File/
├── Memory Services/
│   ├── Search/
│   │   ├── Semantic Memory/
│   │   ├── Text Memory/
│   │   └── Azure AI Search/
│   └── Text Embeddings/
│       ├── OpenAI/
│       └── HuggingFace/
├── Telemetry/
├── Logging/
├── Dependency Injection/
├── HttpClient/
│   ├── Resiliency/
│   └── Usage/
├── Planners/
│   └── Handlerbars/
├── Authentication/
│   └── Azure AD/
├── Function Calling/
│   ├── Auto Function Calling/
│   └── Manual Function Calling/
├── Filtering/
│   ├── Kernel Hooks/
│   └── Service Selector/
├── Templates/
├── Resilience/
├── Memory/
│   ├── Semantic Memory/
│   ├── Text Memory Plugin/
│   └── Search/
├── RAG/
│   ├── Inline/
│   └── Function Calling/
├── Agents/
│   ├── Delegation/
│   ├── Charts/
│   ├── Collaboration/
│   ├── Authoring/
│   ├── Tools/
│   └── Chat Completion Agent/
│       (Agent Syntax Examples가 번호 없이 여기에 들어감)
└── Flow Orchestrator/
```

컴팩트형 (폴더당 파일 수 많음):

```
Concepts/
├── Kernel/
│   ├── Builder/
│   ├── Functions/
│   ├── Plugins/
│   ├── AI Services (커널 호출을 통한 서비스 사용 예제)/
│   │   ├── Chat Completion/
│   │   ├── Text Generation/
│   │   └── Service Selector/
│   ├── Hooks/
│   ├── Filters/
│   └── Templates/
├── AI Services (단일/다중 + 스트리밍 및 비스트리밍 결과를 사용하여 서비스 직접 사용 예제)/
│   ├── Chat Completion/
│   ├── Text Generation/
│   ├── Text to Image/
│   ├── Image to Text/
│   ├── Text to Audio/
│   ├── Audio to Text/
│   └── Custom/
├── Memory Services/
│   ├── Search/
│   └── Text Embeddings/
├── Telemetry/
├── Logging/
├── Dependency Injection/
├── HttpClient/
│   ├── Resiliency/
│   └── Usage/
├── Planners/
│   └── Handlerbars/
├── Authentication/
│   └── Azure AD/
├── Function Calling/
│   ├── Auto Function Calling/
│   └── Manual Function Calling/
├── Filtering/
│   ├── Kernel Hooks/
│   └── Service Selector/
├── Templates/
├── Resilience/
├── RAG/
├── Agents/
└── Flow Orchestrator/
```

장점:

- 컴포넌트가 어떻게 관련되어 있는지 이해하기 쉬움
- 더 고급 개념으로 발전하기 쉬움
- 특정 기능에 대한 샘플을 어디에 넣거나 추가할지 명확한 그림

단점:

- 매우 깊은 구조로 개발자가 탐색하기에 부담스러울 수 있음
- 구조가 명확하지만 너무 장황할 수 있음

### KernelSyntaxExamples 분해 옵션 2 - 컴포넌트별 개념 평면화 버전

옵션 1과 유사한 접근이지만, 깊은 중첩과 복잡성을 피하기 위해 단일 수준의 폴더를 사용하는 평면화된 구조이면서도 컴포넌트화된 개념을 쉽게 탐색할 수 있게 유지합니다.

확장형 (폴더당 파일 수 적음):

```
Concepts/
├── KernelBuilder
├── Kernel.Functions.Arguments
├── Kernel.Functions.MethodFunctions
├── Kernel.Functions.PromptFunctions
├── Kernel.Functions.Types
├── Kernel.Functions.Results.Serialization
├── Kernel.Functions.Results.Metadata
├── Kernel.Functions.Results.StronglyTyped
├── Kernel.Functions.InlineFunctions
├── Kernel.Plugins.DescribePlugins
├── Kernel.Plugins.OpenAIPlugins
├── Kernel.Plugins.OpenAPIPlugins.APIManifest
├── Kernel.Plugins.gRPCPlugins
├── Kernel.Plugins.MutablePlugins
├── Kernel.AIServices.ChatCompletion
├── Kernel.AIServices.TextGeneration
├── Kernel.AIServices.ServiceSelector
├── Kernel.Hooks
├── Kernel.Filters.FunctionFiltering
├── Kernel.Filters.TemplateRenderingFiltering
├── Kernel.Filters.FunctionCallFiltering
├── Kernel.Templates
├── AIServices.ExecutionSettings
├── AIServices.ChatCompletion.Gemini
├── AIServices.ChatCompletion.OpenAI
├── AIServices.ChatCompletion.AzureOpenAI
├── AIServices.ChatCompletion.HuggingFace
├── AIServices.TextGeneration.OpenAI
├── AIServices.TextGeneration.AzureOpenAI
├── AIServices.TextGeneration.HuggingFace
├── AIServices.TextToImage.OpenAI
├── AIServices.TextToImage.AzureOpenAI
├── AIServices.ImageToText.HuggingFace
├── AIServices.TextToAudio.OpenAI
├── AIServices.AudioToText.OpenAI
├── AIServices.Custom.DIY
├── AIServices.Custom.OpenAI.OpenAIFile
├── MemoryServices.Search.SemanticMemory
├── MemoryServices.Search.TextMemory
├── MemoryServices.Search.AzureAISearch
├── MemoryServices.TextEmbeddings.OpenAI
├── MemoryServices.TextEmbeddings.HuggingFace
├── Telemetry
├── Logging
├── DependencyInjection
├── HttpClient.Resiliency
├── HttpClient.Usage
├── Planners.Handlerbars
├── Authentication.AzureAD
├── FunctionCalling.AutoFunctionCalling
├── FunctionCalling.ManualFunctionCalling
├── Filtering.KernelHooks
├── Filtering.ServiceSelector
├── Templates
├── Resilience
├── RAG.Inline
├── RAG.FunctionCalling
├── Agents.Delegation
├── Agents.Charts
├── Agents.Collaboration
├── Agents.Authoring
├── Agents.Tools
├── Agents.ChatCompletionAgent
└── FlowOrchestrator
```

컴팩트형 (폴더당 파일 수 많음):

```
Concepts/
├── KernelBuilder
├── Kernel.Functions
├── Kernel.Plugins
├── Kernel.AIServices
├── Kernel.Hooks
├── Kernel.Filters
├── Kernel.Templates
├── AIServices.ChatCompletion
├── AIServices.TextGeneration
├── AIServices.TextToImage
├── AIServices.ImageToText
├── AIServices.TextToAudio
├── AIServices.AudioToText
├── AIServices.Custom
├── MemoryServices.Search
├── MemoryServices.TextEmbeddings
├── Telemetry
├── Logging
├── DependencyInjection
├── HttpClient
├── Planners.Handlerbars
├── Authentication.AzureAD
├── FunctionCalling
├── Filtering
├── Templates
├── Resilience
├── RAG
├── Agents
└── FlowOrchestrator
```

장점:

- 컴포넌트가 어떻게 관련되어 있는지 이해하기 쉬움
- 더 고급 개념으로 발전하기 쉬움
- 특정 기능에 대한 샘플을 어디에 넣거나 추가할지 명확한 그림
- 평면화된 구조로 깊은 중첩을 피하고 IDE와 GitHub UI에서 탐색이 더 쉬움.

단점:

- 구조가 탐색하기 쉽지만 여전히 너무 장황할 수 있음

# KernelSyntaxExamples 분해 옵션 3 - 기능 그룹별 개념

이 옵션은 크고 관련된 기능을 함께 그룹화하여 Kernel Syntax Examples를 분해합니다.

```
Concepts/
├── Functions/
├── Chat Completion/
├── Text Generation/
├── Text to Image/
├── Image to Text/
├── Text to Audio/
├── Audio to Text/
├── Telemetry
├── Logging
├── Dependency Injection
├── Plugins
├── Auto Function Calling
├── Filtering
├── Memory
├── Search
├── Agents
├── Templates
├── RAG
├── Prompts
└── LocalModels/
```

장점:

- 더 작은 구조, 탐색이 더 쉬움
- 특정 기능에 대한 샘플을 어디에 넣거나 추가할지 명확한 그림

단점:

- 컴포넌트가 어떻게 관련되어 있는지에 대한 명확한 그림을 제공하지 않음
- 구조가 더 상위 수준이므로 파일당 더 많은 예제가 필요할 수 있음
- 더 고급 개념으로 발전하기 어려움
- 동일한 폴더를 공유하는 예제가 더 많아 특정 예제를 찾기 어려움 (KernelSyntaxExamples 폴더의 주요 문제점)

# KernelSyntaxExamples 분해 옵션 4 - 난이도별 개념

기본에서 전문가까지 난이도별로 예제를 분류합니다. 전반적인 구조는 옵션 3과 유사하지만, 해당 복잡성 수준을 가진 경우에만 하위 항목이 달라집니다.

```
Concepts/
├── 200-Basic
|  ├── Functions
|  ├── Chat Completion
|  ├── Text Generation
|  └── ..기본 전용 폴더/파일 ..
├── 300-Intermediate
|  ├── Functions
|  ├── Chat Completion
|  └── ..중급 전용 폴더/파일 ..
├── 400-Advanced
|  ├── Manual Function Calling
|  └── ..고급 전용 폴더/파일 ..
├── 500-Expert
|  ├── Functions
|  ├── Manual Function Calling
|  └── ..전문가 전용 폴더/파일 ..

```

장점:

- 초보자가 올바른 난이도와 예제로 안내되며 복잡도별로 더 조직화됨

단점:

- 기본, 중급, 고급, 전문가 수준의 정의가 없음
- 난이도별로 더 많은 예제가 필요할 수 있음
- 컴포넌트가 어떻게 관련되어 있는지 명확하지 않음
- 예제를 만들 때 예제의 난이도를 알기 어려우며, 여러 다른 수준에 해당할 수 있는 여러 예제를 어떻게 분산할지 어려움

## 결정 결과

선택된 옵션:

[x] 루트 구조 결정: **옵션 2** - Getting Started 루트 분류

[x] KernelSyntaxExamples 분해 결정: **옵션 3** - 기능 그룹별 개념
