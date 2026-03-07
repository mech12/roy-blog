#http://www.occamsrazr.net/book/AiAgentsInAction

from openai import OpenAI

# Point to the local server
client = OpenAI(base_url="http://localhost:1234/v1", api_key="not-needed")

completion = client.chat.completions.create(
  model="local-model", # this field is currently unused
  messages=[
    {"role": "system", "content": "운을 맞추어서 대답해줘"},
    {"role": "user", "content": "네 소개를 해줄래?"}
  ],
  temperature=0.7,
)

print(completion.choices[0].message)