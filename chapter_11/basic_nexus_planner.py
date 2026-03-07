# 이 파일은 번역서 AI 에이전트 인 액션의 예제 11.3~11.5의 코드를 모은 것입니다. 
# 실제로 작동하는 코드는 아니고, 단지 예시로서만 제공됩니다.
# 원서 깃허브 저장소(https://github.com/cxbxmxcx/GPT-Agents)와 Nexus 프로젝트 저장소
# (https://github.com/cxbxmxcx/Nexus) 둘 다 아직 11장에 맞게 갱신이 되지 않은 
# 상태로 보입니다. (번역서 p. 314의 옮긴이 주석 참고.)

### 예제 11.3

PROMPT = """
당신은 넥서스(Nexus)를 위한 플래너입니다. #1
당신의 임무는 주어진 목표를 만족시키기 위해 단계별로 적절한 형식의 JSON 계획을 생성하는 것입니다.
[GOAL]에 기반하여 하위 작업(subtask)들의 목록을 생성하세요.
각 하위 작업은 반드시 [AVAILABLE FUNCTIONS] 목록 안에 있는 함수여야 합니다. 목록에 없는 함수는 사용하지 마세요.
어떤 함수를 사용할지는 함수의 설명과 이름에 근거하여 결정하세요.
필요한 경우, 함수에 인수(argument)들을 제공하세요.
계획은 가능한 한 짧게 작성하세요.
결정을 돕기 위해 이전 계획들에 대한 수정, 제안, 지식 피드백 목록이 제공될 수 있습니다.

예시:
[SPECIAL FUNCTIONS]     #2
for-each- prefix
설명: 목록의 각 항목에 대해 함수를 실행한다.
args:
- function: 실행할 함수
- list: 처리할 항목들의 목록
- index: 목록 내 현재 항목에 대한 인수 이름

[AVAILABLE FUNCTIONS]
GetJokeTopics
설명: 농담 주제 목록([str])을 가져온다.

EmailTo
설명: 입력 텍스트를 수신자에게 이메일로 보낸다.
args:
- text: 이메일로 보낼 텍스트
- recipient: 수신자의 이메일 주소 (여러 주소를 ';'으로 구분하여 포함할 수 있음)

Summarize
설명: 입력 텍스트를 요약한다.
args:
- text: 요약할 텍스트

Joke
설명: 재미있는 농담을 만든다.
args:
- topic: 농담을 생성할 주제
- topic: the topic to generate a joke about

[GOAL]
"농담 주제 목록을 얻고 각 주제에 대해 농담을 생성한다. 농담들을 친구에게 이메일로 보낸다."

[OUTPUT]
    {
        "subtasks": [
            {"function": "GetJokeTopics"},
            {"function": "for-each",
             "args": {
                       "list": "output_GetJokeTopics",
                       "index": "topic",
                       "function":
                                  {
                                   "function": "Joke",
                                   "args": {"topic": "topic"}}}},
            {
             "function": "EmailTo",
              "args": {
                        "text": "for-each_output_GetJokeTopics"
                        "recipient": "friend"}}
        ]
    }

... 예시들이 더 있지만 생략했음 ... #2

[SPECIAL FUNCTIONS]     #3
for-each
— 설명: 목록의 각 항목에 대해 함수를 실행한다.
args:
- function: 실행할 함수
- iterator: 처리할 항목들의 목록
- index: 목록 내 현재 항목에 대한 인수 이름

[AVAILABLE FUNCTIONS]     #4
{{$available_functions}}

[GOAL]
{{$goal}}     #5

반드시 가용 함수 섹션([AVAILABLE FUNCTIONS])에 있는 함수만 사용하세요.
계획은 가능한 한 짧아야 합니다.
그리고 계획은 JSON 형식으로만 반환하세요.
[OUTPUT]     #6
"""

#1 에이전트에게 예시들의 처리 방법을 알려주는 머리말 지침
#2 세 개의 예시(퓨샷) 중 첫 번째
#3 특수 함수 섹션에 반복 함수 for-each를 추가한다.
#4 가용 함수 섹션은 에이전트의 가용 함수 목록에서 자동으로 채워진다.
#5 목표가 여기에 대입된다.
#6 에이전트의 출력이 여기에 들어갈 것이다.

### 예제 11.4

def create_plan(self, nexus, agent, goal: str, prompt: str = PROMPT) -> Plan:
        selected_actions = nexus.get_actions(agent.actions)
        available_functions_string = "\n\n".join(
            format_action(action) for action in selected_actions
        )     #1

        context = {}     #2
        context["goal"] = goal
        context["available_functions"] = available_functions_string

        ptm = PromptTemplateManager()     #3
        prompt = ptm.render_prompt(prompt, context)

        plan_text = nexus.execute_prompt(agent, prompt)     #4
        return Plan(prompt=prompt,
                    goal=goal,
                    plan_text=plan_text)     #5

#1 에이전트의 가용 활동들을 불러오고 결과 문자열을 플래너(planner)용으로 포매팅한다.
#2 컨텍스트는 이후 플래너 프롬프트 템플릿에 대입된다.
#3 간단한, 하지만 Jinja2, Handlebars, Mustache과 비슷한 개념의 템플릿 관리자
#4 채워진 플래너 프롬프트를 LLM으로 전송한다.
#5 결과(수립된 계획)를 Plan 클래스로 감싸서 반환한다. 이후 실행기가 이 Plan 객체를 실행한다.


### 예제 11.5

def execute_plan(self, nexus, agent, plan: Plan) -> str:
        context = {}
        plan = plan.generated_plan
        for task in plan["subtasks"]:     #1
            if task["function"] == "for-each":     #2
                list_name = task["args"]["list"]
                index_name = task["args"]["index"]
                inner_task = task["args"]["function"]

                list_value = context.get(list_name, [])
                for item in list_value:
                    context[index_name] = item
                    result = nexus.execute_task(agent, inner_task, context)
                    context[f"for-each_{list_name}_{item}"] = result

                for_each_output = [
                    context[f"for-each_{list_name}_{item}"] ↪
                      for item in list_value
                ]
                context[f"for-each_{list_name}"] = for_each_output

                for item in list_value:     #3
                    del context[f"for-each_{list_name}_{item}"]

            else:
                result = nexus.execute_task(agent,
                                            task,
                                            context)     #4
                context[f"output_{task['function']}"] = result

        return context     #5

#1 계획의 각 하위 작업(subtask)을 순회한다.
#2 반복 처리해야 하는 함수를 처리하고 전체 결과 목록을 컨텍스트에 추가한다.
#3 개별 for-each 컨텍스트 항목을 제거한다.
#4 일반적인 작업 실행
#5 각 함수 호출 결과를 포함한 전체 컨텍스트를 반환한다.