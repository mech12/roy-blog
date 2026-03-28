import agentops
from crewai import Agent, Crew, Process, Task
from dotenv import load_dotenv

load_dotenv()
agentops.init()

# Creating a senior researcher agent with memory and verbose mode
joke_researcher = Agent(
    role="시니어 유머 연구원",
    goal="다음 {topic}에 대해 무엇이 재미있는지 연구하세요",
    verbose=True,
    memory=True,
    backstory=(
        "슬랩스틱 유머에 이끌려, 당신은 사람들을 웃기는 것이 무엇인지 아는 숙련된 유머 연구원입니다. "
        "당신은 일상적인 상황에서 재미를 찾아내는 재주가 있으며, "
        "지루한 순간도 웃음의 도가니로 만들 수 있습니다."
    ),
    allow_delegation=True,
)

# Creating a writer agent with custom tools and delegation capability
joke_writer = Agent(
    role="유머 작가",
    goal="다음 {topic}에 대해 유머러스하고 재미있는 농담을 작성하세요",
    verbose=True,
    memory=True,
    backstory=(
        "당신은 유머 감각이 뛰어난 농담 작가입니다. "
        "단순한 아이디어도 웃음의 도가니로 만들 수 있습니다. "
        "당신은 말재주가 있어 몇 줄만으로도 사람들을 웃길 수 있습니다."
    ),
    allow_delegation=False,
)

# Research task
research_task = Task(
    description=(
        "다음 주제:{topic}가 왜 재미있는지 파악하세요. "
        "유머를 만드는 핵심 요소를 반드시 포함하세요. "
        "또한 현재 사회 트렌드에 대한 분석과 "
        "그것이 유머 인식에 미치는 영향을 제공하세요."
    ),
    expected_output="최신 유머에 대한 포괄적인 3문단 분량의 보고서.",
    agent=joke_researcher,
)

# Writing task with language model configuration
write_task = Task(
    description=(
        "{topic}에 대해 통찰력 있고, 유머러스하며, 사회적으로 인식 있는 농담을 작성하세요. "
        "재미있게 만드는 핵심 요소와 "
        "현재 사회 트렌드와의 관련성을 반드시 포함하세요."
    ),
    expected_output="{topic}에 대한 간결하고 짧은 한 줄 농담.",
    agent=joke_writer,
    async_execution=False,
    output_file="the_best_joke.md",  # Example of output customization
)

# Forming the tech-focused crew with some enhanced configurations
crew = Crew(
    agents=[joke_researcher, joke_writer],
    tasks=[research_task, write_task],
    process=Process.sequential,  # Optional: Sequential task execution is default
    memory=True,
    cache=True,
    max_rpm=100,
    share_crew=True,
)

result = crew.kickoff(inputs={"topic": "AI 엔지니어 농담"})
print(result)
