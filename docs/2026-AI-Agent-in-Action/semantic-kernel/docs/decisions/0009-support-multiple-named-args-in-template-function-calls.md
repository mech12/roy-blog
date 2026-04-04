---
# 이 항목들은 선택 사항입니다. 필요 없는 항목은 자유롭게 제거하세요.
status: accepted
contact: dmytrostruk
date: 2013-06-16
deciders: shawncal, hario90
consulted: dmytrostruk, matthewbolanos
informed: lemillermicrosoft
---

# 템플릿 함수 호출에서 다중 명명된 인수 지원 추가

## 배경 및 문제 상황

네이티브 함수는 이제 동일한 이름의 컨텍스트 값에서 채워지는 다중 매개변수를 지원합니다. 시맨틱 함수는 현재 1개 이하의 인수로만 네이티브 함수를 호출할 수 있습니다. 이 변경의 목적은 시맨틱 함수 내에서 다중 명명된 인수로 네이티브 함수를 호출하는 기능을 추가하는 것입니다.

## 결정 동인

- Guidance와의 동등성
- 가독성
- SK 개발자에게 익숙한 언어와의 유사성
- YAML 호환성

## 검토된 옵션

### 구문 아이디어 1: 쉼표 사용

```handlebars
{{Skill.MyFunction street: "123 Main St", zip: "98123", city:"Seattle", age: 25}}
```

장점:

- 쉼표를 사용하면 긴 함수 호출을 더 쉽게 읽을 수 있으며, 특히 인수 구분자(이 경우 콜론) 앞뒤의 공백이 허용되는 경우 더욱 그렇습니다.

단점:

- Guidance는 쉼표를 사용하지 않습니다.
- 공백이 이미 다른 곳에서 구분자로 사용되므로 쉼표를 지원하는 추가 복잡성은 불필요합니다.

### 구문 아이디어 2: JavaScript/C# 스타일 구분자 (콜론)

```handlebars

{{MyFunction street:"123 Main St" zip:"98123" city:"Seattle" age: "25"}}

```

장점:

- JavaScript 객체 구문 및 C# 명명된 인수 구문과 유사합니다.

단점:

- 등호를 인수 부분 구분자로 사용하는 Guidance 구문과 맞지 않습니다.
- 향후 YAML 프롬프트를 지원하는 경우 YAML 키/값 쌍과 너무 유사합니다. 콜론을 구분자로 지원하는 것이 가능할 수 있지만 일반 YAML 구문과 구별되는 구분자가 더 좋습니다.

### 구문 아이디어 3: Python/Guidance 스타일 구분자

```handlebars
{{MyFunction street="123 Main St" zip="98123" city="Seattle"}}
```

장점:

- Python의 키워드 인수 구문과 유사합니다.
- Guidance의 명명된 인수 구문과 유사합니다.
- 향후 YAML 프롬프트를 지원하는 경우 YAML 키/값 쌍과 너무 유사하지 않습니다.

단점:

- C# 구문과 맞지 않습니다.

### 구문 아이디어 4: 인수 이름/값 구분자 사이의 공백 허용

```handlebars
{{MyFunction street="123 Main St" zip="98123" city="Seattle"}}
```

장점:

- 공백, 탭, 줄바꿈이 프로그램 기능에 영향을 주지 않는 많은 프로그래밍 언어의 공백 유연성 규칙을 따릅니다.

단점:

- 쉼표를 사용할 수 없는 경우 가독성이 떨어지는 코드를 조장합니다([쉼표 사용](#구문-아이디어-1-쉼표-사용) 참조)
- 지원을 위한 복잡성이 증가합니다.
- = 기호 앞뒤의 공백을 지원하지 않는 Guidance와 맞지 않습니다.

## 결정 결과

선택된 옵션: "구문 아이디어 3: Python/Guidance 스타일 키워드 인수", Guidance의 구문과 잘 맞으며 YAML과 가장 호환되기 때문입니다. 그리고 "구문 아이디어 4: 인수 이름/값 구분자 사이의 공백 허용"은 더 유연한 개발자 경험을 위해 선택되었습니다.

추가 결정 사항:

- 하위 호환성을 위해 최대 1개의 위치 인수를 계속 지원합니다. 현재 함수에 전달되는 인수는 `$input` 컨텍스트 변수로 가정됩니다.

예제

```handlebars
{{MyFunction "inputVal" street="123 Main St" zip="98123" city="Seattle"}}
```

- 인수 값을 문자열 또는 변수로만 정의할 수 있도록 허용합니다. 예:

```handlebars
{{MyFunction street=$street zip="98123" city="Seattle"}}
```

함수가 인수에 대해 문자열이 아닌 값을 기대하는 경우, SDK는 표현식을 평가할 때 해당 TypeConverter를 사용하여 제공된 문자열을 파싱합니다.
