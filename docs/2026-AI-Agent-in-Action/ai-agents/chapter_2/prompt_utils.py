import os
from openai import OpenAI
from dotenv import load_dotenv


load_dotenv()  # loading and setting the api key can be done in one step


# Example function to query ChatGPT
def prompt_llm(messages,
               model=None,
               base_url=None,
               api_key=None):
    base_url = base_url or os.getenv("MSA_LLM_API_BASE")
    model = model or os.getenv("MSA_LLM_MODEL", "gpt-4.1")
    api_key = api_key or os.getenv("MSA_LLM_API_KEY", "")

    if base_url:
        client = OpenAI(base_url=base_url, api_key=api_key)
    else:
        client = OpenAI()

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.7,
        )

    return response.choices[0].message.content