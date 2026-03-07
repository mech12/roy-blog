import os
import json
from prompt_utils import prompt_llm

"""
프롬프트 템플릿(Prompt Template)과 LLM 모델 객체를 결합하여, 
입력을 넣으면 바로 결과가 나오도록 최적화된 함수
"""

#디렉토리에 있는 .jsonl 확장자를 갖는 파일을 모두 불러온다 
def list_text_files_in_directory(directory):
    text_files = []
    for filename in os.listdir(directory):
        if filename.startswith('_'):
            continue
        if filename.endswith(".jsonl"):
            text_files.append(filename)  #파일들의 내용을 모두 덧붙인다 
    return text_files

       
def load_and_parse_json_file(file_path):
    data = []
    with open(file_path, 'r', encoding='utf-8') as file:
        json_text = ""
        for line in file:
            line = line.strip()
            json_text += line
            if line == "]":
                try:
                    json_data = json.loads(json_text)
                    data.append(json_data)
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON: {json_text}")
                    print(e)
                json_text = ""    
    return data


def main():
    directory = "prompts"  #prompt 폴더에서 파일을 모두 불러온다 
    text_files = list_text_files_in_directory(directory)

    if not text_files:
        print("No text files found in the directory.")
        return
    
    def print_available():
        print("Available prompt tactics:")
        for i, filename in enumerate(text_files, start=1):
            print(f"{i}. {filename}")

    while True:
        try:
            print_available()
            choice = int(input("실행할 프롬프트 전략의 번호를 입력하세요 (종료하려면 0 입력): "))
            if choice == 0:
                break
            elif 1 <= choice <= len(text_files):
                selected_file = text_files[choice - 1]
                file_path = os.path.join(directory, selected_file)
                prompts = load_and_parse_json_file(file_path)
                print(f"Running prompts for {selected_file}")                
                for i, prompt in enumerate(prompts):
                    print(f"PROMPT {i+1} -------------------------------------------------")
                    print(prompt)
                    print(f"REPLY -------------------------------------------------")
                    #using OpenAI
                    print(prompt_llm(prompt))
                    #using local LLM
                    # print(prompt_llm(prompt, 
                    #                  model="local-model", 
                    #                  base_url="http://localhost:1234/v1",
                    #                  api_key="not used"))
            else:
                print("Invalid choice. Please enter a valid number.")
        except ValueError:
            print("Invalid input. Please enter a number.")

if __name__ == "__main__":
    main()
