# 용어집 ✍

커널 전반에 걸쳐 제시되는 개념을 이해하기 위한 자주 사용되는 용어 모음입니다.

**Semantic Kernel (SK)** - SK의 사용 가능한 [PLUGINS](PLUGINS.md)를 활용하여 사용자의 ASK를 수행하는 오케스트레이터입니다.

**Ask** - 사용자가 목표를 달성하기 위해 Semantic Kernel에 요청하는 것입니다.

- "SK에 ASK를 합니다"

**Plugins** - SK에서 정밀하게 조정된 함수들의 그룹으로 제공되는 도메인 특화 컬렉션입니다.

- "Office를 더 잘 사용하기 위한 PLUGIN이 있습니다"

**Function** - [PLUGIN](PLUGINS.md)에서 사용할 수 있는 시맨틱 AI 및/또는 네이티브 코드로 구성된 계산 단위입니다.

- "Office PLUGIN에는 많은 FUNCTION이 있습니다"

**Native Function** - 전통적인 프로그래밍 언어(C#, Python, Typescript)로 표현되며
SK와 쉽게 통합됩니다.

**Semantic Function** - SK의 [프롬프트 템플릿 언어](PROMPT_TEMPLATE_LANGUAGE.md)를 사용하여
텍스트 파일 "*skprompt.txt*"에 자연어로 표현됩니다.
각 시맨틱 함수는 최신 **프롬프트 엔지니어링** 기법을 활용하여 개발된
고유한 프롬프트 템플릿 파일로 정의됩니다.

**Memory** - **[임베딩](EMBEDDINGS.md)**으로 인덱싱된 사실, 이벤트, 문서 기반의 시맨틱 지식 모음입니다.

<p align="center">
<img width="682" alt="image" src="https://user-images.githubusercontent.com/371009/221690406-caaff98e-87b5-40b7-9c58-cfa9623789b5.png">
</p>

커널은 **함수 조합(function composition)**을 장려하도록 설계되어, 사용자가 여러 함수
(네이티브 및 시맨틱)를 단일 파이프라인으로 결합할 수 있습니다.

<p align="center">
<img width="682" alt="image" src="https://user-images.githubusercontent.com/371009/221690156-3f90a8c9-ef90-46f7-a097-beb483656e97.png">
</p>
