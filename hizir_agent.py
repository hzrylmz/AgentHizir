import requests
from sqlite_memory import SQLiteMemory
import re

memory = SQLiteMemory()
BOT_NAME = "Agent Dusty"

def query_ollama(prompt):
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "mistral",
            "prompt": prompt,
            "stream": False
        }
    )
    return response.json()["response"]

def clean_ai_response(text):
    return re.sub(r"^(%s:|User:)\s*" % BOT_NAME, "", text.strip(), flags=re.IGNORECASE)

def chat_with_memory(user_input):
    memory.add_message("user", user_input)

    conversation = memory.get_conversation()
    prompt = ""
    for msg in conversation:
        role = "User" if msg['role'] == "user" else BOT_NAME
        prompt += f"{role}: {msg['content']}\n"
    prompt += f"{BOT_NAME}:"

    ai_response = query_ollama(prompt)
    ai_response = clean_ai_response(ai_response)

    memory.add_message("ai", ai_response)

    return ai_response

print(f"{BOT_NAME} + Mistral is active. Type 'exit' to quit.")
while True:
    user_input = input("👤 You: ")
    if user_input.strip().lower() == 'exit':
        print("Memory saved, exiting...")
        break
    response = chat_with_memory(user_input)
    print(f"🤖 {BOT_NAME}: {response}")
