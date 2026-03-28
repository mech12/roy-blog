from textwrap import dedent

import agentops
from crewai import Agent, Crew, Process, Task
from dotenv import load_dotenv

load_dotenv()

agentops.init()

print("## Welcome to the Game Crew")
print("-------------------------------")
game = input("What is the game you would like to build? What will be the mechanics?\n")


senior_engineer_agent = Agent(
    role="시니어 소프트웨어 엔지니어",
    goal="필요에 따라 소프트웨어를 만드세요",
    backstory=dedent(
        """
        당신은 선도적인 기술 싱크탱크의 시니어 소프트웨어 엔지니어입니다.
        Python 프로그래밍에 전문성을 가지고 있으며, 완벽한 코드를
        작성하기 위해 최선을 다합니다.
        """
    ),
    allow_delegation=False,
    verbose=True,
)

qa_engineer_agent = Agent(
    role="소프트웨어 품질 관리 엔지니어",
    goal="주어진 코드의 오류를 분석하여 완벽한 코드를 만드세요",
    backstory=dedent(
        """
        당신은 코드의 오류를 검사하는 데 특화된 소프트웨어 엔지니어입니다.
        세부 사항에 대한 안목이 있고 숨겨진 버그를 찾아내는 재주가 있습니다.
        누락된 임포트, 변수 선언, 불일치하는 괄호, 구문 오류를 검사합니다.
        또한 보안 취약점과 로직 오류도 검사합니다.
        """
    ),
    allow_delegation=False,
    verbose=True,
)

chief_qa_engineer_agent = Agent(
    role="수석 소프트웨어 품질 관리 엔지니어",
    goal="코드가 의도한 대로 작동하는지 확인하세요",
    backstory=dedent(
        """
        당신은 선도적인 기술 싱크탱크의 수석 소프트웨어 품질 관리 엔지니어입니다.
        작성된 코드가 의도한 대로 작동하는지 확인하는 책임을 맡고 있습니다.
        코드의 오류를 검사하고 최고 품질을 보장하는 것이 당신의 역할입니다.
        """
    ),
    allow_delegation=True,
    verbose=True,
)

code_task = Task(
    description=f"""Python을 사용하여 게임을 만들 것입니다. 다음은 지시사항입니다:
        지시사항
        ------------
        {game}
        Python을 사용하여 게임 코드를 작성하세요.""",
    expected_output="최종 답변은 전체 Python 코드여야 하며, Python 코드만 포함하고 다른 것은 포함하지 마세요.",
    agent=senior_engineer_agent,
)

qa_task = Task(
    description=f"""Python을 사용하여 게임을 만드는 것을 돕고 있습니다. 다음은 지시사항입니다:
        지시사항
        ------------
        {game}
        받은 코드를 사용하여 오류를 검사하세요. 로직 오류,
        구문 오류, 누락된 임포트, 변수 선언, 불일치하는 괄호,
        보안 취약점을 검사하세요.""",
    expected_output="코드에서 발견한 문제점 목록을 출력하세요.",
    agent=qa_engineer_agent,
)

evaluate_task = Task(
    description=f"""Python을 사용하여 게임을 만드는 것을 돕고 있습니다. 다음은 지시사항입니다:
        지시사항
        ------------
        {game}
        코드가 완전하고 의도한 대로 작동하는지 코드를 검토하세요.""",
    expected_output="최종 답변은 수정된 전체 Python 코드여야 하며, Python 코드만 포함하고 다른 것은 포함하지 마세요.",
    agent=chief_qa_engineer_agent,
)

# Instantiate your crew with a sequential process
crew = Crew(
    agents=[senior_engineer_agent, qa_engineer_agent, chief_qa_engineer_agent],
    tasks=[code_task, qa_task, evaluate_task],
    verbose=True,
    process=Process.sequential,
)

# Get your crew to work!
result = crew.kickoff()

print("######################")
print(result)
