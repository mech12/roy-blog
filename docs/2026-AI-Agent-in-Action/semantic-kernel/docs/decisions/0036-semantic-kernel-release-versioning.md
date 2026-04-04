---
status: accepted
contact: markwallace
date: 2024-023-2706
deciders: sergeymenshykh, markwallace, rbarreto, dmytrostruk
consulted: matthewbolanos
informed: matthewbolanos
---

# Semantic Kernel 릴리스 버전 관리

## 배경 및 문제 설명

이 ADR은 Semantic Kernel의 새 버전을 릴리스할 때 패키지 버전 번호를 변경하는 데 사용되는 접근 방식을 요약합니다.

이 ADR은 Semantic Kernel의 .Net, Java, Python 릴리스에 관련됩니다(패키지가 v1.0에 도달한 후).

1. [NuGet의 Semantic Kernel](https://www.nuget.org/packages/Microsoft.SemanticKernel/)
1. [Python Package Index의 Semantic Kernel](https://pypi.org/project/semantic-kernel/)
1. [Maven Central의 Semantic Kernel](https://central.sonatype.com/search?q=com.microsoft.semantic-kernel)

## 결정 동인

### 시맨틱 버전 관리 및 문서화

- NuGet 패키지에서 엄격하게 따르지 않으므로 엄격한 [시맨틱 버전 관리](https://semver.org/)를 따르지 않습니다.
- 사소한 비호환 API 변경 사항은 릴리스 노트에 문서화합니다.
- Semantic Kernel의 대부분의 정기 업데이트에는 새 기능이 포함되며 하위 호환될 것으로 예상합니다.
 
### 패키지 버전 관리

- 새 릴리스를 만들 때 모든 패키지에 동일한 버전 번호를 사용합니다.
- 모든 패키지는 모든 릴리스에 포함되며, 특정 패키지가 변경되지 않았더라도 버전 번호가 증가합니다.
- 각 릴리스를 테스트하여 모든 패키지가 호환되는지 확인합니다.
- 고객에게 동일한 버전의 패키지를 사용할 것을 권장하며, 이것이 우리가 지원하는 구성입니다.

### 메이저 버전

- 영향이 적은 비호환 API 변경에 대해 MAJOR 버전을 증가시키지 않습니다 <sup>1</sup>
- 실험적 기능이나 알파 패키지에 대한 API 변경에 대해 MAJOR 버전을 증가시키지 않습니다.
  
<sup>1</sup> 영향이 적은 비호환 API 변경은 일반적으로 Semantic Kernel 내부 구현이나 단위 테스트에만 영향을 미칩니다. Semantic Kernel의 API 표면에 중요한 변경을 할 계획은 없습니다.
  
### 마이너 버전

- 하위 호환 방식으로 기능을 추가할 때 MINOR 버전을 증가시킵니다.
  
### 패치 버전

- 릴리스 시점까지 하위 호환 버그 수정만 이루어진 경우 PATCH 버전을 증가시킵니다.

### 버전 접미사

다음 버전 접미사가 사용됩니다:

- `preview` 또는 `beta` - 이 접미사는 릴리스에 가까운 패키지에 사용됩니다. 예를 들어 `1.x.x-preview` 버전은 v1.x 릴리스에 가까운 패키지에 사용됩니다. 패키지는 기능이 완성되고 인터페이스가 릴리스 버전에 매우 가깝습니다. `preview` 접미사는 .Net 릴리스에, `beta`는 Python 릴리스에 사용됩니다.
- `alpha` - 이 접미사는 기능이 완성되지 않고 공개 인터페이스가 아직 개발 중이며 변경될 것으로 예상되는 패키지에 사용됩니다.
