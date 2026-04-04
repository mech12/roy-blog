# 아키텍처 결정 기록 (ADR)

아키텍처 결정(AD)은 아키텍처적으로 중요한 기능적 또는 비기능적 요구사항을 다루는 정당화된 소프트웨어 설계 선택입니다. 아키텍처 결정 기록(ADR)은 단일 AD와 그 근거를 기록합니다.

자세한 내용은 [여기](https://adr.github.io/)를 참조하세요.

## ADR을 사용하여 기술 결정을 추적하는 방법

1. docs/decisions/adr-template.md를 docs/decisions/NNNN-title-with-dashes.md로 복사합니다. 여기서 NNNN은 순서상 다음 번호를 나타냅니다.
    1. 올바른 순번을 사용하고 있는지 기존 PR을 확인하세요.
    2. 간략한 형식의 템플릿 docs/decisions/adr-short-template.md도 있습니다.
2. NNNN-title-with-dashes.md를 편집합니다.
    1. 상태는 처음에 `proposed`여야 합니다.
    2. `deciders` 목록에는 결정을 승인할 사람들의 github ID가 포함되어야 합니다.
    3. 관련 EM과 아키텍트는 모든 결정의 deciders로 포함되거나 통보(informed)되어야 합니다.
    4. 결정 과정에서 자문한 모든 파트너의 이름 또는 github ID를 나열해야 합니다.
    5. `deciders` 목록은 짧게 유지하세요. 결정에 대해 `consulted`(자문)하거나 `informed`(통보)한 사람을 나열할 수도 있습니다.
3. 각 옵션에 대해 검토한 각 대안의 좋은 점, 중립적인 점, 나쁜 점을 나열합니다.
    1. 상세한 조사 내용은 `More Information` 섹션에 인라인으로 포함하거나 외부 문서 링크로 포함할 수 있습니다.
4. PR을 deciders 및 기타 관계자와 공유합니다.
   1. Deciders는 필수 리뷰어로 등록되어야 합니다.
   2. 결정이 합의되면 상태를 `accepted`로 업데이트해야 하며, 날짜도 함께 업데이트해야 합니다.
   3. 결정의 승인은 PR 승인을 통해 기록됩니다.
5. 결정은 나중에 변경될 수 있으며 새로운 ADR로 대체될 수 있습니다. 이 경우 원본 ADR에 부정적인 결과를 기록하는 것이 유용합니다.
