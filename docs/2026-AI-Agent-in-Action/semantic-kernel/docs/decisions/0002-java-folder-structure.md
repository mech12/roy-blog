---
# 이 항목들은 선택 사항입니다. 필요 없는 항목은 자유롭게 제거하세요.
status: accepted
date: 2013-06-19
deciders: shawncal,johnoliver
consulted: 
informed:
---
# Java 폴더 구조

## 배경 및 문제 상황

Semantic Kernel의 Java 포팅이 `experimental-java` 브랜치에서 개발 중입니다. 사용 중인 폴더 구조가 .Net 구현과 달라졌습니다.
이 ADR의 목적은 Java 포팅에서 사용할 폴더 구조를 문서화하여 개발자들이 .Net과 Java 구현 간을 쉽게 탐색할 수 있도록 하는 것입니다.

## 결정 동인

* 이미 우수한 다국어 지원을 갖춘 SDK에서 배우는 것이 목표입니다. 예: [Azure SDK](https://github.com/Azure/azure-sdk/)
* Java SK는 Java의 일반적인 설계 가이드라인과 관례를 따라야 합니다. Java 개발자에게 자연스러워야 합니다.
* 다른 언어 버전은 .Net 구현과 일관성을 유지해야 합니다. 충돌이 발생할 경우 Java 관례와의 일관성이 최우선입니다.
* Java와 .Net용 SK는 단일 팀이 개발한 하나의 제품처럼 느껴져야 합니다.
* Java와 .Net 간에 기능 동등성이 있어야 합니다. 기능 상태는 [FEATURE_MATRIX](../../FEATURE_MATRIX.md)에서 추적해야 합니다.

## 검토된 옵션

다음은 .Net과 Java 폴더 구조의 비교입니다.

```bash
dotnet/src
           Connectors
           Extensions
           IntegrationTests
           InternalUtilities
           SemanticKernel.Abstractions
           SemanticKernel.MetaPackage
           SemanticKernel.UnitTests
           SemanticKernel
           Skills
```

| 폴더                           | 설명 |
|--------------------------------|------|
| Connectors                     | 다양한 Connector 구현의 상위 폴더. 예: AI 또는 Memory 서비스 |
| Extensions                     | SK 확장의 상위 폴더. 예: planner 구현 |
| IntegrationTests               | 통합 테스트 |
| InternalUtilities              | 내부 유틸리티, 즉 공유 코드 |
| SemanticKernel.Abstractions    | SK API 정의 |
| SemanticKernel.MetaPackage     | SK 공통 패키지 모음 |
| SemanticKernel.UnitTests       | 단위 테스트 |
| SemanticKernel                 | SK 구현 |
| Skills                         | 다양한 Skills 구현의 상위 폴더. 예: Core, MS Graph, GRPC, OpenAI, ... |

몇 가지 관찰 사항:

* `src` 폴더가 폴더 구조의 맨 앞에 위치하여 유연성이 줄어듭니다.
* `Skills` 용어는 변경 예정입니다.

```bash
java
     api-test
     samples
     semantickernel-api
     semantickernel-bom
     semantickernel-connectors-parent
     semantickernel-core-skills
     semantickernel-core
     semantickernel-extensions-parent
```

| 폴더                                | 설명 |
|-------------------------------------|------|
| `api-test`                          | 통합 테스트 및 API 사용 예제 |
| `samples`                           | SK 샘플 |
| `semantickernel-api`                | SK API 정의 |
| `semantickernel-bom`                | SK Bill Of Materials |
| `semantickernel-connectors-parent`  | 다양한 Connector 구현의 상위 폴더 |
| `semantickernel-core-skills`        | SK 핵심 스킬 (.Net에서는 핵심 구현의 일부) |
| `semantickernel-core`               | SK 핵심 구현 |
| `semantickernel-extensions-parent`  | SK 확장의 상위 폴더. 예: planner 구현 |

몇 가지 관찰 사항:

* `-` 구분자를 사용한 소문자 폴더명은 Java의 관례적 표기법입니다.
* `src` 폴더는 소스 파일에 최대한 가까이 위치합니다. 예: `semantickernel-api/src/main/java`, 이는 Java의 관례적 표기법입니다.
* 단위 테스트는 구현과 함께 포함됩니다.
* 샘플은 `java` 폴더 내에 위치하며 각 샘플은 독립적으로 실행됩니다.

## 결정 결과

다음 가이드라인을 따릅니다:

* 폴더명은 .Net에서 사용하는(또는 예정된) 이름과 일치하되, Java의 관례적 폴더 명명 규칙을 따릅니다.
* .Net 중심적인 `MetaPackage` 대신 `bom`을 사용합니다.
* .Net 중심적인 `Abstractions` 대신 `api`를 사용합니다.
* `semantickernel-core-skills`를 새로운 `plugins` 폴더로 이동하고 `plugins-core`로 이름을 변경합니다.
* `skills` 대신 `plugins` 용어를 사용하고 기술 부채 발생을 방지합니다.

| 폴더                             | 설명 |
|----------------------------------|------|
| `connectors`                     | 포함: `semantickernel-connectors-ai-openai`, `semantickernel-connectors-ai-huggingface`, `semantickernel-connectors-memory-qadrant`, ...  |
| `extensions`                     | 포함: `semantickernel-planning-action-planner`, `semantickernel-planning-sequential-planner` |
| `integration-tests`              | 통합 테스트 |
| `semantickernel-api`             | SK API 정의 |
| `semantickernel-bom`             | SK 공통 패키지 모음 |
| `semantickernel-core`            | SK 핵심 구현 |
| `plugins`                        | 포함: `semantickernel-plugins-core`, `semantickernel-plugins-document`, `semantickernel-plugins-msgraph`, ... |
