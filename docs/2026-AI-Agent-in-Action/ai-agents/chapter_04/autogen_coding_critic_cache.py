from autogen import AssistantAgent, UserProxyAgent, config_list_from_json
from autogen.cache import Cache

# Load the configuration list from the config file.
config_list = config_list_from_json(env_or_file="OAI_CONFIG_LIST")

# Create the agent that represents the user in the conversation.
user_proxy = UserProxyAgent(
    "user",
    code_execution_config={
        "work_dir": "working",
        "use_docker": False,
        "last_n_messages": 1,
    },
    human_input_mode="ALWAYS",
    is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
)

engineer = AssistantAgent(
    name="Engineer",
    llm_config={"config_list": config_list},
    system_message="""
    당신은 소프트웨어 개발 전문성으로 유명한 전문 Python 엔지니어입니다.
    당신은 기능적이고 효율적인 소프트웨어 애플리케이션, 도구, 게임을 만드는 데 자신의 기술을 활용합니다.
    당신은 읽기 쉽고 유지보수하기 좋은 깔끔하고 잘 구조화된 코드를 작성하는 것을 선호합니다.
    """,
)

critic = AssistantAgent(
    name="Reviewer",
    llm_config={"config_list": config_list},
    system_message="""
    당신은 꼼꼼함과 표준 준수로 유명한 코드 리뷰어입니다.
    당신의 임무는 코드 내용에서 유해하거나 기준 미달인 요소를 면밀히 검토하는 것입니다.
    당신은 코드가 안전하고 효율적이며 모범 사례를 준수하는지 확인합니다.
    코드에서 문제점이나 개선이 필요한 부분을 식별하여 목록으로 출력합니다.
    """,
)


def review_code(recipient, messages, sender, config):
    return f"""
            다음 코드를 리뷰하고 비평해 주세요.

            {recipient.chat_messages_for_summary(sender)[-1]['content']}
            """


user_proxy.register_nested_chats(
    [
        {
            "recipient": critic,
            "message": review_code,
            "summary_method": "last_msg",
            "max_turns": 3,
        }
    ],
    trigger=engineer,  # condition=my_condition,
)

task = """Pygame을 사용하여 스네이크 게임을 만들어 주세요."""

with Cache.disk(cache_seed=42) as cache:
    res = user_proxy.initiate_chat(
        recipient=engineer,
        message=task,
        max_turns=2,
        summary_method="last_msg",
        cache=cache,
    )
