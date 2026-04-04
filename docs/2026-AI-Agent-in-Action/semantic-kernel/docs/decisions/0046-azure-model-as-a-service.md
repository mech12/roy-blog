---
# 이 항목들은 선택 사항입니다. 필요 없는 항목은 자유롭게 제거하세요.
status: { accepted }
contact: { rogerbarreto, taochen }
date: { 2024-06-20 }
deciders: { alliscode, moonbox3, eavanvalkenburg }
consulted: {}
informed: {}
---

# SK에서의 Azure Model-as-a-Service 지원

## 컨텍스트 및 문제 설명

고객들로부터 SK에서의 Model-as-a-Service(MaaS) 구현에 대한 요구가 있었습니다. MaaS는 [서버리스 API](https://learn.microsoft.com/en-us/azure/ai-studio/how-to/model-catalog-overview#model-deployment-managed-compute-and-serverless-api-pay-as-you-go)라고도 불리며, [Azure AI Studio](https://learn.microsoft.com/en-us/azure/ai-studio/what-is-ai-studio)에서 이용 가능합니다. 이 소비 모델은 종량제 방식으로 운영되며, 일반적으로 토큰 기반으로 과금됩니다. 클라이언트는 [Azure AI Model Inference API](https://learn.microsoft.com/en-us/azure/ai-studio/reference/reference-model-inference-api?tabs=azure-studio) 또는 클라이언트 SDK를 통해 서비스에 접근할 수 있습니다.

현재 SK에서는 MaaS에 대한 공식 지원이 없습니다. 이 ADR의 목적은 서비스의 제약 사항을 검토하고, 새로운 AI 커넥터 개발을 통해 서비스 지원을 가능하게 하는 잠재적 솔루션을 탐색하는 것입니다.

## 클라이언트 SDK

Azure 팀은 서비스와의 효과적인 상호작용을 위해 .Net에서는 `Azure.AI.Inference`, Python에서는 `azure-ai-inference`라는 새로운 클라이언트 라이브러리를 제공할 예정입니다. 서비스 API가 OpenAI와 호환되지만, 서비스 상호작용에 OpenAI 및 Azure OpenAI 클라이언트 라이브러리를 사용하는 것은 허용되지 않습니다. 이는 모델과 공급자에 대해 독립적이지 않기 때문입니다. Azure AI Studio는 OpenAI 모델 외에도 다양한 오픈소스 모델을 제공합니다.

### 제한 사항

클라이언트 SDK의 초기 릴리스는 채팅 완성(Chat Completion)과 텍스트/이미지 임베딩 생성만 지원하며, 이미지 생성은 추후 추가될 예정입니다.

텍스트 완성(Text Completion) 지원 계획은 현재 불명확하며, SDK에 텍스트 완성 지원이 포함될 가능성은 매우 낮습니다. 따라서 새로운 AI 커넥터는 더 많은 고객 요청이 있거나 클라이언트 SDK에서 지원이 추가될 때까지 초기 버전에서 텍스트 완성을 **지원하지 않을** 것입니다.

## AI 커넥터

### 네이밍 옵션

- Azure
- AzureAI
- AzureAIInference
- AzureAIModelInference

  결정: `AzureAIInference`

### 모델별 파라미터 지원

모델은 기본 API에 포함되지 않은 추가 파라미터를 가질 수 있습니다. 서비스 API와 클라이언트 SDK는 모델별 파라미터를 제공할 수 있도록 합니다. 사용자는 `temperature`, `top_p` 등의 설정과 함께 전용 인수를 통해 모델별 설정을 제공할 수 있습니다.

SK 컨텍스트에서 실행 파라미터는 `PromptExecutionSettings`로 분류되며, 모든 커넥터별 설정 클래스가 이를 상속합니다. 새 커넥터의 설정에는 모델별 파라미터를 그룹화하는 `dictionary` 타입의 멤버가 포함될 것입니다.
