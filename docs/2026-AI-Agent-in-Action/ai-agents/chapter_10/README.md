# Chapter 10: 프롬프트 엔지니어링과 Q-Learning 기반 에이전트

## 개요

이 챕터에서는 다양한 프롬프트 엔지니어링 기법을 Azure Prompt Flow를 활용하여 실습하고, Q-Learning 개념을 LLM 에이전트에 접목한 시맨틱 메모리 기반 에이전트를 구현한다. 프롬프트 설계 방식에 따라 LLM의 추론 품질이 크게 달라진다는 점을 실험적으로 확인하며, 강화학습의 Q-값 개념을 에이전트의 행동 선택에 적용하는 방법을 다룬다.

---

## 파일 구조 및 설명

### 루트 파일

| 파일 | 설명 |
|------|------|
| `q_agent.py` | Q-Learning과 시맨틱 메모리를 결합한 LLM 에이전트 구현체. 코사인 유사도 기반으로 유사 상태를 검색하고, 과거 경험(상태, 행동, Q-값)을 활용하여 쿼리에 대한 최적 행동을 선택한다. |
| `requirements.txt` | 프로젝트 의존성 패키지 목록 (promptflow, scipy, langchain, semantic-kernel, chromadb 등) |

### prompt_flow/ 디렉토리

Prompt Flow를 활용한 다양한 프롬프트 엔지니어링 기법의 실습 예제 모음이다. 각 하위 디렉토리는 하나의 프롬프트 기법을 독립된 플로우로 구현하며, `flow.dag.yaml`로 파이프라인을 정의하고 Jinja2 템플릿으로 프롬프트를 작성한다.

| 디렉토리 | 프롬프트 기법 | 설명 |
|----------|-------------|------|
| `zero-shot-prompting/` | Zero-Shot | 예시 없이 직접 지시만으로 텍스트 감성 분류를 수행한다. |
| `few-shot-prompting/` | Few-Shot | 몇 가지 예시를 제공하여 모델이 패턴을 학습하도록 유도한다. 가상의 단어를 사용한 문장 생성 과제를 다룬다. |
| `zero-shot-cot-prompting/` | Zero-Shot CoT | "단계별로 생각하라"는 지시를 추가하여 별도의 예시 없이 연쇄적 추론을 유도한다. |
| `chain-of-thought-prompting/` | Chain-of-Thought (CoT) | 시간 여행 시나리오 문제를 활용하여 단계별 추론 과정을 명시적으로 보여주는 예시를 제공한다. 평가 노드가 포함되어 예측 결과를 자동으로 검증한다. |
| `reasoning-prompting/` | Reasoning | 문제를 단계별로 분해하여 풀도록 지시하되 최종 답만 반환하는 방식이다. 변형(variant) 프롬프트도 포함되어 있다. |
| `prompt-chaining/` | Prompt Chaining | 문제를 분해(decompose) -> 단계별 계산(calculate_steps) -> 최종 해답 도출(calculate_solution)의 3단계 체인으로 구성한다. |
| `self-consistancy-prompting/` | Self-Consistency | 동일 문제에 대해 여러 번 독립적으로 답을 생성한 뒤 일관성을 평가한다. |
| `self-consistency-evaluation/` | Self-Consistency 평가 | 코사인 유사도 기반으로 여러 응답의 임베딩을 비교하여 가장 일관된 답변을 선택하는 평가 파이프라인이다. |
| `tree-of-thoughts/` | Tree of Thoughts (ToT) | 3명의 가상 전문가가 각각 독립적으로 문제를 분해하고, 단계별로 사고하며, 최종 답을 도출하는 트리 구조의 추론을 수행한다. Semantic Kernel을 활용한다. |
| `tree-of-thoughts_evaluation/` | ToT 평가 | Tree of Thoughts 결과에 대한 평가 파이프라인이다. |
| `question-answer-prompting/` | Question-Answer | 단순 질의응답 형태의 기본 프롬프트 구조를 구현한다. |

### 각 플로우의 공통 파일 구성

