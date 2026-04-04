---
status: proposed
contact: rogerbarreto
date: 2025-03-07
deciders: rogerbarreto, markwallace, dmytrostruk, westey-m, sergeymenshykh
---

# Semantic Kernel의 구조화된 데이터 플러그인 구현

## 맥락과 문제 설명

현대 AI 애플리케이션은 LLM 기능을 활용하면서 데이터베이스의 구조화된 데이터와 상호작용해야 하는 경우가 많습니다. Semantic Kernel의 핵심이 AI 오케스트레이션에 초점을 맞추고 있으므로, 데이터베이스 작업과 AI 기능을 통합하기 위한 표준화된 접근 방식이 필요합니다. 이 ADR은 기본 CRUD 작업과 간단한 쿼리에 초점을 맞춘 데이터베이스-AI 통합을 위한 초기 솔루션으로 실험적 StructuredDataConnector를 제안합니다.

## 결정 동인

- SK와의 초기 데이터베이스 통합 패턴 필요
- 기본적인 조합 가능한 AI 및 데이터베이스 작업 요구사항
- SK의 플러그인 아키텍처와의 정렬
- 실제 사용을 통한 접근 방식 검증 능력
- 강타입 스키마 검증 지원
- AI 상호작용을 위한 일관된 JSON 포맷팅

## 주요 이점

1. **플러그인 기반 아키텍처**

   - SK의 플러그인 아키텍처와 정렬
   - 일반 작업을 위한 확장 메서드 지원
   - 타입 안전성을 위한 KernelJsonSchema 활용

2. **구조화된 데이터 작업**

   - 스키마 검증을 포함한 CRUD 작업
   - 적절한 포맷팅을 갖춘 JSON 기반 상호작용
   - 타입 안전한 데이터베이스 작업

3. **통합 기능**

   - 내장 JSON 스키마 생성
   - 자동 타입 변환
   - 더 나은 AI 상호작용을 위한 정리된 JSON 출력

## 구현 세부사항

구현에는 다음이 포함됩니다:

1. 핵심 컴포넌트:

   - `StructuredDataService<TContext>`: 데이터베이스 작업을 위한 기본 서비스
   - `StructuredDataServiceExtensions`: CRUD 작업을 위한 확장 메서드
   - `StructuredDataPluginFactory`: SK 플러그인 생성을 위한 팩토리
   - 타입 검증을 위한 `KernelJsonSchema` 통합

2. 주요 기능:

   - 엔티티 타입으로부터의 자동 스키마 생성
   - 적절히 포맷된 JSON 응답
   - 유지보수성을 위한 확장 기반 아키텍처
   - Entity Framework Core 지원

3. 사용 예시:

```csharp
var service = new StructuredDataService<ApplicationDbContext>(dbContext);
var plugin = StructuredDataPluginFactory.CreateStructuredDataPlugin<ApplicationDbContext, MyEntity>(
    service,
    operations: StructuredDataOperation.Default);
```

## 결정 결과

선택한 옵션: TBD:

1. 표준화된 데이터베이스 통합 제공
2. SK의 스키마 검증 기능 활용
3. AI 상호작용을 위한 적절한 JSON 포맷팅 지원
4. 생성된 스키마를 통한 타입 안전성 유지
5. 확립된 SK 패턴과 원칙 준수

## 추가 정보

이것은 커뮤니티 피드백을 기반으로 발전할 실험적 접근 방식입니다.
