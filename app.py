import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
app = Flask(__name__)

# Inicializar cliente OpenAI con clave
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route("/webhook", methods=["POST"])
def webhook():
    incoming_msg = request.values.get("Body", "").strip()
    if not incoming_msg:
        return jsonify({"mensaje": "No se recibió ningún mensaje"}), 400

    try:
        # Llamada al modelo GPT-4
        response = client.chat.completions.create(
            model="gpt-4-1106-preview",  # o usa "gpt-3.5-turbo", "gpt-4.1-mini", etc.
            messages=[
                {"role": "system", "content": "Eres un asistente útil que responde con jerga semiformal colombiana."},
                {"role": "user", "content": incoming_msg}
            ]
        )
        reply = response.choices[0].message.content.strip()
        return jsonify({"mensaje": reply}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(deb
