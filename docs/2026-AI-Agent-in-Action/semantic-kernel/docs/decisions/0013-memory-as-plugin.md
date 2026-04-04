---
# 이 항목들은 선택 사항입니다. 필요 없는 항목은 자유롭게 제거하세요.
status: accepted
contact: dmytrostruk
date: 2023-09-21
deciders: shawncal, dmytrostruk
consulted: 
informed: 
---
# 모든 Memory 관련 로직을 별도의 플러그인으로 이동

## 배경 및 문제 상황

Memory 관련 로직이 여러 C# 프로젝트에 분산되어 있습니다:

- `SemanticKernel.Abstractions`
  - `IMemoryStore`
  - `ISemanticTextMemory`
  - `MemoryRecord`
  - `NullMemory`
- `SemanticKernel.Core`
  - `MemoryConfiguration`
  - `SemanticTextMemory`
  - `VolatileMemoryStore`
- `Plugins.Core`
  - `TextMemoryPlugin`

`ISemanticTextMemory Memory` 속성도 `Kernel` 타입의 일부이지만, 커널 자체는 이를 사용하지 않습니다. 이 속성은 플러그인에 Memory 기능을 주입하기 위해 필요합니다. 현재 `ISemanticTextMemory` 인터페이스는 `TextMemoryPlugin`의 주요 의존성이며, 일부 예제에서는 `TextMemoryPlugin`을 `new TextMemoryPlugin(kernel.Memory)`로 초기화합니다.

이 접근 방식은 Memory에는 작동하지만, 현재 다른 플러그인에 `MathPlugin`을 주입할 방법이 없습니다. 동일한 접근 방식을 따라 `Kernel` 타입에 `Math` 속성을 추가하는 것은 확장 가능한 솔루션이 아닙니다. 각 사용 가능한 플러그인마다 별도의 속성을 정의하는 것은 불가능하기 때문입니다.

## 결정 동인

1. Memory가 커널에서 사용되지 않는다면 `Kernel` 타입의 속성이 되어서는 안 됩니다.
2. Memory는 특정 플러그인에서 필요할 수 있는 다른 플러그인이나 서비스와 동일한 방식으로 취급되어야 합니다.
3. Vector DB가 연결된 Memory 기능을 등록하고 이를 필요로 하는 플러그인에 해당 기능을 주입할 수 있는 방법이 있어야 합니다.

## 결정 결과

모든 Memory 관련 로직을 `Plugins.Memory`라는 별도의 프로젝트로 이동합니다. 이를 통해 Kernel 로직을 단순화하고 Memory가 필요한 곳(다른 플러그인)에서 사용할 수 있게 됩니다.

상위 수준 작업:

1. Memory 관련 코드를 별도의 프로젝트로 이동합니다.
2. Memory를 필요로 하는 플러그인에 주입할 방법을 구현합니다.
3. `Kernel` 타입에서 `Memory` 속성을 제거합니다.
