import os
from openai import OpenAI
from dotenv import load_dotenv


load_dotenv()


def prompt_llm(messages,
               model=None,
               base_url=None,
               api_key=None):
    client = OpenAI(
        base_url=base_url or os.getenv('MSA_LLM_API_BASE', 'http://10.10.20.92:8009/v1'),
        api_key=api_key or os.environ['MSA_LLM_API_KEY'],
    )

    response = client.chat.completions.create(
        model=model or os.getenv('MSA_LLM_MODEL', '/models/gpt-oss-120b'),
        messages=messages,
        temperature=0.7,                
        )       
    
    return response.choices[0].message.content