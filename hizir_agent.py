import requests
from sqlite_memory import SQLiteMemory
import re

memory = SQLiteMemory()

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
    
    return re.sub(r"^(AI:|User:)\s*", "", text.strip(), flags=re.IGNORECASE)

def chat_with_memory(user_input):
    memory.add_message("user", user_input)

    conversation = memory.get_conversation()

    
    prompt = ""
    for msg in conversation:
        role = "User" if msg['role'] == "user" else "AI"
        prompt += f"{role}: {msg['content']}\n"
    prompt += "AI:"

    ai_response = query_ollama(prompt)
    ai_response = clean_ai_response(ai_response)

    memory.add_message("ai", ai_response)

    return ai_response


print("HızırAgent + Mistral aktif. Çıkmak için 'exit' yaz.")
while True:
    user_input = input("👤 Sen: ")
    if user_input.strip().lower() == 'exit':
        print("Hafıza kaydedildi, çıkılıyor...")
        break
    response = chat_with_memory(user_input)
    print(f"🤖 HızırAgent: {response}")
