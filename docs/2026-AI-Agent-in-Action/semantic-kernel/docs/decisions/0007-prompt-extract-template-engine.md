---
# 이 항목들은 선택 사항입니다. 필요 없는 항목은 자유롭게 제거하세요.
status: accepted
contact: markwallace-microsoft
date: 2023-08-25
deciders: shawncal
consulted: 
informed: 
---
# Semantic Kernel 코어에서 프롬프트 템플릿 엔진 추출

## 배경 및 문제 상황

Semantic Kernel에는 Semantic Kernel 프롬프트, 즉 `skprompt.txt` 파일을 렌더링하는 데 사용되는 기본 프롬프트 템플릿 엔진이 포함되어 있습니다. 프롬프트 템플릿은 AI에 전송되기 전에 렌더링되어 프롬프트를 동적으로 생성할 수 있게 합니다. 예를 들어 입력 매개변수나 네이티브 또는 시맨틱 함수 실행 결과를 포함할 수 있습니다.
Semantic Kernel의 복잡성과 API 표면을 줄이기 위해 프롬프트 템플릿 엔진을 추출하여 별도의 패키지로 분리할 예정입니다.

장기 목표는 다음 시나리오를 가능하게 하는 것입니다:

1. 사용자 정의 템플릿 엔진을 구현합니다. 예: Handlebars 템플릿 사용. 현재 지원되지만 구현할 API를 단순화하고자 합니다.
2. 0개 또는 여러 개의 템플릿 엔진 사용을 지원합니다.

## 결정 동인

* Semantic Kernel 코어의 API 표면과 복잡성을 줄입니다.
* `IPromptTemplateEngine` 인터페이스를 단순화하여 사용자 정의 템플릿 엔진을 더 쉽게 구현할 수 있게 합니다.
* 기존 클라이언트를 깨뜨리지 않고 변경합니다.

## 결정 결과

* `Microsoft.SemanticKernel.TemplateEngine`이라는 새 패키지를 생성합니다.
* 모든 프롬프트 템플릿 엔진 코드의 기존 네임스페이스를 유지합니다.
* `IPromptTemplateEngine` 인터페이스를 `RenderAsync` 구현만 요구하도록 단순화합니다.
* `Microsoft.SemanticKernel.TemplateEngine` 어셈블리가 사용 가능한 경우 기존 `PromptTemplateEngine`을 동적으로 로드합니다.
