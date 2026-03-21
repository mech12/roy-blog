# Chapter 9: Prompt Flow를 활용한 LLM 애플리케이션 구축 및 평가

## 개요

이 챕터에서는 Microsoft의 **Prompt Flow** 프레임워크를 활용하여 LLM 기반 추천 시스템을 단계적으로 구축하는 과정을 다룬다. 단순한 프롬프트 호출에서 시작하여, 입력 매개변수화, 프롬프트 변형(variant) 실험, LLM 기반 자동 평가, 결과 파싱, 그라운딩 점수 산출, 그리고 평가 플로우 분리에 이르기까지 점진적으로 복잡성을 높여가며 실무에서 필요한 LLM 파이프라인 설계 패턴을 학습한다.

---

## 디렉토리 구조 및 파일 설명

### requirements.txt

챕터 전체에서 사용하는 Python 패키지 의존성을 정의한다. `promptflow`와 `promptflow-tools` 두 패키지를 사용한다.

### prompt_flow/

Prompt Flow 실습 예제들이 단계별로 구성된 디렉토리이다. 각 하위 디렉토리는 하나의 독립적인 플로우를 구성한다.

---

#### 1. simple_flow/ -- 기본 플로우

가장 단순한 형태의 Prompt Flow 예제이다. 사용자 입력을 받아 LLM(GPT-4)에 전달하고, 결과를 그대로 반환한다.

| 파일 | 설명 |
|------|------|
| flow.dag.yaml | 플로우의 DAG(방향성 비순환 그래프) 구조를 정의한다. `recommender`(LLM 노드)와 `echo`(Python 노드) 두 개의 노드로 구성된다. |
| recommend.jinja2 | "시간 여행 영화 전문가" 역할의 시스템 프롬프트를 정의하는 Jinja2 템플릿이다. |
| echo.py | LLM 출력을 그대로 반환하는 패스스루(passthrough) Python 도구 함수이다. |
| samples.json | 테스트용 샘플 입력 데이터이다. |
| flow.meta.yaml | 플로우 메타데이터 파일이다. |
| requirements.txt | 플로우별 패키지 의존성 파일이다. |

---

#### 2. recommender_with_inputs/ -- 매개변수화된 입력

프롬프트에 구조화된 입력 매개변수(`subject`, `genre`, `format`, `custom`)를 도입하여 다양한 추천 요청을 처리할 수 있도록 확장한 예제이다.

| 파일 | 설명 |
|------|------|
| flow.dag.yaml | 4개의 입력 매개변수(subject, genre, format, custom)를 정의하고 LLM 노드에 전달하는 플로우 구조이다. |
| recommend.jinja2 | 주제, 장르, 포맷, 사용자 커스텀 조건을 받아 3개의 추천 항목을 생성하도록 지시하는 프롬프트 템플릿이다. Jinja2 조건문(`{% if custom %}`)을 활용한다. |
| echo.py | 결과를 그대로 반환하는 Python 도구 함수이다. |
| samples.json | 테스트용 샘플 입력 데이터이다. |

---

#### 3. recommender_with_variations/ -- 프롬프트 변형 실험

동일한 플로우에서 여러 프롬프트 변형(variant)을 정의하고 비교 실험할 수 있는 구조를 보여주는 예제이다.

| 파일 | 설명 |
|------|------|
| flow.dag.yaml | `node_variants`를 사용하여 `variant_0`과 `variant_1` 두 가지 프롬프트 변형을 정의한다. `use_variants: true` 설정으로 변형 간 전환이 가능하다. |
| recommend.jinja2 | variant_0에 해당하는 범용 추천 전문가 프롬프트이다. |
| recommender_variant_1.jinja2 | variant_1에 해당하며, 특정 주제/장르의 전문가로 역할을 한정한 프롬프트이다. |
| echo.py | 결과를 그대로 반환하는 Python 도구 함수이다. |
| samples.json | 테스트용 샘플 입력 데이터이다. |

---

#### 4. recommender_with_LLM_evaluation/ -- LLM 기반 자동 평가

추천 결과를 별도의 LLM 호출로 자동 평가하는 패턴을 도입한 예제이다. 추천 노드의 출력을 평가 노드에 전달하여 주제(Subject), 포맷(Format), 장르(Genre) 기준으로 1~5점 척도의 정렬도(alignment) 점수를 매긴다.

