#http://www.occamsrazr.net/book/AiAgentsInAction

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(
    base_url=os.getenv('MSA_LLM_API_BASE', 'http://10.10.20.92:8009/v1'),
    api_key=os.environ['MSA_LLM_API_KEY'],
)

completion = client.chat.completions.create(
  model=os.getenv('MSA_LLM_MODEL', '/models/gpt-oss-120b'),
  messages=[
    {"role": "system", "content": "운을 맞추어서 대답해줘"},
    {"role": "user", "content": "네 소개를 해줄래?"}
  ],
  temperature=0.7,
)

print(completion.choices[0].message)