# Semantic Kernel

**이 엔터프라이즈급 오케스트레이션 프레임워크로 지능형 AI 에이전트 및 멀티 에이전트 시스템을 구축하세요**

[![License: MIT](https://img.shields.io/github/license/microsoft/semantic-kernel)](https://github.com/microsoft/semantic-kernel/blob/main/LICENSE)
[![Python package](https://img.shields.io/pypi/v/semantic-kernel)](https://pypi.org/project/semantic-kernel/)
[![Nuget package](https://img.shields.io/nuget/vpre/Microsoft.SemanticKernel)](https://www.nuget.org/packages/Microsoft.SemanticKernel/)
[![Discord](https://img.shields.io/discord/1063152441819942922?label=Discord&logo=discord&logoColor=white&color=d82679)](https://aka.ms/SKDiscord)


## Semantic Kernel이란?

Semantic Kernel은 개발자가 AI 에이전트 및 멀티 에이전트 시스템을 구축, 오케스트레이션, 배포할 수 있도록 지원하는 모델 비종속(model-agnostic) SDK입니다. 간단한 챗봇부터 복잡한 멀티 에이전트 워크플로까지, Semantic Kernel은 엔터프라이즈급 안정성과 유연성을 갖춘 도구를 제공합니다.

## 시스템 요구 사항

- **Python**: 3.10+
- **.NET**: .NET 10.0+ 
- **Java**: JDK 17+
- **OS 지원**: Windows, macOS, Linux

## 주요 기능

- **모델 유연성**: [OpenAI](https://platform.openai.com/docs/introduction), [Azure OpenAI](https://azure.microsoft.com/en-us/products/ai-services/openai-service), [Hugging Face](https://huggingface.co/), [NVidia](https://www.nvidia.com/en-us/ai-data-science/products/nim-microservices/) 등에 대한 기본 지원으로 모든 LLM에 연결
- **에이전트 프레임워크**: 도구/플러그인, 메모리, 계획 기능에 접근 가능한 모듈형 AI 에이전트 구축
- **멀티 에이전트 시스템**: 전문 에이전트가 협업하는 복잡한 워크플로 오케스트레이션
- **플러그인 생태계**: 네이티브 코드 함수, 프롬프트 템플릿, OpenAPI 스펙 또는 Model Context Protocol(MCP)으로 확장
- **벡터 DB 지원**: [Azure AI Search](https://learn.microsoft.com/en-us/azure/search/search-what-is-azure-search), [Elasticsearch](https://www.elastic.co/), [Chroma](https://docs.trychroma.com/docs/overview/getting-started) 등과 원활한 통합
- **멀티모달 지원**: 텍스트, 비전, 오디오 입력 처리
- **로컬 배포**: [Ollama](https://ollama.com/), [LMStudio](https://lmstudio.ai/) 또는 [ONNX](https://onnx.ai/)로 실행
- **프로세스 프레임워크**: 구조화된 워크플로 접근 방식으로 복잡한 비즈니스 프로세스 모델링
- **엔터프라이즈 대응**: 관측성, 보안 및 안정적인 API를 위해 설계

## 설치

먼저 AI 서비스용 환경 변수를 설정합니다:

**Azure OpenAI:**
```bash
export AZURE_OPENAI_API_KEY=AAA....
```

**또는 OpenAI 직접 사용:**
```bash
export OPENAI_API_KEY=sk-...
```

### Python

```bash
pip install semantic-kernel
```

### .NET

```bash
dotnet add package Microsoft.SemanticKernel
dotnet add package Microsoft.SemanticKernel.Agents.Core
```

### Java

[semantic-kernel-java 빌드](https://github.com/microsoft/semantic-kernel-java/blob/main/BUILD.md) 문서를 참조하세요.

## 빠른 시작

### 기본 에이전트 - Python

사용자 프롬프트에 응답하는 간단한 어시스턴트를 생성합니다:

```python
import asyncio
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion

async def main():
    # 기본 지시사항으로 채팅 에이전트 초기화
    agent = ChatCompletionAgent(
        service=AzureChatCompletion(),
        name="SK-Assistant",
        instructions="You are a helpful assistant.",
    )

    # 사용자 메시지에 대한 응답 받기
    response = await agent.get_response(messages="Write a haiku about Semantic Kernel.")
    print(response.content)

asyncio.run(main()) 

# Output:
# Language's essence,
# Semantic threads intertwine,
# Meaning's core revealed.
```

### 기본 에이전트 - .NET

```csharp
using Microsoft.SemanticKernel;
using Microsoft.SemanticKernel.Agents;

var builder = Kernel.CreateBuilder();
builder.AddAzureOpenAIChatCompletion(
                Environment.GetEnvironmentVariable("AZURE_OPENAI_DEPLOYMENT"),
                Environment.GetEnvironmentVariable("AZURE_OPENAI_ENDPOINT"),
                Environment.GetEnvironmentVariable("AZURE_OPENAI_API_KEY")
                );
var kernel = builder.Build();

ChatCompletionAgent agent =
    new()
    {
        Name = "SK-Agent",
        Instructions = "You are a helpful assistant.",
        Kernel = kernel,
    };

await foreach (AgentResponseItem<ChatMessageContent> response 
    in agent.InvokeAsync("Write a haiku about Semantic Kernel."))
{
    Console.WriteLine(response.Message);
}

// Output:
// Language's essence,
// Semantic threads intertwine,
// Meaning's core revealed.
```

### 플러그인이 있는 에이전트 - Python

커스텀 도구(플러그인)와 구조화된 출력으로 에이전트를 강화합니다:

```python
import asyncio
from typing import Annotated
from pydantic import BaseModel
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion, OpenAIChatPromptExecutionSettings
from semantic_kernel.functions import kernel_function, KernelArguments

class MenuPlugin:
    @kernel_function(description="Provides a list of specials from the menu.")
    def get_specials(self) -> Annotated[str, "Returns the specials from the menu."]:
        return """
        Special Soup: Clam Chowder
        Special Salad: Cobb Salad
        Special Drink: Chai Tea
        """

    @kernel_function(description="Provides the price of the requested menu item.")
    def get_item_price(
        self, menu_item: Annotated[str, "The name of the menu item."]
    ) -> Annotated[str, "Returns the price of the menu item."]:
        return "$9.99"

class MenuItem(BaseModel):
    price: float
    name: str

async def main():
    # 구조화된 출력 형식 설정
    settings = OpenAIChatPromptExecutionSettings()
    settings.response_format = MenuItem

    # 플러그인과 설정으로 에이전트 생성
    agent = ChatCompletionAgent(
        service=AzureChatCompletion(),
        name="SK-Assistant",
        instructions="You are a helpful assistant.",
        plugins=[MenuPlugin()],
        arguments=KernelArguments(settings)
    )

    response = await agent.get_response(messages="What is the price of the soup special?")
    print(response.content)

    # Output:
    # The price of the Clam Chowder, which is the soup special, is $9.99.

asyncio.run(main()) 
```

### 플러그인이 있는 에이전트 - .NET

```csharp
using System.ComponentModel;
using Microsoft.SemanticKernel;
using Microsoft.SemanticKernel.Agents;
using Microsoft.SemanticKernel.ChatCompletion;

var builder = Kernel.CreateBuilder();
builder.AddAzureOpenAIChatCompletion(
                Environment.GetEnvironmentVariable("AZURE_OPENAI_DEPLOYMENT"),
                Environment.GetEnvironmentVariable("AZURE_OPENAI_ENDPOINT"),
                Environment.GetEnvironmentVariable("AZURE_OPENAI_API_KEY")
                );
var kernel = builder.Build();

kernel.Plugins.Add(KernelPluginFactory.CreateFromType<MenuPlugin>());

ChatCompletionAgent agent =
    new()
    {
        Name = "SK-Assistant",
        Instructions = "You are a helpful assistant.",
        Kernel = kernel,
        Arguments = new KernelArguments(new PromptExecutionSettings() { FunctionChoiceBehavior = FunctionChoiceBehavior.Auto() })

    };

await foreach (AgentResponseItem<ChatMessageContent> response 
    in agent.InvokeAsync("What is the price of the soup special?"))
{
    Console.WriteLine(response.Message);
}

sealed class MenuPlugin
{
    [KernelFunction, Description("Provides a list of specials from the menu.")]
    public string GetSpecials() =>
        """
        Special Soup: Clam Chowder
        Special Salad: Cobb Salad
        Special Drink: Chai Tea
        """;

    [KernelFunction, Description("Provides the price of the requested menu item.")]
    public string GetItemPrice(
        [Description("The name of the menu item.")]
        string menuItem) =>
        "$9.99";
}
```

### 멀티 에이전트 시스템 - Python

협업할 수 있는 전문 에이전트 시스템을 구축합니다:

```python
import asyncio
from semantic_kernel.agents import ChatCompletionAgent, ChatHistoryAgentThread
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion, OpenAIChatCompletion

billing_agent = ChatCompletionAgent(
    service=AzureChatCompletion(), 
    name="BillingAgent", 
    instructions="You handle billing issues like charges, payment methods, cycles, fees, discrepancies, and payment failures."
)

refund_agent = ChatCompletionAgent(
    service=AzureChatCompletion(),
    name="RefundAgent",
    instructions="Assist users with refund inquiries, including eligibility, policies, processing, and status updates.",
)

triage_agent = ChatCompletionAgent(
    service=OpenAIChatCompletion(),
    name="TriageAgent",
    instructions="Evaluate user requests and forward them to BillingAgent or RefundAgent for targeted assistance."
    " Provide the full answer to the user containing any information from the agents",
    plugins=[billing_agent, refund_agent],
)

thread: ChatHistoryAgentThread = None

async def main() -> None:
    print("Welcome to the chat bot!\n  Type 'exit' to exit.\n  Try to get some billing or refund help.")
    while True:
        user_input = input("User:> ")

        if user_input.lower().strip() == "exit":
            print("\n\nExiting chat...")
            return False

        response = await triage_agent.get_response(
            messages=user_input,
            thread=thread,
        )

        if response:
            print(f"Agent :> {response}")

# Agent :> I understand that you were charged twice for your subscription last month, and I'm here to assist you with resolving this issue. Here's what we need to do next:

# 1. **Billing Inquiry**:
#    - Please provide the email address or account number associated with your subscription, the date(s) of the charges, and the amount charged. This will allow the billing team to investigate the discrepancy in the charges.

# 2. **Refund Process**:
#    - For the refund, please confirm your subscription type and the email address associated with your account.
#    - Provide the dates and transaction IDs for the charges you believe were duplicated.

# Once we have these details, we will be able to:

# - Check your billing history for any discrepancies.
# - Confirm any duplicate charges.
# - Initiate a refund for the duplicate payment if it qualifies. The refund process usually takes 5-10 business days after approval.

# Please provide the necessary details so we can proceed with resolving this issue for you.


if __name__ == "__main__":
    asyncio.run(main())
```



## 다음 단계

1. [시작 가이드](https://learn.microsoft.com/en-us/semantic-kernel/get-started/quick-start-guide)를 따라해 보거나 [에이전트 구축](https://learn.microsoft.com/en-us/semantic-kernel/frameworks/agent/)에 대해 알아보세요
2. 100개 이상의 [상세 샘플](https://learn.microsoft.com/en-us/semantic-kernel/get-started/detailed-samples)을 살펴보세요
3. Semantic Kernel의 핵심 [개념](https://learn.microsoft.com/en-us/semantic-kernel/concepts/kernel)을 알아보세요

### API 레퍼런스

- [C# API 레퍼런스](https://learn.microsoft.com/en-us/dotnet/api/microsoft.semantickernel?view=semantic-kernel-dotnet)
- [Python API 레퍼런스](https://learn.microsoft.com/en-us/python/api/semantic-kernel/semantic_kernel?view=semantic-kernel-python)

## 문제 해결

### 일반적인 문제

- **인증 오류**: API 키 환경 변수가 올바르게 설정되었는지 확인하세요
- **모델 가용성**: Azure OpenAI 배포 또는 OpenAI 모델 접근 권한을 확인하세요

### 도움 받기

- 알려진 문제는 [GitHub 이슈](https://github.com/microsoft/semantic-kernel/issues)를 확인하세요
- [Discord 커뮤니티](https://aka.ms/SKDiscord)에서 해결 방법을 검색하세요
- 도움을 요청할 때 SDK 버전과 전체 오류 메시지를 포함해 주세요


## 커뮤니티 참여

SK 커뮤니티에 대한 여러분의 기여와 제안을 환영합니다! 가장 쉽게 참여하는 방법 중 하나는 GitHub 리포지토리에서 토론에 참여하는 것입니다. 버그 리포트와 수정 사항을 환영합니다!

새로운 기능, 컴포넌트 또는 확장 기능의 경우, PR을 보내기 전에 이슈를 열어 먼저 논의해 주세요. 이는 핵심 방향이 다를 수 있어 거부될 수 있는 상황을 방지하기 위함이며, 더 큰 생태계에 대한 영향도 고려하기 위함입니다.

더 알아보고 시작하려면:

- [문서](https://aka.ms/sk/learn)를 읽어보세요
- 프로젝트에 [기여하는 방법](https://learn.microsoft.com/en-us/semantic-kernel/support/contributing)을 알아보세요
- [GitHub 토론](https://github.com/microsoft/semantic-kernel/discussions)에서 질문하세요
- [Discord 커뮤니티](https://aka.ms/SKDiscord)에서 질문하세요

- 정기 [오피스 아워 및 SK 커뮤니티 이벤트](COMMUNITY.md)에 참석하세요
- [블로그](https://aka.ms/sk/blog)에서 팀 소식을 확인하세요

## 기여자 명예의 전당

[![semantic-kernel contributors](https://contrib.rocks/image?repo=microsoft/semantic-kernel)](https://github.com/microsoft/semantic-kernel/graphs/contributors)

## 행동 강령

이 프로젝트는
[Microsoft 오픈 소스 행동 강령](https://opensource.microsoft.com/codeofconduct/)을 채택하였습니다.
자세한 내용은
[행동 강령 FAQ](https://opensource.microsoft.com/codeofconduct/faq/)를 참조하거나
추가 질문이나 의견이 있으면 [opencode@microsoft.com](mailto:opencode@microsoft.com)으로
연락해 주세요.

## 라이선스

Copyright (c) Microsoft Corporation. All rights reserved.

[MIT](LICENSE) 라이선스에 따라 사용이 허가됩니다.