| 파일 | 설명 |
|------|------|
| flow.dag.yaml | `recommender` -> `evaluate_recommendation` -> `echo` 순서의 3단계 파이프라인을 정의한다. 프롬프트 변형도 함께 지원한다. |
| recommend.jinja2 | variant_0 추천 프롬프트이다. |
| recommender_variant_1.jinja2 | variant_1 추천 프롬프트이다. |
| evaluate_recommendation.jinja2 | 추천 결과를 평가하는 프롬프트 템플릿이다. 주제/포맷/장르 각 기준에 대해 1~5점 척도로 평가하도록 지시한다. |
| evaluate_recommendation_variant_1.jinja2 | 평가 프롬프트의 변형 버전이다. |
| echo.py | 결과를 그대로 반환하는 Python 도구 함수이다. |
| bulk_recommend.jsonl | 다양한 주제/포맷/장르 조합의 대량 테스트 데이터(10건)이다. |
| samples.json | 테스트용 샘플 입력 데이터이다. |

---

#### 5. recommender_with_parsing/ -- 결과 파싱 추가

LLM 평가 결과를 구조화된 데이터(딕셔너리 리스트)로 파싱하는 단계를 추가한 예제이다.

| 파일 | 설명 |
|------|------|
| flow.dag.yaml | `recommender` -> `evaluate_recommendation` -> `parsing_results` 순서의 파이프라인이다. 파싱된 결과가 최종 출력이 된다. |
| parsing_results.py | LLM의 텍스트 출력을 줄바꿈 기준으로 분리하고, 각 추천 항목을 `key: value` 형태로 파싱하여 딕셔너리 리스트로 변환하는 Python 도구이다. |
| evaluate_recommendation.jinja2 | 추천 평가 프롬프트 템플릿이다. |
| evaluate_recommendation_variant_1.jinja2 | 평가 프롬프트 변형 버전이다. |
| recommend.jinja2 | variant_0 추천 프롬프트이다. |
| recommender_variant_1.jinja2 | variant_1 추천 프롬프트이다. |
| bulk_recommend.jsonl | 대량 테스트 데이터이다. |
| samples.json | 테스트용 샘플 입력 데이터이다. |

---

#### 6. recommender_with_grounding/ -- 그라운딩 점수 및 집계

파싱된 평가 결과에 대해 평균 점수(avg_score)를 계산하고, 전체 결과를 집계(aggregation)하여 메트릭으로 기록하는 단계를 추가한 예제이다.

| 파일 | 설명 |
|------|------|
| flow.dag.yaml | `recommender` -> `evaluate_recommendation` -> `parsing_results` -> `grounding` -> `aggregation` 순서의 완전한 파이프라인이다. `aggregation` 노드는 `aggregation: true`로 설정되어 모든 행의 결과를 종합한다. |
| grounding.py | 각 추천 항목의 점수들을 합산하여 평균 점수(`avg_score`)를 계산하는 Python 도구이다. |
| aggregation.py | 모든 추천 결과의 점수를 집계하고 `log_metric()`을 통해 Prompt Flow 메트릭으로 기록하는 Python 도구이다. |
| parsing_results.py | LLM 출력을 구조화된 데이터로 파싱하는 Python 도구이다. |
| evaluate_recommendation.jinja2 | 추천 평가 프롬프트 템플릿이다. |
| evaluate_recommendation_variant_1.jinja2 | 평가 프롬프트 변형 버전이다. |
| recommend.jinja2 | variant_0 추천 프롬프트이다. |
| recommender_variant_1.jinja2 | variant_1 추천 프롬프트이다. |
| bulk_recommend.jsonl | 대량 테스트 데이터이다. |
| samples.json | 테스트용 샘플 입력 데이터이다. |

---

#### 7. evaluate_groundings/ -- 독립 평가 플로우

추천 플로우와 분리된 독립적인 평가 전용 플로우이다. 다른 플로우의 출력을 입력으로 받아 행별 처리(line_process)와 전체 집계(aggregate)를 수행한다.

