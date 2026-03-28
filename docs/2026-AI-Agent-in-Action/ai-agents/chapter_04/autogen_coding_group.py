from autogen import (
    AssistantAgent,
    GroupChat,
    GroupChatManager,
    UserProxyAgent,
    config_list_from_json,
)
from autogen.cache import Cache

# Load the configuration list from the config file.
config_list = config_list_from_json(env_or_file="OAI_CONFIG_LIST")

# Create the agent that represents the user in the conversation.
user_proxy = UserProxyAgent(
    "user",
    code_execution_config={
        "work_dir": "working",
        "use_docker": False,
        "last_n_messages": 3,
    },
    human_input_mode="NEVER",
)

llm_config = {"config_list": config_list}

engineer = AssistantAgent(
    name="Engineer",
    llm_config=llm_config,
    system_message="""
    당신은 소프트웨어 개발 전문성으로 유명한 전문 Python 엔지니어입니다.
    당신은 기능적이고 효율적인 소프트웨어 애플리케이션, 도구, 게임을 만드는 데 자신의 기술을 활용합니다.
    당신은 읽기 쉽고 유지보수하기 좋은 깔끔하고 잘 구조화된 코드를 작성하는 것을 선호합니다.
    """,
)

critic = AssistantAgent(
    name="Critic",
    llm_config=llm_config,
    system_message="""
    비평가. 당신은 게임 엔지니어이자 주어진 게임 코드의 품질을 1점(나쁨) - 10점(좋음)으로 평가하며 명확한 근거를 제시하는 전문가입니다. 각 평가에서 반드시 게임 개발 모범 사례를 고려해야 합니다. 구체적으로, 다음 차원에서 코드를 신중하게 평가할 수 있습니다:
    - 버그 (bugs): 버그, 로직 오류, 구문 오류 또는 오타가 있는가? 코드가 컴파일에 실패할 수 있는 이유가 있는가? 어떻게 수정해야 하는가? 버그가 하나라도 있으면 버그 점수는 반드시 5점 미만이어야 합니다.
    - 게임 플레이: 게임 플레이가 얼마나 잘 되는가? 몰입감 있고, 재미있고, 도전적인가? 개선할 수 있는 게임 플레이 요소가 있는가?
    - 목표 준수 (compliance): 코드가 지정된 게임 목표를 얼마나 잘 충족하는가?
    - 미학 (aesthetics): 게임의 미학이 테마 유형과 데이터에 적합한가?

    위의 각 차원에 대해 반드시 점수를 제공해야 합니다.
    {bugs: 0, transformation: 0, compliance: 0, type: 0, encoding: 0, aesthetics: 0}
    코드를 제안하지 마세요.
    마지막으로, 위의 비평을 바탕으로 코더가 코드를 개선하기 위해 취해야 할 구체적인 조치 목록을 제안하세요.
    """,
)

groupchat = GroupChat(agents=[user_proxy, engineer, critic], messages=[], max_round=20)
manager = GroupChatManager(groupchat=groupchat, llm_config=llm_config)

task = """Pygame을 사용하여 스네이크 게임을 만들어 주세요."""

with Cache.disk(cache_seed=43) as cache:
    res = user_proxy.initiate_chat(
        recipient=manager,
        message=task,
        cache=cache,
    )
