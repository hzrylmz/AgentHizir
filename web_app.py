from flask import Flask, render_template, request, jsonify, g, Response
from sqlite_memory import SQLiteMemory
import requests
import json

app = Flask(__name__)

BOT_NAME = "Agent Dusty"  # Bot adını buradan kolayca değiştir

def get_memory():
    if 'memory' not in g:
        g.memory = SQLiteMemory()
    return g.memory

@app.teardown_appcontext
def close_memory(exception=None):
    memory = g.pop('memory', None)
    if memory is not None:
        memory.close()

@app.route("/", methods=["GET"])
def index():
    conversation = get_memory().get_conversation()
    conversation = [
        dict(msg) if not isinstance(msg, dict) else msg
        for msg in conversation
    ]
    return render_template("index.html", conversation=conversation, bot_name=BOT_NAME)

def ollama_stream(prompt):
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": "mistral",   
        "prompt": prompt,
        "stream": True
    }
    with requests.post(url, json=payload, stream=True) as r:
        for line in r.iter_lines():
            if line:
                data = json.loads(line)
                if "response" in data:
                    yield data["response"]

@app.route("/stream", methods=["POST"])
def stream_response():
    user_message = request.form["message"]
    
    mem = get_memory()
    mem.add_message("user", user_message)
    
    prompt = ""
    for msg in mem.get_conversation(last_n=10):
        role = "User" if msg['role'] == "user" else BOT_NAME
        prompt += f"{role}: {msg['content']}\n"
    prompt += f"{BOT_NAME}:"

    def generate_and_save():
        full_response = ""
        for chunk in ollama_stream(prompt):
            full_response += chunk
            yield chunk
        if full_response.strip():
            temp_mem = SQLiteMemory()
            temp_mem.add_message("ai", full_response.strip())
            temp_mem.close()

    return Response(generate_and_save(), mimetype='text/plain')

@app.route("/reset", methods=["POST"])
def reset():
    mem = get_memory()
    mem.clear()
    return jsonify({"success": True})

@app.route("/delete_message", methods=["POST"])
def delete_message():
    msg_id = request.json.get("id")
    mem = get_memory()
    mem.delete_message(msg_id)
    return jsonify({"success": True})

@app.route("/export", methods=["GET"])
def export():
    mem = get_memory()
    conversation = mem.get_conversation()
    export_lines = []
    for msg in conversation:
        role = "👤 You:" if msg['role'] == "user" else f"🤖 {BOT_NAME}:"
        export_lines.append(f"{role} {msg['content']}")
        export_lines.append(f"{msg['timestamp']}")
        export_lines.append("")  
    export_data = "\n".join(export_lines)
    return Response(
        export_data,
        mimetype="text/plain",
        headers={"Content-Disposition": "attachment;filename=chat.txt"}
    )

if __name__ == "__main__":
    app.run(debug=True)
