---
# 선택적 요소입니다. 필요 없는 항목은 자유롭게 제거하세요.
status: accepted
contact: markwallace-microsoft
date: 2024-03-14
deciders: sergeymenshykh, markwallace, rbarreto, dmytrostruk
consulted: 
informed: 
---

# 완성 서비스 선택 전략

## 배경 및 문제 설명

현재 SK는 텍스트 프롬프트를 실행할 때 사용되는 서비스 유형을 결정하기 위해 현재의 `IAIServiceSelector` 구현을 사용합니다.
`IAIServiceSelector` 구현은 채팅 완성 서비스, 텍스트 생성 서비스 또는 둘 다 구현하는 서비스를 반환할 수 있습니다.
프롬프트는 기본적으로 채팅 완성을 사용하여 실행되며, 대체 옵션으로 텍스트 생성으로 폴백합니다.

이 동작은 [ADR-0015](0015-completion-service-selection.md)에 설명된 내용을 대체합니다.

## 결정 동인

- 채팅 완성 서비스가 업계에서 지배적이 되고 있습니다. 예를 들어 OpenAI는 대부분의 텍스트 생성 서비스를 폐기했습니다.
- 채팅 완성은 일반적으로 더 나은 응답과 도구 호출과 같은 고급 기능 사용 능력을 제공합니다.

## 결정 결과

선택된 옵션: 위에서 설명한 현재 동작을 유지합니다.
