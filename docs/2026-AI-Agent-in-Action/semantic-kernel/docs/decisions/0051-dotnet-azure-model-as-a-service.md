---
# 이 항목들은 선택 사항입니다. 필요 없는 항목은 자유롭게 제거하세요.
status: proposed
contact: rogerbarreto
date: 2024-08-07
deciders: rogerbarreto, markwallace-microsoft
consulted: taochen
---

# .Net Azure Model-as-a-Service (Azure AI Studio) 커넥터 지원

## 컨텍스트 및 문제 설명

고객으로부터 [Azure AI Studio - 서버리스 API](https://learn.microsoft.com/en-us/azure/ai-studio/how-to/model-catalog-overview#model-deployment-managed-compute-and-serverless-api-pay-as-you-go)에 배포된 모델을 기본적으로 사용하고 지원해 달라는 요구가 있었습니다. 이 소비 모델은 종량제 방식으로 운영되며, 일반적으로 토큰 기반으로 과금됩니다. 클라이언트는 [Azure AI Model Inference API](https://learn.microsoft.com/en-us/azure/ai-studio/reference/reference-model-inference-api?tabs=azure-studio) 또는 클라이언트 SDK를 통해 서비스에 접근할 수 있습니다.

현재 [Azure AI Studio](https://learn.microsoft.com/en-us/azure/ai-studio/what-is-ai-studio)에 대한 공식 지원이 없습니다. 이 ADR의 목적은 서비스의 제약 사항을 검토하고, 새로운 AI 커넥터 개발을 통해 서비스 지원을 가능하게 하는 잠재적 솔루션을 탐색하는 것입니다.

## .NET용 Azure Inference 클라이언트 라이브러리

Azure 팀은 서비스와의 효과적인 상호작용을 위해 .Net에서 [Azure.AI.Inference](https://github.com/Azure/azure-sdk-for-net/blob/Azure.AI.Inference_1.0.0-beta.1/sdk/ai/Azure.AI.Inference/README.md)라는 새 클라이언트 라이브러리를 제공합니다. 서비스 API가 OpenAI와 호환되지만, 서비스 상호작용에 OpenAI 및 Azure OpenAI 클라이언트 라이브러리를 사용하는 것은 허용되지 않습니다. 이는 모델과 공급자에 대해 독립적이지 않기 때문입니다. Azure AI Studio는 OpenAI 모델 외에도 다양한 오픈소스 모델을 제공합니다.

### 제한 사항

현재 클라이언트 SDK의 첫 번째 버전은 `Chat Completion`, `Text Embedding Generation`, `Image Embedding Generation`만 지원하며 `TextToImage Generation`이 계획되어 있는 것으로 알려져 있습니다.

`Text Generation` 모달리티를 지원할 현재 계획은 없습니다.

## AI 커넥터

### 네임스페이스 옵션

- `Microsoft.SemanticKernel.Connectors.AzureAI`
- `Microsoft.SemanticKernel.Connectors.AzureAIInference`
- `Microsoft.SemanticKernel.Connectors.AzureAIModelInference`

결정: `Microsoft.SemanticKernel.Connectors.AzureAIInference`

### 모델별 파라미터 지원

모델은 기본 API에 포함되지 않은 추가 파라미터를 가질 수 있습니다. 서비스 API와 클라이언트 SDK는 모델별 파라미터를 제공할 수 있도록 합니다. 사용자는 `temperature`, `top_p` 등의 설정과 함께 전용 인수를 통해 모델별 설정을 제공할 수 있습니다.

Azure AI Inference 특화 `PromptExecutionSettings`는 이러한 사용자 정의 가능한 파라미터를 지원할 것입니다.

### 기능 브랜치

Azure AI Inference 커넥터의 개발은 `feature-connectors-azureaiinference`라는 기능 브랜치에서 수행됩니다.