| 파일 | 설명 |
|------|------|
| flow.dag.yaml | `line_process` -> `aggregate` 구조의 평가 전용 플로우이다. 입력 타입이 `object`로 설정되어 구조화된 데이터를 직접 받는다. |
| line_process.py | 각 행의 추천 데이터에서 점수를 추출하고 평균 점수를 계산하는 Python 도구이다. 문자열 점수를 실수로 변환하는 안전 처리를 포함한다. |
| aggregate.py | 모든 행의 처리 결과를 종합하여 각 기준별 평균 점수를 산출하고 `log_metric()`으로 메트릭을 기록하는 Python 도구이다. |
| samples.json | 테스트용 샘플 입력 데이터이다. |

---

## 핵심 개념

### Prompt Flow 기본 구성 요소
- **flow.dag.yaml**: 플로우의 노드, 입출력, 연결 관계를 DAG로 정의하는 핵심 설정 파일
- **Jinja2 템플릿**: `system`/`user` 역할 구분과 변수 바인딩을 지원하는 프롬프트 정의 방식
- **Python 도구(@tool 데코레이터)**: 데이터 전처리, 후처리, 변환 등을 수행하는 커스텀 노드

### 점진적 파이프라인 설계
- 단순 입출력에서 시작하여 매개변수화, 변형 실험, 자동 평가, 파싱, 그라운딩, 집계 단계를 점진적으로 추가하는 설계 방법론

### 프롬프트 변형(Variant) 관리
- `node_variants`와 `use_variants` 설정을 통해 동일 노드에서 여러 프롬프트를 정의하고 A/B 테스트 방식으로 비교 실험하는 기법

### LLM-as-a-Judge 패턴
- LLM 출력을 다른 LLM 호출로 평가하는 자동 평가 패턴. 주제, 포맷, 장르 기준의 정렬도(alignment)를 1~5점 척도로 측정

### 결과 파싱 및 구조화
- LLM의 비정형 텍스트 출력을 프로그래밍적으로 파싱하여 딕셔너리/리스트 형태의 구조화된 데이터로 변환

### 그라운딩 및 메트릭 집계
- 개별 항목의 점수를 평균 내어 그라운딩 점수를 산출하고, `log_metric()`을 통해 Prompt Flow 대시보드에서 추적 가능한 메트릭으로 기록

### 대량 실행(Batch Run)
- JSONL 형식의 데이터 파일(`bulk_recommend.jsonl`)을 사용하여 다양한 입력 조합에 대해 플로우를 일괄 실행하고 결과를 비교

---

## 학습 교훈

1. **작게 시작하고 점진적으로 확장하라.** simple_flow에서 시작하여 단계별로 기능을 추가하는 접근 방식은 각 구성 요소의 역할을 명확히 이해하게 해준다. 처음부터 복잡한 파이프라인을 설계하려 하면 디버깅이 어려워진다.

2. **프롬프트는 반드시 실험하고 비교하라.** 프롬프트의 미세한 차이(범용 전문가 vs. 특정 분야 전문가)가 출력 품질에 큰 영향을 미친다. Prompt Flow의 변형(variant) 기능을 활용하면 체계적인 A/B 테스트가 가능하다.

3. **LLM 출력은 반드시 평가하라.** LLM의 추천이 실제로 요청 기준에 부합하는지 자동으로 검증하는 단계가 필수적이다. LLM-as-a-Judge 패턴은 수동 평가의 부담을 크게 줄여준다.

4. **비정형 출력의 구조화는 별도 단계로 분리하라.** LLM이 생성한 텍스트를 그대로 사용하지 말고, 파싱 단계를 두어 구조화된 데이터로 변환해야 후속 처리(점수 계산, 집계 등)가 안정적으로 이루어진다.

5. **평가 로직은 독립된 플로우로 분리하라.** evaluate_groundings 예제처럼 평가 플로우를 추천 플로우와 분리하면 재사용성이 높아지고, 다른 플로우의 결과에 대해서도 동일한 평가 기준을 적용할 수 있다.

6. **메트릭을 체계적으로 기록하라.** `log_metric()`을 활용한 정량적 메트릭 기록은 프롬프트 변형 간 비교, 시간에 따른 품질 추적, 회귀 감지 등 운영 수준의 LLM 관리에 필수적이다.

7. **대량 테스트 데이터를 준비하라.** 단일 입력이 아닌 다양한 조합(주제, 장르, 포맷)의 대량 데이터로 테스트해야 프롬프트의 일반화 성능과 엣지 케이스를 확인할 수 있다.
