# Semantic Kernel Python Hello World Starter

The `sk-python-hello-world` console application demonstrates how to execute a semantic function.

## Prerequisites

- [Python](https://www.python.org/downloads/) 3.8 and above
  - [Poetry](https://python-poetry.org/) is used for packaging and dependency management
  - [Semantic Kernel Tools](https://marketplace.visualstudio.com/items?itemName=ms-semantic-kernel.semantic-kernel)

## Configuring the starter

The starter can be configured with a `.env` file in the project which holds api keys and other secrets and configurations.

Make sure you have an
[Open AI API Key](https://openai.com/api/) or
[Azure Open AI service key](https://learn.microsoft.com/azure/cognitive-services/openai/quickstart?pivots=rest-api)

Copy the `.env.example` file to a new file named `.env`. Then, copy those keys into the `.env` file:

```
OPENAI_API_KEY=""
OPENAI_ORG_ID=""
AZURE_OPENAI_DEPLOYMENT_NAME=""
AZURE_OPENAI_ENDPOINT=""
AZURE_OPENAI_API_KEY=""
```

## Running the starter

To run the console application within Visual Studio Code, just hit `F5`.
As configured in `launch.json` and `tasks.json`, Visual Studio Code will run `poetry install` followed by `python hello_world/main.py`

To build and run the console application from the terminal use the following commands:


포이트리 설치하기 

2018 년 등장 자바의 maven 이나 gradle의 역할 
버전관리를 알아서 해준다 

1. 버전 충돌 방지: AI 분야는 라이브러리 업데이트 속도가 굉장히 빠릅니다. 
pip만 쓰면 오늘 되던 코드가 내일 안 되는 일이 허다하지만,  Poetry는 출시 당시부터 도입된 poetry.lock 시스템으로 "어제 돌린 환경 그대로" 복제해 줍니다.

2. 프로젝트 격리: 30년 전 자바 환경 설정할 때 클래스패스(Classpath) 꼬이는 것과 비슷하게, 파이썬도 전역(Global)에 깔면 난리가 납니다. Poetry는 프로젝트 폴더마다 **독립된 방(가상환경)**을 아주 깔끔하게 만들어줍니다.


. 왜 "자기만의 가상환경"을 만드는 게 정석인가요? (강사님 의견)
Poetry의 가장 큰 장점은 프로젝트마다 완전히 격리된 방을 만드는 것입니다.

파이썬 버전 고정 가능: 시스템에 3.13이 깔려 있어도, 이 프로젝트는 반드시 3.11로 돌리겠다고 선언하면 Poetry가 해당 버전을 찾아 가상환경을 구축합니다. (단, 해당 버전의 파이썬이 시스템 어딘가에는 설치되어 있어야 합니다.)

깔끔한 삭제: 프로젝트가 끝나면 해당 폴더의 가상환경만 지우면 끝입니다. base나 다른 환경에 찌꺼기가 남지 않습니다.

독립성: A 프로젝트는 numpy 1.0, B 프로젝트는 numpy 2.0을 써도 서로 절대 간섭하지 않습니다.

2. 그럼 왜 아까는 "Conda에 합치라"고 했나요?
강사님이 현재 **Conda(3.13)**를 이미 활성화해서 쓰고 계셨기 때문입니다.

충돌 방지: Conda 자체가 이미 하나의 가상환경입니다. "가상환경(Conda) 안에 또 가상환경(Poetry)"을 만들면 윈도우 경로(PATH)가 꼬여서 python 명령어를 쳤을 때 어느 방의 파이썬이 실행될지 컴퓨터가 헷갈려 합니다.

편의성: 이미 구축된 autogen_env가 있다면, 굳이 또 새 방을 만들지 않고 그 방의 자원(파이썬 3.13)을 Poetry가 '관리'만 하게 하는 것이 에러를 줄이는 지름길이었기 때문입니다.


Conda를 완전히 끕니다. (가장 중요!)

PowerShell
conda deactivate
# 프롬프트 앞에 (base)나 (autogen_env)가 완전히 사라질 때까지!
Poetry 설정을 초기화합니다. (다시 새 방을 만들도록)

PowerShell
poetry config virtualenvs.create true
poetry config virtualenvs.prefer-active-python false
원하는 파이썬 버전을 지정합니다. (내 컴퓨터에 깔린 3.11 등을 쓸 때)

PowerShell
poetry env use python3.11 
# 만약 3.13을 쓰고 싶다면 poetry env use python3.13
설치 및 실행

PowerShell
poetry install
poetry run python hello_world/main.py

rm poetry.lock
poetry env remove --all
poetry install 

poetry run python -c "import semantic_kernel; print(semantic_kernel.__version__)"

설치방법 
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -

```powershell
poetry install
poetry run python hello_world/main.py
```