- `flow.dag.yaml` -- Prompt Flow DAG 정의 파일. 노드 간 의존 관계와 LLM 연결 설정을 포함한다.
- `*.jinja2` -- Jinja2 프롬프트 템플릿. 시스템 프롬프트와 사용자 입력 변수를 정의한다.
- `evaluate.py` -- 코사인 유사도 기반 평가 함수. `@tool` 데코레이터로 Prompt Flow 도구로 등록된다.
- `samples.json` -- 테스트용 샘플 데이터.
- `requirements.txt` -- 플로우별 의존성 정의.

---

## 핵심 개념

### 1. 프롬프트 엔지니어링 기법의 스펙트럼

가장 단순한 Zero-Shot부터 가장 정교한 Tree of Thoughts까지 점진적으로 복잡해지는 프롬프트 기법을 체계적으로 비교한다.

- **Zero-Shot / Few-Shot**: 예시의 유무에 따른 성능 차이
- **Chain-of-Thought**: 중간 추론 과정을 명시적으로 유도
- **Self-Consistency**: 다수의 독립적 추론 결과에서 가장 일관된 답을 선택
- **Tree of Thoughts**: 여러 전문가 관점에서 병렬적으로 사고한 뒤 종합

### 2. Q-Learning 기반 에이전트 (q_agent.py)

강화학습의 Q-Learning 개념을 LLM 에이전트에 적용한 구조이다.

- **SemanticMemory**: 상태 임베딩, 행동, Q-값을 저장하는 시맨틱 메모리. 코사인 유사도로 유사 상태를 검색한다.
- **QLearningModel**: 쿼리를 임베딩하고, 유사한 과거 경험의 행동으로 쿼리를 보강(annotate)한 뒤, LLM에 전달하여 행동을 생성하고, 그 행동의 품질을 Q-값으로 평가하여 메모리에 저장한다.
- 핵심 흐름: 쿼리 임베딩 -> 유사 상태 검색 -> 쿼리 보강 -> LLM 응답 -> Q-값 평가 -> 메모리 갱신

### 3. Prompt Flow 파이프라인

Azure Prompt Flow를 활용하여 프롬프트 기법을 DAG(Directed Acyclic Graph) 형태의 파이프라인으로 구성한다. 각 노드는 LLM 호출 또는 Python 도구이며, 노드 간 데이터 흐름이 YAML로 선언적으로 정의된다.

### 4. Semantic Kernel 통합

Tree of Thoughts 구현에서 Microsoft Semantic Kernel을 활용하여 시맨틱 함수를 정의하고 비동기적으로 실행한다. OpenAI와 Azure OpenAI 양쪽 연결을 모두 지원한다.

---

## 학습 교훈

1. **프롬프트 설계가 곧 성능이다**: 동일한 LLM이라도 프롬프트 구조에 따라 추론 품질이 극적으로 달라진다. Zero-Shot으로 풀기 어려운 복잡한 추론 문제도 Chain-of-Thought나 Tree of Thoughts 기법을 적용하면 정확도가 크게 향상된다.

2. **단계적 추론의 중요성**: 복잡한 문제를 한 번에 풀도록 요청하는 것보다, 분해 -> 단계별 계산 -> 종합의 체인으로 나누는 것이 훨씬 효과적이다. Prompt Chaining은 이를 파이프라인 수준에서 구조화한다.

3. **다양성과 일관성의 균형**: Self-Consistency 기법은 temperature를 높여 다양한 답변을 생성한 뒤, 임베딩 기반 유사도로 가장 대표적인 답변을 선택한다. 단일 응답에 의존하는 것보다 신뢰도가 높다.

4. **경험 기반 학습의 가능성**: Q-Learning 에이전트는 과거 쿼리-행동-보상 이력을 시맨틱 메모리에 축적하여, 유사한 새로운 상황에서 더 나은 행동을 선택할 수 있다. 이는 LLM의 정적인 지식을 동적 경험으로 보완하는 접근법이다.

5. **평가 자동화가 필수적이다**: 프롬프트 기법의 효과를 객관적으로 비교하려면 자동화된 평가 파이프라인이 필요하다. 이 챕터에서는 코사인 유사도와 LLM 기반 평가를 조합하여 예측 결과를 자동으로 검증한다.

6. **도구와 프레임워크의 조합**: Prompt Flow(파이프라인 오케스트레이션), Semantic Kernel(시맨틱 함수 실행), LangChain(체인 구성), ChromaDB(벡터 저장소) 등 다양한 도구를 목적에 맞게 조합하는 것이 실무에서 중요하다.
